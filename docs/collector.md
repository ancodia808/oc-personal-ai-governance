# Local Desktop measurement contract

`scripts/collect_usage.py` reads current and archived JSONL session logs without modifying them or contacting a service. Only files whose metadata identifies both `Codex Desktop` and the selected account are eligible. Unknown or conflicting identities are excluded. CLI and VS Code activity are excluded. Desktop-originated support/child sessions with eligible metadata are included; their distinct responses are not assumed to be duplicates of parent usage.

Each response ID is counted once across files. Identical copies are discarded; inconsistent copies are excluded entirely. Only per-response `usage` is summed, never cumulative thread/turn snapshots. Total must equal input plus output; cached input and reasoning output are subsets, never extra tokens. Missing subset counts remain unknown. Invalid/missing primary counts or identifiers are excluded. No dollar-cost conversion is performed.

Intervals are start-inclusive and cutoff-exclusive. The default window is the trailing seven days (168 hours) ending at collection cutoff; it continues across week and daylight-saving boundaries. Usage is assigned by record timestamp, not filename, modification time, or task start. Full scans intentionally avoid missing old sessions resumed within the window. Daily buckets use Eastern dates. Missing days are absent, not asserted to be zero.

Output includes totals, daily/project breakdowns, record counts, diagnostics, and coverage limitations. It excludes prompts, response text, credentials, and raw account IDs. Project folder names remain private and may merge identically named folders. Parse errors, unsupported records, missing directories, and conflicting IDs are surfaced. These logs are an undocumented source: compatible observed schemas are supported, not guaranteed future versions. Appends after the read/cutoff appear on a later run.

Active processing and ongoing-run fields deliberately remain null. Completion gaps, elapsed wall time, and a token snapshot alone cannot establish a two-hour active-processing alert.

## Run

Use Python 3.11+ with operating-system timezone rules. Windows uses native APIs and macOS uses its system IANA database. No third-party Python package is required. Verify access with `python scripts/eastern_time.py`. Reporting is fixed to ET; non-Eastern configuration is rejected rather than silently mislabelled.

Create an ignored `private/collector.local.json` with `account_id` obtained from a verified local Desktop session's `creator_account_id`, and `timezone` set to `America/New_York`. Do not read authentication secrets or select the first account when multiple accounts exist. Keep this configuration private; it is separate from email/Slack onboarding settings.

```sh
python scripts/eastern_time.py
python scripts/collect_usage.py --config private/collector.local.json --output private/usage-snapshot.json
python -m unittest discover -s tests -v
```

Use `python3` where appropriate on macOS. `CODEX_HOME` defaults to the user's `.codex` directory; override with `--codex-home`. For repeatable reconciliation, supply `--start` and `--cutoff` as ISO timestamps with offsets. Output is required explicitly. Prefer a private path outside the checkout; inside this checkout only Git-ignored, untracked `private/` paths are accepted. Output replaces the specified snapshot atomically; use distinct filenames to retain history.

The collector creates a private JSON snapshot. Render that snapshot without additional collection or model calls:

```sh
python scripts/render_review.py --input private/usage-snapshot.json --output-dir private
```

This writes `daily-review.html` and `daily-summary.md`. Refresh the HTML in your browser. The Markdown includes an absolute local details link suitable for the project chat; links from other devices or email may not work. Rendering uses the snapshot cutoff, not the current clock, and reports arbitrary intervals accurately without labeling them as whole weeks. No third-party package is required.

Outputs remain private and are never sent automatically. The renderer verifies primary totals against daily/project breakdowns and escapes text in HTML/Markdown. Coverage issues receive priority in its maximum three findings. Findings are deterministic observations, not validated model-switch advice. Missing active-processing telemetry and unset budgets stay explicitly unavailable. Generation token accounting is not inferred: the renderer itself makes no model call, while any surrounding agent work uses tokens separately.

All test fixtures are invented. Platform validation to date is Windows; macOS and rendered browser visual verification remain pending. Scheduling and delivery are separate punch-list items.

## Payload sources and destinations

Daily HTML and Markdown reports include high-level requested sources and destinations over the same reporting interval as the token totals (rolling seven days by default). HTML lists observed external groups; chat/email summaries list the top five in each direction. Local project directories and Codex app groups are filtered from both readouts, including when rendering older snapshots. External means outside the local Codex environment, not necessarily outside the organization. Both sort by request-message count descending, then group name.

The collector inspects tool-call metadata only in eligible account/Desktop logs. A call ID counts once across current and archived copies. Each request message contributes at most one count per group and direction, even if a wrapper contains multiple calls to that group. Conflicting group classifications for one ID are excluded. These counts are neither payload bytes nor the number of emails, Slack messages, files or search results inside a response, and do not confirm success.

Supported attribution includes recognized Outlook, Slack, Codex app, Pages and SharePoint read/write operations; literal web opens grouped by hostname; web searches; relative-path local read/write commands grouped by their working project directory; and relative-path patch destinations. Website paths, queries, filenames, recipients and message bodies are not retained. Identically named project directories can merge. The readout headings are External Sources (requested) and External Destinations (posted). Website GET/web-open requests count only as sources. Website destinations require explicit HTTP POST and outbound-payload evidence; current adapters do not establish that evidence, so website destination rows are omitted, including legacy rows. A future POST adapter must establish method and payload before adding website destinations. Posted service operations are requests, not confirmed deliveries. Search requests do not expose a provider hostname, so their counts appear separately as unidentified-provider searches rather than in website rankings. Search results and domain filters are not evidence of query destinations. Service reads also send request metadata, which is not separately counted as outgoing.

Wrapper code is inspected statically without execution. Literal calls may be conditional or never executed. Dynamic arguments, arbitrary scripts, absolute or parent-relative shell targets, browser interactions and unsupported tools are omitted from attribution; the unclassified-request count makes this gap visible. A partly attributed wrapper can still contain omitted calls. This is a partial requested-access inventory, not a complete data-transfer or security audit. Older snapshots explicitly show this section as unavailable.

Synthetic preview: `examples/app/payload-report.html`; fixture: `examples/fixtures/payload-report.json`. Real snapshots and reports remain private. Daily emails attach the generated HTML; Slack point-in-time alerts are unchanged.

Diagnostic labels distinguish routine exclusions from uncertainty: "Running totals skipped to prevent double counting" counts unused cumulative totals; "Files skipped by account and app filters" counts known nonmatching accounts/apps; "Files that could not be attributed" counts missing or conflicting attribution and is shown only when nonzero. Legacy snapshots retain an explicitly combined label until recollected.

Project activity groups the recognized automatic `Documents/Codex/YYYY-MM-DD/<folder>` workspace layout under `<Chats without a project>`. This is a path-based classification; ordinary project folders retain their names.
