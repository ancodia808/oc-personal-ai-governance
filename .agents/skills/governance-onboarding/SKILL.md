---
name: governance-onboarding
description: Interview a consultant to set up or update their personal AI Governance project, private recipients, and reporting preferences. Use for onboarding this repository, not for sending reports or enabling monitoring.
---

# Personal governance onboarding

Read the repository README, `docs/data-privacy.md`, and `docs/notification-design.md`. Locate the repository root from this skill's location. The implementation supports synthetic reports, private configuration, and an on-demand collector described in `docs/collector.md`; scheduled delivery is not implemented. Do not represent onboarding as active monitoring.

## Interview in the current chat

Ask questions as ordinary numbered chat text so they are visible without a special question UI. Use short rounds of at most three questions, wait for answers, and incorporate existing answers rather than asking again. Opening the project alone does not start an interview; invoking this skill does. Do not create another chat merely to conduct onboarding.

1. Ask which operating system they use, their daily-report email address (or whether they decline email), and their Slack workspace plus username/profile identity (or whether they decline Slack). Never assume the pilot owner's identity or preferences apply to a new consultant. Do not request passwords, tokens, or credentials in chat.
2. Offer configurable defaults: daily reports every day at 06:00 America/New_York; Friday active-processing warning at 18:00 in that timezone; checks every 30 minutes; long-run trigger after 120 active minutes excluding known waits; one notification per trigger per run. Ask for timezone and any changes. Explain that Friday warnings apply regardless of duration, and all actions remain advisory.
3. Confirm baseline-first budgeting, a new project chat plus opted-in email for daily reports, Slack DMs for opted-in alerts, and whether project names/brief task descriptions are acceptable in those messages. Omit prompt excerpts. Explain that Slack/email create copies in those services and local HTML links may not work on other devices. Ask about overnight/offline availability for future scheduling feasibility; do not promise monitoring while the host is asleep.

## Verify and save

If Slack tools are available, use read-only identity lookup to resolve the supplied handle in the intended workspace. Ask the user to disambiguate multiple matches. Store unresolved IDs as null and verification as false; missing connectors do not block the rest of the interview. Guide the user to connect Slack and Outlook through their own app when needed; never assume the current author's connectors carry over.

Use `config/onboarding.example.json` as the blank contract. Summarize selected settings in chat and resolve ambiguous answers before writing. Save to `private/onboarding.local.json` for this prototype only after `git check-ignore private/onboarding.local.json` confirms exclusion and `git ls-files -- private/onboarding.local.json` confirms it is untracked. If the folder is not a Git checkout or these checks fail, fix exclusion or select an authorized location outside the checkout before storing personal details. Never write them into README, shared docs, fixtures, or skill files.

On repeat setup, first ask whether an existing private configuration belongs to this user; do not display another person's details. Preserve unrelated fields in an owned configuration and update only requested settings. Leave `delivery_enabled` false. Do not change `private/pilot.local.json` unless the current user explicitly chooses to update that pilot configuration. Validate saved JSON without printing sensitive values.

## Finish with a reviewable result

Show the synthetic report and daily summary from `examples/app/`, using absolute file links in chat. Regenerate with `python scripts/build_demo.py` (or `python3` on macOS) if needed and available. Keep real data out of the demo.

Report the private configuration path, selected schedule/channels, verified versus unresolved connection status, and remaining implementation gaps. No emails, Slack test messages, schedules, or external publication are part of this setup interview. If the user requests activation separately, first establish telemetry and delivery readiness and use their existing authorization rather than asking them to reconfirm settled preferences.
