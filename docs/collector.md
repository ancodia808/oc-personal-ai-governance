# Local Desktop measurement contract

`scripts/collect_usage.py` reads current and archived JSONL session logs without modifying them or contacting a service. Only files whose metadata identifies both `Codex Desktop` and the selected account are eligible. Unknown or conflicting identities are excluded. CLI and VS Code activity are excluded. Desktop-originated support/child sessions with eligible metadata are included; their distinct responses are not assumed to be duplicates of parent usage.

Each response ID is counted once across files. Identical copies are discarded; inconsistent copies are excluded entirely. Only per-response `usage` is summed, never cumulative thread/turn snapshots. Total must equal input plus output; cached input and reasoning output are subsets, never extra tokens. Missing subset counts remain unknown. Invalid/missing primary counts or identifiers are excluded. No dollar-cost conversion is performed.

Intervals are start-inclusive and cutoff-exclusive. The default start is Monday midnight in the configured IANA timezone, including daylight-saving changes. Usage is assigned by record timestamp, not filename, modification time, or task start. Full scans intentionally avoid missing old sessions resumed this week. Daily buckets use the same timezone. Missing days are absent, not asserted to be zero.

Output includes totals, daily/project breakdowns, record counts, diagnostics, and coverage limitations. It excludes prompts, response text, credentials, and raw account IDs. Project folder names remain private and may merge identically named folders. Parse errors, unsupported records, missing directories, and conflicting IDs are surfaced. These logs are an undocumented source: compatible observed schemas are supported, not guaranteed future versions. Appends after the read/cutoff appear on a later run.

Active processing and ongoing-run fields deliberately remain null. Completion gaps, elapsed wall time, and a token snapshot alone cannot establish a two-hour active-processing alert.

## Run

Use Python 3.11+ and install `requirements.txt` into your chosen Python environment (prefer a virtual environment outside the checkout). On Windows this supplies the IANA timezone database; macOS can also use it when system data is unavailable. The pinned package must be reviewed when timezone rules change.

Create an ignored `private/collector.local.json` with `account_id` obtained from a verified local Desktop session's `creator_account_id`, and `timezone` such as `America/New_York`. Do not read authentication secrets or select the first account when multiple accounts exist. Keep this configuration private; it is separate from email/Slack onboarding settings.

```sh
python -m pip install -r requirements.txt
python scripts/collect_usage.py --config private/collector.local.json --output private/usage-snapshot.json
python -m unittest discover -s tests -v
```

Use `python3` where appropriate on macOS. `CODEX_HOME` defaults to the user's `.codex` directory; override with `--codex-home`. For repeatable reconciliation, supply `--start` and `--cutoff` as ISO timestamps with offsets. Output is required explicitly. Prefer a private path outside the checkout; inside this checkout only Git-ignored, untracked `private/` paths are accepted. Output replaces the specified snapshot atomically; use distinct filenames to retain history.

The collector creates a private JSON snapshot. Render that snapshot without additional collection or model calls:

```sh
python scripts/render_review.py --input private/usage-snapshot.json --output-dir private
```

This writes `daily-review.html` and `daily-summary.md`. Refresh the HTML in your browser. The Markdown includes an absolute local details link suitable for the project chat; links from other devices or email may not work. Rendering uses the snapshot cutoff, not the current clock, and reports arbitrary intervals accurately without labeling them as whole weeks. No new third-party package is required beyond the existing timezone dependency.

Outputs remain private and are never sent automatically. The renderer verifies primary totals against daily/project breakdowns and escapes text in HTML/Markdown. Coverage issues receive priority in its maximum three findings. Findings are deterministic observations, not validated model-switch advice. Missing active-processing telemetry and unset budgets stay explicitly unavailable. Generation token accounting is not inferred: the renderer itself makes no model call, while any surrounding agent work uses tokens separately.

All test fixtures are invented. Platform validation to date is Windows; macOS and rendered browser visual verification remain pending. Scheduling and delivery are separate punch-list items.
