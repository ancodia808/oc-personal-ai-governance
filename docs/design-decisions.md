# Confirmed design decisions

The design interview established these choices:

- Revised activity policy supersedes the earlier verified-processing requirement: use fresh Thinking/Working status and reported duration as proxies. Structured active/in-progress chat status maps to Working with elapsed-turn duration explicitly labeled. Two hours triggers an advisory; Friday 18:00 triggers regardless of duration. Do not describe this as verified continuous processing or cost. See `docs/active-processing.md`.

- Initial metric scope: locally observed Codex Desktop activity only. Exclude VS Code, chatgpt.com, and cross-application account usage summaries from the usage review. Those integrations are deferred. Label the retained metrics as partial local coverage rather than account-wide totals.

- First milestone: an end-to-end synthetic demo, followed by private usage integration.
- Daily delivery: a new chat in this project for each daily report. Scheduling remains disabled until cadence and thresholds are confirmed and the delivery mechanism is verified.
- Confirmed cadence: every day, including weekends, at 06:00 America/New_York. Friday active-processing warnings run at 18:00 in the same timezone. Follow daylight saving time automatically.
- Budget: observe a baseline before setting a numeric weekly budget.
- Summary: up to three findings, with links to local report details.
- Coaching: cover long or expensive tasks, model/reasoning choices, repeated work/context, and prompt/workflow structure. Preserve quality; recommend savings when evidence supports them.
- Explicit priority: identify and discourage unattended long-running prompts that continue processing across a weekend. Daily reports must surface observed weekend execution and still-running tasks; prompt age alone is not evidence of processing or expense. More frequent advisory checks are a proposed extension, with cadence and thresholds still to be agreed. Automatic stopping is not authorized.
- Confirmed advisory triggers: two hours of active processing, excluding known waits; also notify when processing remains active on Friday evening, regardless of whether it has reached two hours. Check every 30 minutes. Deliver long-run and other red-level warnings directly to the affected team member through Slack DMs. Do not infer uninterrupted processing from stale status or elapsed chat age.
- Pilot delivery: Outlook daily email alongside the new project chat, and Slack direct messages for alerts, addressed only to the pilot owner. User-supplied recipients are stored in ignored local configuration; Slack workspace/user identity still requires verification. Never commit recipient mappings or delivery logs. Use once-per-trigger-per-run deduplication. Additional red-level conditions require explicit definitions.
- Privacy: show project names and brief task descriptions, without prompt excerpts. All real data and derived output stay out of Git.
- Platforms: Windows and macOS with Codex desktop.
- Detail view: a self-contained local HTML report with charts and tables; no server required.

Open decisions: additional red-level definitions, weekend boundaries per team member, baseline completeness criteria, numeric budget and thresholds after baseline, retention period, and installation/update workflow for teammates. Slack identity resolution, runtime availability, and account-wide telemetry coverage require verification.
