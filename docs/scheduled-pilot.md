# Scheduled pilot operations

Three local app automations are enabled for the current pilot:

| Workflow | Intended schedule | Run destination |
| --- | --- | --- |
| PAIGe - Daily review | Every day, 06:00 America/New_York | New project chat and configured Outlook recipient |
| PAIGe - Long-run checks | Every 30 minutes | Existing monitoring chat; new warnings to configured Slack DM |
| PAIGe - Friday check | Friday, 18:00 America/New_York | Existing monitoring chat; configured Slack DM |

The current host is America/Chicago. The daily and Friday app rules use 05:00 and 17:00 host time. Verify the displayed next-run times in Scheduled and the first actual runs. If the machine timezone changes, adjust these schedules; do not assume they remain anchored to Eastern automatically. US Central and Eastern daylight-saving transitions currently keep these scheduled-hour conversions aligned.

Reporting uses `.agents/skills/governance-daily-report/SKILL.md`; monitoring uses `.agents/skills/governance-monitor/SKILL.md`. Shared files contain procedures only. Identities, recipients, observations, generated reports, and receipts remain private. Local dependency access failures must surface as failures; scripts must not fabricate a report or alter security settings to continue.

## Availability and verification

The computer must be on and the desktop app running for local scheduled tasks. Sleeping, shutdown, offline services, missing permissions, or expired connections may delay or prevent checks. This pilot does not wake the computer or provide cloud failover. See [official scheduled-task documentation](https://learn.chatgpt.com/docs/automations).

Manual Slack and email tests were confirmed received. Accelerated scheduled tests subsequently completed real daily collection/rendering and email connector acceptance, plus synthetic two-hour and Friday Slack connector acceptance. Duplicate claims were suppressed. The first monitoring tests failed on timezone package access; after a scoped permission repair, scheduled retries passed. A later normal 30-minute monitoring cycle also completed. All original schedules were verified restored; the temporary audit is retired after verification.

The pilot owner confirmed receipt of the scheduled email and both Slack test DMs. These results establish scheduled workflow execution and delivery, but not real Friday wall-clock behavior. NotLoaded chats with a completed latest turn now normalize to offloaded and count as non-running. Missing or ambiguous turn evidence remains unknown. Normal morning/Friday timing, sleep/offline recovery and macOS remain unverified. Earlier 36-test results required elevation; a later full-suite sandbox run hit temporary-directory permission errors, separate from the repaired timezone issue. The seven proxy tests passed without elevation.

Keep monitoring checks compact. Record meaningful coverage gaps, including unavailable statuses or eligible in-scope chats left uninspected. Monitor agent token overhead during the baseline: a 30-minute heartbeat can run up to 48 times daily and uses model context even when nothing alerts. The daily job uses a low-effort model and deterministic generation; the heartbeat inherits its chat settings.

## Duplicate delivery and failures

`scripts/delivery_ledger.py` uses SQLite unique keys and transactions to claim sends. Only a newly claimed key allows sending. A successful tool response records a receipt; uncertain outcomes remain pending and are not retried automatically. This favors avoiding duplicate messages over guaranteed eventual delivery. Review pending failures manually, reconcile the actual destination, and only then decide whether to retry. Keys include recipient/channel scope; changing recipients should not silently reuse old receipts.

## Disable and resume

Pause all three PAIGe automations in Scheduled, or ask Codex to pause those named automations. Setting `delivery_enabled` to false in private/pilot.local.json prevents skill-driven sends but does not stop scheduler/model usage. Use both when stopping the pilot. Do not delete receipt history when pausing or resuming.

Before resuming, verify local configuration and connections, then resume the existing schedules rather than creating duplicates. A delayed daily run sends at most the current day's report. Missing Friday observations cannot reconstruct past status.

Monitoring covers the 50 most recent non-pinned chats plus all pinned chats returned by the app, filtered to the configured account and local Desktop origin. Older unpinned chats are outside this scope; reaching 50 results is not a failure. Daily token collection still uses all eligible local session logs.
