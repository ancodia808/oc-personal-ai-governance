# Active-processing advisories

## Current policy: Thinking/Working proxy

The user approved status-based advisories in place of verified processing intervals. The supported entry point is `scripts/check_activity.py`, using `evaluate_proxy` and `normalize_thread` from `scripts/evaluate_activity.py`. The older interval engine below is retained for reference/tests, not used by this command.

- Two-hour advisory: fresh Thinking or Working status and reported duration at least 7,200 seconds.
- Friday advisory: fresh Thinking or Working status on Friday at/after 18:00 in the configured timezone, regardless of duration. No historical boundary-crossing evidence is required. Friday polling continues until local midnight; no Saturday catch-up claim is made.
- The live adapter maps structured `read_thread` status `active` plus one `inProgress` turn to Working. It computes elapsed turn time from `startedAt`; it does not claim a literal UI label or uninterrupted processing. Any active flags conservatively yield unknown, since approval/input flag semantics have not been established comprehensively.
- A fresh `notLoaded` observation with exactly one returned latest turn marked `completed` and no active flags is `offloaded`. Count it as checked and non-running, exclude it from long-run/Friday advisories, and do not flag it as uncertain coverage. Missing, unfinished or ambiguous turn evidence remains unknown. Re-evaluate on every check; offloaded is not permanent.
- Thinking is accepted by the normalized policy interface if a source supplies it explicitly. The current adapter does not infer Thinking from message text.
- Observations older than five minutes, future timestamps, waiting/idle states, and ambiguous run identity do not alert. Unknown duration prevents the two-hour trigger but not Friday's trigger.
- Alerts say the chat *appears* to still be thinking/working. They never assert verified processing, tokens consumed, or cost. Deduplication keys use host/chat/turn/trigger, plus Friday's date. Only successful delivery receipts suppress future sends.

### Obtain and evaluate a live observation

In an authorized monitoring chat, use `list_threads(limit=50)` to discover the 50 most recent non-pinned chats plus all returned pinned chats, then `read_thread` with `turnLimit: 1` and `includeOutputs: false` for fresh status. Do not interpret `notLoaded` as idle. Filter to locally verified Desktop-origin chats using session metadata; the app's Codex list may also contain extension chats. Combine both lists, deduplicate by host/chat ID, and exclude the monitoring chat. Inspect all eligible active/notLoaded candidates in this scoped set, including pinned candidates beyond 50. Reaching the recent-list limit and older unpinned inventory IDs outside this set are expected scope boundaries. Report unavailable hosts or uninspected eligible in-scope candidates as coverage gaps. This project remains Desktop-only.

Save an envelope with `observed_at` (actual retrieval time) and `snapshot` containing only thread `id`, `hostId`, `title`, `status`, and turn `id`, `status`, `startedAt`. Exclude returned messages and tool content. Optional `delivered_keys` contains previously successful receipts. Store the envelope privately. Never refresh its observation timestamp without retrieving status again.

```sh
python scripts/check_activity.py --input private/activity-observation.json --output private/activity-evaluation.json
```

The command reads a supplied observation; it cannot independently invoke desktop MCP tools from a shell. An agent/scheduler integration must fetch observations every 30 minutes and evaluate eligible chats within the recent-50-plus-pinned scope. One live Desktop chat was checked successfully on Windows; full inventory polling, scheduling, and delivery remain pending. No notification is sent by this command.

## Superseded interval design

The following contract describes the older stricter policy. It is not required for the approved status-proxy advisories.

`scripts/evaluate_activity.py` accepts explicit processing intervals and a fresh state observation from a future verified adapter. It unions overlapping intervals, excludes gaps, never extrapolates stale state, and produces two-hour/Friday advisory candidates only while processing is confirmed. It does not send, stop tasks, or schedule work. A string marking evidence as verified is a contract, not verification by itself; adapters must establish those semantics before calling it.

## Source findings

Inspected local Desktop logs expose task starts/completions, token usage, and completed items with start/end timestamps. These demonstrate activity and elapsed intervals, but do not establish a complete processing-versus-wait state machine. Commands and MCP calls may include idle/wait time, and missing completion may mean a crash, approval, stale file, or a still-running task. Do not count their entire elapsed duration as processing. No personal observations or log samples belong in this document.

## Decision contract

- Input identity: account, thread, and turn IDs, stored privately.
- Input intervals: UTC-offset timestamps for independently verified processing; waits must be absent. Overlaps and duplicates count once. All intervals must lie between run start and state observation.
- Current state: processing, waiting, completed, interrupted, failed, or unknown. Observation must be no more than five minutes old by default and never in the future. Each 30-minute check must fetch a fresh observation.
- Two-hour threshold: at least 7,200 accumulated processing seconds, with fresh processing state and a processing interval reaching that observation.
- Friday: observed processing crossing Friday 18:00 in the configured timezone, with fresh processing state. A delayed weekend check can catch up for that boundary; a Saturday-started task is not classified as having crossed Friday.
- Deduplication keys distinguish run and trigger; Friday includes the date. Pass only successful delivery receipts to suppress future candidates. Persist receipts privately in the delivery layer; do not mark a candidate delivered before successful sending.
- Unknown/stale/waiting/completed states yield no red advisory. They must still appear as coverage limitations in reports; no alert does not mean no risk.

## Remaining live-source acceptance work

Verify a supported execution event source and collect synthetic controlled traces for model execution, commands, user approvals, sleeps, retries, cancellation, restart, and lost telemetry. Establish whether provider processing or only client elapsed time is measurable. Add a source adapter only after those distinctions are demonstrated; otherwise propose a separately labeled elapsed-task reminder for user approval rather than silently weakening the active-processing policy.

Scheduling, live integration, and delivery remain incomplete. The collector's active-processing fields remain null until source verification succeeds.
