---
name: governance-onboarding
description: Interview a consultant to set up or update their personal AI Governance project, private recipients, and reporting preferences. Use for onboarding this repository, not for sending reports or enabling monitoring.
---

# Personal governance onboarding

Read the repository README, `docs/data-privacy.md`, and `docs/notification-design.md`. Locate the repository root from this skill's location. The implementation supports synthetic reports, private configuration, and an on-demand collector described in `docs/collector.md`; scheduled reporting and monitoring skills are implemented, but require a separate authorized activation handoff. Do not represent onboarding as active monitoring.

## Interview in the current chat

Ask questions as ordinary numbered chat text so they are visible without a special question UI. Use short rounds of at most three questions, wait for answers, and incorporate existing answers rather than asking again. Opening the project alone does not start an interview; invoking this skill does. Do not create another chat merely to conduct onboarding.

1. Ask which operating system they use, their daily-report email address (or whether they decline email), and their Slack workspace plus username/profile identity (or whether they decline Slack). Never assume the pilot owner's identity or preferences apply to a new consultant. Do not request passwords, tokens, or credentials in chat.
2. Offer configurable defaults: daily reports every day at 06:00 America/New_York; Friday active-processing warning at 18:00 in that timezone; checks every 30 minutes; long-run trigger after 120 minutes of reported Thinking/Working proxy duration (elapsed turn time, not verified continuous processing); one notification per trigger per run. Reporting uses fixed Eastern Time (ET). Ask for the host timezone for scheduling conversion and any schedule changes. Explain that Friday warnings apply regardless of duration, and all actions remain advisory.
3. Confirm baseline-first budgeting, a new project chat plus opted-in email for daily reports, Slack DMs for opted-in alerts, and whether project names/brief task descriptions are acceptable in those messages. Omit prompt excerpts. Explain that Slack/email create copies in those services and local HTML links may not work on other devices. Ask about private-data retention and overnight/offline availability for scheduling feasibility; do not promise monitoring while the host is asleep.

## Verify and save

If Slack tools are available, use read-only identity lookup to resolve the supplied handle in the intended workspace. Ask the user to disambiguate multiple matches. Store unresolved IDs as null and verification as false; missing connectors do not block the rest of the interview. Guide the user to connect Slack and Outlook through their own app when needed; never assume the current author's connectors carry over.

Use `config/onboarding.example.json` as the blank contract. Summarize selected settings in chat and resolve ambiguous answers before writing. Save to `private/onboarding.local.json` for this prototype only after `git check-ignore private/onboarding.local.json` confirms exclusion and `git ls-files -- private/onboarding.local.json` confirms it is untracked. If the folder is not a Git checkout or these checks fail, fix exclusion or select an authorized location outside the checkout before storing personal details. Never write them into README, shared docs, fixtures, or skill files.

On repeat setup, first ask whether an existing private configuration belongs to this user; do not display another person's details. Preserve unrelated fields in an owned configuration and update only requested settings. Leave `delivery_enabled` false. Do not change `private/pilot.local.json` unless the current user explicitly chooses to update that pilot configuration. Validate saved JSON without printing sensitive values.

## Finish with a reviewable result

Show the synthetic report and daily summary from `examples/app/`, using absolute file links in chat. Regenerate with `python scripts/build_demo.py` (or `python3` on macOS) if needed and available. Keep real data out of the demo.

Report the private configuration path, selected schedule/channels, verified versus unresolved connection status, and remaining implementation gaps. No emails, Slack test messages, schedules, or external publication are part of this setup interview. If the user requests activation separately, first establish telemetry and delivery readiness and use their existing authorization rather than asking them to reconfirm settled preferences.

## Prerequisites and activation handoff

Use the README requirements and config/readiness.example.json to maintain ignored private/readiness.local.json. Assume normal laptop and Git setup. Record readiness from actual setup operations and investigate failures when encountered. Internally preserve ignored/untracked private-path safeguards and establish local Desktop account eligibility, opted-in recipients and schedule timezone conversion. Avoid presenting routine environment checks to the user. Apply the same ignore/untracked checks as for onboarding configuration before storing readiness evidence. Record status, check time, evidence, blocker and next action for each item. Standard corporate apps being installed does not prove connector access. Never install or change permissions silently; use authorized setup steps. Existing pilot settings belong to their owner and must not be replaced during another user's onboarding.

Explain that runtime reads private/pilot.local.json and private/collector.local.json, not the onboarding file. On explicit activation, read and follow docs/team-setup.md for the complete handoff: prepare this user's runtime configuration, verify account metadata, generate a private report, perform authorized opted-in test sends, obtain receipt confirmation, then create schedules and store IDs in private readiness. Respect email_enabled/slack_enabled when present. Declined channels must not be tested or activated. Record nondefault policies as blocked until supported by the evaluator and scheduled skills; do not promise that saving a preference changes behavior. Keep retention unset until agreed; no automatic deletion exists. Do not enable recurring delivery solely because the interview finished.
