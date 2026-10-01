# Offline monitoring and consolidated Slack delivery

Run `python -B scripts/offline_monitor.py --queue` once from the repository (`python3` on macOS). The command reads private configuration, scans local Codex records, prints JSON, saves `private/offline-monitor/latest.json`, and exits. Codex provides the 30-minute cadence and Friday 18:00 ET check. No persistent loop or Windows Task Scheduler is used. The detector has no network or model calls; its surrounding Codex agent still requires working sandbox permissions and consumes tokens.

## Policy

Each uniquely identified unmatched turn start is considered separately, including multiple starts in one chat. Closed or ambiguous turns never alert. From two hours until just before 24 hours, show the start under **Possibly still running**. On Friday at/after 18:00 ET, include younger unmatched starts too. These are uncertain elapsed-start proxies, not proof of live Thinking/Working, uninterrupted processing or cost.

At 24 hours the start leaves the active list and becomes **Final Notice!**. Send the final once, including on the next successful check if the cutoff was missed. A final at least one check interval late is labeled delayed. Already-old unmatched starts discovered at activation are also eligible for one final notice. Recorded completion suppresses an unsent notice. Pending/ambiguous delivery stays reserved for user review; it is never automatically retried. A successful final receipt retires that start permanently from future digests. This does not assert that it completed.

Send at most one consolidated digest per 30-minute UTC time slot to the configured verified recipient. Include the full active list every interval plus all final notices not already sent or pending. Stay quiet when empty. The Friday schedule shares the same slot and ledger, preventing duplicate sends. No backlog of old digests is delivered: every claim requires a fresh scan, and old queued digests expire.

## Format

Title: **PAIGe - Possibly still running**

Greeting: `<@VERIFIED_USER_ID>, you have chats that may still be running (see below).` Append `This is the final notice for some of them.` only when final notices are present.

One bullet per unmatched start: `"Project" - "Chat" - Started 24h 00m ago - **Final Notice!**`. Omit the final suffix for active entries; delayed finals add `(delayed)`. Sort by Project then Chat, with projectless chats last and their project prefix omitted. Within a chat, older starts sort first. Escape label markup and mentions. The local Codex session index supplies chat titles, with thread ID as fallback; session working-folder names provide project labels, and recognized automatic projectless folders omit the prefix. Folder labels are not authoritative project registration.

Close with `Unmatched starts do not confirm ongoing processing.` When finals are present, explain that they leave the active list with status unknown. Do not silently truncate a full listing or send separate per-chat DMs. If a connector size limit prevents one message, report the delivery limitation without claiming success.

## Delivery procedure for the authorized scheduled agent

1. Follow AGENTS.md. Read `private/pilot.local.json` and `private/collector.local.json`; stop if disabled. Run the one-shot command in normal sandbox permissions. Never silently escalate during a scheduled check. Failure means coverage unavailable; do not treat an old snapshot as current.
2. Read the new result. Surface material gaps, with no claims that zero notices prove inactivity. If `digest_key` is null, send nothing. If Slack is disabled/unverified, no queue is eligible; report actionable findings only in the authorized chat.
3. Immediately before sending, run `python -B scripts/offline_monitor.py --claim KEY`, safely quoting the exact returned digest key. This rescans and claims a fresh digest in `private/delivery-ledger.sqlite`. Only `send_allowed: true` permits a send. Use the returned `payload.message` verbatim and `payload.recipient` as the Slack DM destination. Do not query Slack or enrich the evidence. If more than five minutes pass after claiming, leave pending for review rather than sending stale information.
4. After immediate successful Slack acceptance, run `python -B scripts/offline_monitor.py --complete KEY --receipt RECEIPT` with the tool response/message link. This records the shared ledger receipt and retires the digest's final notices. Never inspect Slack history to confirm delivery. Failed/ambiguous sends remain pending; do not retry automatically. Do not claim success without a receipt.
5. Stay quiet on empty or unchanged non-actionable coverage failures. A nonempty active list intentionally produces one digest each 30-minute slot, even if unchanged. No source or schedule edits during runs. All observations, recipient settings, queue data and receipts remain private.

Legacy per-turn queue rows expire and cannot be claimed by the digest adapter. Existing delivery ledger keys are preserved; new digests use a separate `offline-digest|SLOT|RECIPIENT` namespace. A private final-notice table reserves individual finals within a claimed digest and marks them sent only after acceptance. Ambiguous finals stay reserved to prevent duplicates.

## Evidence and operation

Only configured-account Desktop session metadata and lifecycle records from local `sessions`/`archived_sessions` are read, plus the local Codex title index for display. Duplicate records merge; completion in either copy closes a turn. Unsupported or malformed evidence stays unknown. The scan covers all attributable local Desktop lifecycle records, not the live tool's recent-50-plus-pinned scope. Counts describe turns, not chats. No recorded tool code is executed or logged target revisited. Read errors/missing directories suppress queue creation. The previous successful timestamp exposes stale snapshots; gaps over 45 minutes are reported, not reconstructed.

Python 3.11+, Git for the private-output guard, and OS Eastern timezone rules are required; no third-party packages. The laptop and Codex scheduler must be available. macOS execution, sustained scheduled operation and production digest transport remain unverified. Tests use isolated invented records, never inject events into real Codex logs, and never send messages.
