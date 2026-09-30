"""Conservative request metadata summaries; never execute logged tool code."""
import ast
from collections import Counter
import json
import re
from urllib.parse import urlsplit


NOTE = ('Observed tool-request messages in the reporting interval, not bytes, email/message '
        'counts inside results, or confirmed transfers. One message counts once per group '
        'and direction; groups can overlap. Static wrapper inspection is partial; dynamic '
        'targets, browser interaction, arbitrary shell/script traffic and unrecognized tools '
        'are not attributed. Literal calls inside wrappers are inferred and may not have '
        'executed. Website destinations require explicit HTTP POST and outbound-payload '
        'evidence; GET/web-open requests appear only as sources. The current adapters do '
        'not establish website POST payloads. Posted labels describe outbound operations, '
        'not confirmed delivery. Search-provider hostnames are not exposed in these request records; '
        'result sites and domain filters are not treated as query destinations. '
        'Local directories and Codex app activity are excluded from this readout. '
        'External means outside the local Codex environment, not necessarily outside your '
        'organization. No account-wide ChatGPT coverage.')


def directory(path):
    value = str(path or '').replace('\\', '/').rstrip('/')
    return 'Local project directory: ' + (value.split('/')[-1] or 'Unknown')


def classify(name, args, cwd):
    """Return coarse requested sources/destinations, with no body/recipient retention."""
    result = set()
    name = name.lower()
    service = next((label for key, label in (
        ('outlook_email', 'Outlook Email'), ('outlook_calendar', 'Outlook Calendar'),
        ('slack', 'Slack'), ('codex_app', 'Codex app'), ('chatgpt_space', 'ChatGPT Pages'),
        ('sharepoint', 'SharePoint')) if key in name), None)
    operation = name.split('__')[-1]
    if service:
        if re.search(r'(?:^|_)(search|read|fetch|list|get)(?:_|$)', operation):
            result.add(('sources', service))
        elif re.search(r'(?:^|_)(send|create|update|edit|add|upload|complete_file_upload|attach|set|delete)(?:_|$)', operation):
            result.add(('destinations', service))
        return result
    if name.endswith('exec_command'):
        cmd = args.get('cmd', '')
        # Do not assign explicit path targets or network/script commands to the cwd.
        # Such commands need a richer adapter; guessing would mislabel their traffic.
        if not isinstance(cmd, str) or re.search(r'https?://|[A-Za-z]:[\\/]|(?:^|[\s\"\'])/|\.\.[\\/]|\$env:|\$HOME|python|curl|Invoke-WebRequest', cmd, re.I):
            return result
        group = directory(args.get('workdir') or cwd)
        if re.search(r'\b(Get-Content|rg|cat|head|tail|Get-ChildItem)\b', cmd, re.I):
            result.add(('sources', group))
        if re.search(r'\b(Set-Content|Add-Content|Out-File)\b', cmd, re.I):
            result.add(('destinations', group))
    elif name.endswith('web__run'):
        for entry in args.get('open', []):
            if isinstance(entry, dict):
                url = urlsplit(str(entry.get('ref_id', '')))
                host = url.hostname
                if host and url.scheme in ('https', 'http'):
                    result.add(('sources', 'Website: ' + host.lower()))
        if args.get('search_query') or args.get('image_query'):
            result.add(('sources', 'Web search (result sites not attributed)'))
            result.add(('destinations', 'Web search service (queries)'))
    elif name.endswith('apply_patch'):
        patch = args.get('patch', '')
        paths = re.findall(r'^\*\*\* (?:Add|Update|Delete) File: (.+)$', patch, re.M)
        if paths and all(not re.match(r'(?:[A-Za-z]:|/|\.\.)', p) for p in paths):
            result.add(('destinations', directory(cwd)))
    return result


def external_readout(activity):
    """Filter presentation, including older snapshots, without relabeling unknown sites."""
    result = dict(activity)
    for direction in ('sources', 'destinations'):
        result[direction] = [row for row in activity.get(direction, [])
                             if row['group'] != 'Codex app'
                             and not row['group'].startswith('Local project directory:')
                             and row['group'] not in ('Web search (result sites not attributed)',
                                                      'Web search service (queries)')
                             and not (direction == 'destinations'
                                      and row['group'].startswith('Website:'))]
    result['unattributed_search_messages'] = sum(row['messages'] for row in activity.get('destinations', [])
                                               if row['group'] == 'Web search service (queries)')
    result['measurement_note'] = NOTE
    return result


def literal_arguments(text):
    """Decode JSON or the literal subset of JS objects, never eval logged code."""
    tokens = re.findall(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|[A-Za-z_$][\w$]*|[^\s]', text)
    normalized = []
    for i, token in enumerate(tokens):
        if token.startswith("'"):
            token = json.dumps(ast.literal_eval(token))
        elif re.fullmatch(r'[A-Za-z_$][\w$]*', token) and i+1 < len(tokens) and tokens[i+1] == ':':
            token = json.dumps(token)
        normalized.append(token)
    return json.JSONDecoder().raw_decode(''.join(normalized))[0]


def summarize_request(payload, cwd):
    name = payload.get('name', '')
    args = payload.get('arguments', {})
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            args = {}
    if not isinstance(args, dict):
        args = {}
    if name not in ('exec', 'functions.exec'):
        if name.endswith('apply_patch'):
            args = {'patch': payload.get('input', '')}
        return classify(name, args, cwd)
    code = payload.get('input', '')
    if not isinstance(code, str):
        return set()
    result = set()
    # Only literal tools.NAME({...}) invocations. Dynamic expressions are omitted.
    for match in re.finditer(r'\btools\.([A-Za-z0-9_]+)\s*\(\s*', code):
        tail = code[match.end():]
        try:
            values = literal_arguments(tail)
        except (ValueError, SyntaxError):
            values = {}
            # Common JS object-literal calls: decode literal cmd/workdir only.
            for field in ('cmd', 'workdir'):
                found = re.match(r'\{\s*'+field+r'\s*:\s*("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')', tail)
                if found:
                    try:
                        values[field] = ast.literal_eval(found[1])
                    except (SyntaxError, ValueError):
                        pass
        result.update(classify(match[1], values if isinstance(values, dict) else {'patch': values} if isinstance(values, str) else {}, cwd))
    return result


def aggregate_requests(records, conflicts):
    counts = {'sources': Counter(), 'destinations': Counter()}
    unclassified = 0
    for key, groups in records.items():
        if key in conflicts:
            continue
        if not groups:
            unclassified += 1
        for direction, label in groups:
            counts[direction][label] += 1
    return {**{direction: [{'group': label, 'messages': count} for label, count in
                           sorted(values.items(), key=lambda item: (-item[1], item[0]))]
               for direction, values in counts.items()},
            'observed_request_messages': len(records.keys() - conflicts),
            'unclassified_request_messages': unclassified,
            'conflicting_request_ids_excluded': len(conflicts), 'measurement_note': NOTE}
