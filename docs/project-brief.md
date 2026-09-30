# Project brief

## Objective

Current activity-advisory policy uses fresh Thinking/Working status as a proxy, with elapsed-turn duration labeled where supplied by structured chat status. This supersedes earlier measured-active-processing wording for two-hour and Friday rules; no cost or continuous execution is inferred.

Establish a weekly personal usage budget, report daily progress against a soft limit, and coach expensive patterns across the user's Codex chats and projects. Recommendations must preserve useful outcomes and remain advisory: no automatic interruptions, model changes, or enforcement.

## Scope and evidence

- Prefer repository-owned, project-specific Codex skills and concrete artifacts (schemas, data fixtures, scripts, and an app where useful) for implementation and maintenance. Shared instructions, processes, and standards must be reviewable and reusable by the delivery consulting team rather than depend on an individual chat's history.

- Initial reports cover locally observed Codex Desktop metrics only. VS Code, chatgpt.com, and cross-application account usage summaries are deferred. Attribute usage to chats, projects, and models only where measured data supports it; expose unobserved devices, cloud runs, and attribution gaps. Do not describe these metrics as account-wide totals.
- Account usage sources may return unavailable windows or balances. Missing values cannot establish consumption, remaining capacity, or token totals. Capability checks and their user-specific results stay in private local storage.
- Chat summaries may support qualitative coaching but do not establish measured tokens, active execution time, or cost. Telemetry availability must be validated first.
- Tokens, account allowance percentages, credits, and currency are distinct units. Never convert between them without a documented conversion source. Keep API usage separate unless explicitly added later.
- Official [pricing documentation](https://learn.chatgpt.com/docs/pricing) is a reference to recheck during implementation; verify each user's data availability separately.

## Proposed policy - awaiting confirmation

| Decision | Proposed starting point |
| --- | --- |
| Budget unit and amount | Prefer measured tokens for an initial pilot; choose a numeric weekly budget after seven complete days of representative observation. User may supply a budget sooner. No active budget until confirmed. |
| Week | Monday 00:00 to next Monday 00:00, America/Chicago |
| Daily report | Confirmed: every day at 06:00 America/New_York, including weekends |
| Destination | A new project chat plus optional Outlook email to the affected member; local HTML details in chat. Slack DMs for long-run and other defined red-level warnings. Recipient setup and scheduled delivery require verification. |
| Pace warning | Week-to-date usage exceeds expected pace by at least 10% of the entire weekly budget |
| Weekly warning | At 80% and 100% of the confirmed weekly budget |
| Long-running advisory | Confirmed: two hours of measured active processing, excluding known approval/user waits; check every 30 minutes and notify the affected member by Slack DM |
| Friday-evening advisory | Confirmed: notify by Slack DM about processing still active Friday at 18:00 America/New_York, regardless of duration |
| Expensive turn | At least 5% of weekly token budget; after baseline, also review turns above the 95th percentile |

Except where explicitly marked confirmed, thresholds are pilot proposals. A trigger is not an assertion that a task or model is wasteful. Where reliable timing or usage is absent, report the corresponding signal as unavailable.

## Daily report contract

Show coverage and freshness first, then weekly measured usage/budget, expected pace, deviation, projected total, daily change, and remaining budget. List up to three meaningful deviations or expensive/long-running turns with evidence and one actionable suggestion each. Highlight potentially excessive reasoning effort, repeated context loading, duplicate work, or repeated failed attempts only when observable. Recommend model/workflow experiments; do not declare a model non-optimal solely because it is powerful or a task takes a long time.

Prioritize unattended processing that extends overnight or into/across a weekend. Show observed execution intervals, latest known state and freshness, and measured usage where available. Distinguish active execution from waiting, stale status, and missing observations. Recommend bounded work with checkpoints and explicit stop conditions. Daily reporting alone cannot prevent a costly weekend run; a more frequent advisory check requires an agreed trigger, cadence, and delivery policy before activation.

Example format (placeholders, not measured results):

> Coverage: [sources, gaps, last observation]. Weekly usage: [U] / [B] tokens. Expected: [E]; deviation: [U-E]. Projected: [P]; remaining: [B-U]. Since prior report: [delta]. Review: [turn, measured tokens/time, observed pattern]. Suggested experiment: [change and quality check].

## Success and sharing

All collected user data and derived presentations are private and excluded from Git, including aggregates, redacted records, reports, app state, visualizations, screenshots, and exports. Version reusable source, standards, templates, and wholly synthetic examples, including populated reference reports and app/visualization artifacts that establish consistent results and presentation. Follow the [data privacy standard](data-privacy.md).

Success means a reproducible weekly ledger, an honest daily report even when telemetry is missing, useful evidence-based coaching, and no duplicate accounting or unsupported cost claims. Keep raw telemetry and personal reports local. Prepare sanitized code, policy templates, synthetic examples, and documentation for a user-approved GitHub repository and intended audience.

Team consistency means the same versioned inputs and policy produce the same calculated metrics and validation outcomes. Skills should invoke tested repository tools for calculations and validation, and guide interpretation using shared evidence standards. Narrative coaching can vary; its required evidence, report structure, and acceptance criteria must remain consistent. Personal budgets and account access stay configurable without changing the shared process.

Before activation, confirm budget unit/amount, thresholds, cadence, timezone/week boundary, and destination. Before publishing, confirm repository owner/name, visibility, audience, and exact sanitized content. These gates come from the user's request.
