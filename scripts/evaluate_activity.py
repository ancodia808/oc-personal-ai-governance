"""Conservative advisory engine for a verified execution-state adapter.

This module does not treat local task-start/token events as execution heartbeats.
No sending or scheduling occurs here.
"""
from datetime import datetime, timedelta, time
try:
    from .eastern_time import eastern as ZoneInfo
except ImportError:
    from eastern_time import eastern as ZoneInfo
try:
    from .collect_usage import timestamp
except ImportError:
    from collect_usage import timestamp


def normalize_thread(snapshot, observed_at):
    """Adapt read_thread structured data; caller supplies actual retrieval time.

    Retain no messages, tool arguments, or prompt content. 'active' +
    'inProgress' is labeled as a Working proxy, not a literal UI label.
    """
    observed = timestamp(observed_at)
    thread = snapshot['thread']
    status = thread.get('status', {})
    if isinstance(status, str):
        status = {'type':status}
    turns = [t for t in snapshot.get('turns',[]) if t.get('status')=='inProgress']
    turn = turns[0] if len(turns)==1 else {}
    flags = status.get('activeFlags',[])
    state = 'working' if status.get('type')=='active' and turn and not flags else 'unknown'
    if status.get('type')=='idle':state='idle'
    # Monitoring reads one latest turn. Do not infer completion from an older
    # turn in a multi-turn response or from missing/contradictory evidence.
    latest = snapshot.get('turns', [])
    if (status.get('type')=='notLoaded' and not flags and len(latest)==1
            and latest[0].get('status')=='completed'):
        state='offloaded'
    started = turn.get('startedAt')
    elapsed = None
    if isinstance(started,(int,float)) and not isinstance(started,bool):
        from datetime import timezone as utc_timezone
        start = datetime.fromtimestamp(started,utc_timezone.utc)
        if start<=observed:elapsed=(observed-start).total_seconds()
        else:state='unknown'
    return {'thread_id':thread['id'],'host_id':thread.get('hostId','local'),
            'turn_id':turn.get('id'), 'title':thread.get('title','Untitled chat'),
            'state':state,'status_as_of':observed.isoformat(),
            'reported_duration_seconds':elapsed,'duration_basis':'elapsed_turn',
            'source':'codex_read_thread_active_inProgress_proxy',
            'coverage_note':'A notLoaded chat with one completed latest turn is offloaded; ambiguous evidence remains unknown. Only one current in-progress turn is accepted.'}


def evaluate_proxy(run, cutoff, delivered=(), timezone='America/New_York',
                   threshold_seconds=7200, freshness_seconds=300):
    """Current Thinking/Working proxy policy. No continuous-work assertion."""
    now=timestamp(cutoff)
    observed=timestamp(run['status_as_of'])
    if threshold_seconds<=0 or freshness_seconds<=0 or observed>now:
        raise ValueError('Invalid threshold or observation time')
    state=run.get('state','unknown').lower()
    duration=run.get('reported_duration_seconds')
    if duration is not None and (type(duration) not in (int,float) or not __import__('math').isfinite(duration) or duration<0):
        raise ValueError('Invalid reported duration')
    result={'policy':'thinking_working_proxy_v1','status':state,'advisories':[],
            'reported_duration_seconds':duration,'duration_basis':run.get('duration_basis','unknown'),
            'confirmed_active_seconds':None}
    if (now-observed).total_seconds()>freshness_seconds:
        result['status']='stale'
        return result
    if state not in ('thinking','working'):return result
    if not all(isinstance(run.get(k),str) and run[k] for k in ('host_id','thread_id','turn_id')):
        result['status']='unknown'
        return result
    import json
    identity=[run[k] for k in ('host_id','thread_id','turn_id')]
    triggers=[]
    if duration is not None and run.get('duration_basis') in ('elapsed_turn','reported_state') and duration>=threshold_seconds:
        triggers.append(('two_hour','two_hour'))
    local=now.astimezone(ZoneInfo(timezone))
    # Friday checks from 18:00 through midnight. No inference about earlier
    # state, no need for a processing interval crossing the boundary.
    if local.weekday()==4 and local.time()>=time(18):
        triggers.append(('friday_evening','friday_evening:'+local.date().isoformat()))
    for trigger,suffix in triggers:
        key=json.dumps(identity+[suffix],separators=(',',':'))
        if key not in delivered:
            result['advisories'].append({'trigger':trigger,'severity':'red','deduplication_key':key,
                'message':f'This chat appears to still be {state}. Review progress before leaving it unattended.',
                'duration_seconds':duration,'duration_basis':run.get('duration_basis','unknown'),
                'status_as_of':observed.isoformat(),'verified_processing':False})
    return result


def union_seconds(intervals):
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return sum((end-start).total_seconds() for start,end in merged)


def evaluate(run, cutoff, delivered=(), timezone='America/New_York',
             threshold_seconds=7200, freshness_seconds=300):
    """Intervals must be adapter-certified processing, excluding all waits.

    Current state is independent from historical accumulated processing.
    A trusted adapter must supply status_as_of, run_started_at and intervals.
    Freshness is intentionally shorter than the 30-minute polling interval:
    each poll must retrieve fresh state, not reuse the previous poll's result.
    """
    now = timestamp(cutoff)
    if threshold_seconds <= 0 or freshness_seconds <= 0:
        raise ValueError('Positive thresholds required')
    result = {'status':'unknown','confirmed_active_seconds':None,'advisories':[],
              'reason':'Verified execution-state coverage is unavailable'}
    if run.get('evidence') != 'verified_execution_intervals_v1':
        return result
    for key in ('account_id','thread_id','turn_id'):
        if not isinstance(run.get(key),str) or not run[key]:
            raise ValueError('Stable run identity required')
    started = timestamp(run['run_started_at'])
    observed = timestamp(run['status_as_of'])
    state = run['state']
    if state not in ('processing','waiting','completed','interrupted','failed','unknown'):
        raise ValueError('Invalid state')
    if not started <= observed <= now:
        raise ValueError('Invalid observation time')
    intervals=[]
    for interval in run['processing_intervals']:
        a,b=timestamp(interval['start']),timestamp(interval['end'])
        if not started <= a <= b <= observed:
            raise ValueError('Invalid execution interval')
        intervals.append((a,b))
    seconds=union_seconds(intervals)
    fresh=(now-observed).total_seconds()<=freshness_seconds
    result.update(status=state if fresh else 'stale',confirmed_active_seconds=seconds,
                  reason='Historical intervals only; no extrapolation beyond evidence')
    if not fresh or state!='processing':
        return result
    # A processing status must agree with an interval reaching its observation.
    if not intervals or max(b for a,b in intervals)!=observed:
        result.update(status='unknown',reason='Processing state lacks current execution evidence')
        return result
    prefix='|'.join(run[k] for k in ('account_id','thread_id','turn_id'))
    triggers=[]
    if seconds>=threshold_seconds:triggers.append(('two_hour','two_hour'))
    local=now.astimezone(ZoneInfo(timezone))
    friday=local.date()-timedelta(days=(local.weekday()-4)%7)
    boundary=timestamp(datetime.combine(friday,time(18),ZoneInfo(timezone)).isoformat())
    # Catch up during the weekend, but only for runs with observed processing
    # crossing Friday's boundary; do not call a Saturday-started task a Friday run.
    if local.weekday() in (4,5,6) and now>=boundary and any(a<=boundary<=b for a,b in intervals):
        triggers.append(('friday_evening','friday_evening:'+friday.isoformat()))
    for trigger,suffix in triggers:
        key=prefix+'|'+suffix
        if key not in delivered:
            result['advisories'].append({'trigger':trigger,'severity':'red','deduplication_key':key,
                'active_seconds':seconds,'status_as_of':observed.isoformat(),
                'action':'Review progress and set a checkpoint; no automatic interruption.'})
    return result
