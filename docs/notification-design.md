# Notification delivery design

## Naming

PAIGe stands for Personal AI Governance. Prefix schedule names, email subjects, Slack notification headings, and notification failure headings with `PAIGe - `. Keep existing automation IDs and delivery-ledger keys stable so renaming does not cause duplicate sends.

## Agreed routing

Activity policy update: Thinking/Working status is the approved proxy for the long-run and Friday rules below, replacing measured active processing. Structured active/in-progress status is labeled Working with elapsed-turn time; alerts describe apparent activity, not proven execution or expense. Unknown duration still permits Friday warnings. The old active-duration wording in examples must not be used for proxy notifications.

- Run long-processing checks every 30 minutes. Notify the affected member by Slack direct message when a run reaches two hours of measured active processing.
- Notify the member about processing still active Friday evening, regardless of duration. Confirmed cutoff: Friday 18:00 America/New_York.
- Route other red-level warnings to Slack DMs once their conditions are defined. Do not invent token or spending thresholds before the baseline and budget decision.
- Generate a daily project chat, including weekends. Confirmed time: daily 06:00 America/New_York. Send an additional Outlook email to the pilot owner. Use timezone-aware scheduling across daylight saving changes.

Polling means detection can occur up to roughly 30 minutes after crossing a threshold when checks run normally; delayed execution or missing telemetry may increase that delay. Verify execution while the user's computer is asleep or offline before promising unattended coverage.

## Private recipient setup

Resolve and verify the affected member's Slack workspace/user ID and Outlook recipient address before enabling delivery. Store mappings and delivery receipts outside Git. Each consultant receives their own activity only. No channel broadcasts, manager copies, or team-wide usage digest are implied.

Slack send-message and Outlook send-email tools are exposed in the current session. This confirms interactive capabilities, not unattended scheduler access or successful delivery. Validate those separately using a clearly labeled synthetic test addressed to the configured member before activation.

## Message contract

Slack alerts include severity, trigger, project name, brief task description, measured active duration, latest observation time, and a quality-preserving action. Omit prompt excerpts and include token totals only when observed. A synthetic example:

> RED — Long-running processing: Integration demo / Validate mapping examples has accumulated 2h 08m of active processing. Latest observation: [timestamp]. Review progress and set a checkpoint or stop condition before leaving it unattended. No automatic interruption has occurred. Synthetic example only.

Daily email includes the same concise summary and up to three findings as the project chat. Local filesystem report links may not open from email or another device; identify the project chat as the place to access local details. Do not publish or attach private HTML automatically. Email and Slack content are external copies of private data, authorized only for the affected member's configured destinations.

## Delivery reliability — proposed

Deduplicate by member, run, trigger, and delivery channel. Send once per trigger per run; Friday escalation remains distinct from the two-hour alert. Persist delivery state privately across restarts. Retry transient failures with bounded backoff; reconcile ambiguous sends before retrying to avoid duplicate messages. Record failures locally and surface them in the next report. Repeated escalation intervals remain unconfigured.

Pilot status: the owner confirmed both synthetic delivery tests arrived. Daily, half-hourly, and Friday schedules are enabled with private recipient configuration and durable send claims. First unattended runs and outage behavior still require validation; see `scheduled-pilot.md`. Coverage remains local Desktop only.
