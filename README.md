# PAIGe - Personal AI Governance

An advisory system for understanding and managing personal Codex usage across chats and projects, with reusable guidance for teammates.

Implementation preference: repository-owned, project-specific Codex skills backed by versioned code, schemas, synthetic data, and an app where useful. Shared processes and validation criteria support consistent use across the delivery consulting team; personal telemetry and reports remain private local artifacts.

Versioned synthetic datasets, populated demo reports, and reference app/visualization artifacts establish shared expectations for both calculations and presentation. Example builds use synthetic inputs exclusively.

Status: collector, renderer, activity-proxy checks, onboarding, and scheduled-workflow skills implemented. Scheduled pre-checks and delivery validation have been accepted; normal schedules are enabled for the local pilot. New-user onboarding only saves preferences and does not activate schedules or notifications.

A reusable, on-demand local Codex Desktop collector and HTML/Markdown renderer are available. See [setup and measurement rules](docs/collector.md), [scheduled pilot operations](docs/scheduled-pilot.md), and the maintained [implementation punch list](docs/implementation-punch-list.md). All actual snapshots, reports, and recipients remain private.

## Set up in your own Codex app

1. **Get your own checkout.** Clone `https://github.com/ancodia808/oc-personal-ai-governance.git` to a local folder on Windows or macOS. Copy only shared source if using a source package; do not copy another person's `private/`, runtime data, or reports. Git is needed for the privacy checks. Python 3.11+ is needed for collection, monitoring, report generation and tests; viewing the supplied HTML needs no server or Python.
2. **Open that folder as a local project in Codex desktop.** Start a new chat in that project, using the checkout root as its working folder. Keep onboarding in this chat. Each consultant uses their own checkout, accounts, and private settings.
3. **Start the interview.** Paste and send this message:

   ```text
   Use $governance-onboarding to set up my personal AI Governance project. Interview me in this chat for my email address, Slack workspace and username, timezone, schedule, and reporting preferences. Save my settings privately, show me the synthetic report, and explain what is ready versus still pending. Do not send messages or enable schedules during setup.
   ```

   The repository includes the skill at `.agents/skills/governance-onboarding/SKILL.md`. Codex discovers repository skills from `.agents/skills`; if it does not appear, restart Codex and try a new project chat. You can also ask: `Read .agents/skills/governance-onboarding/SKILL.md and follow its onboarding interview.` See the official [skill discovery documentation](https://learn.chatgpt.com/docs/build-skills).

4. **Answer the short interview rounds.** Expect questions about your own email, Slack workspace/username, operating system, timezone, and message content. Defaults offered for your review are daily 06:00 Eastern reports, Friday 18:00 Eastern warnings, 30-minute checks, and a two-hour active-processing trigger. You can change them or decline either external delivery channel. The budget stays unset until a baseline is measured.
5. **Connect your own apps when prompted.** For external delivery, connect Slack and Outlook Email through the integrations available in your Codex app. Complete sign-in in the app, not by pasting credentials into chat. The interview can finish with unresolved connections; it must identify those gaps. Slack handles must resolve to the correct workspace/user before sending.
6. **Review the result.** The chat should show your selected settings, a link to the synthetic HTML report, and connection/readiness gaps. Your answers are saved in ignored `private/onboarding.local.json`; the repository contains only a blank configuration template. Delivery remains disabled. Live telemetry, unattended scheduling, and delivery validation are later implementation steps, not completed by this interview.

To update your setup later, invoke `$governance-onboarding` again and describe what changed. Never commit private configuration or share the onboarding chat as a team example. Use synthetic artifacts for team demonstrations.

## Try the synthetic demo

Open [the HTML report](examples/app/daily-report.html) or [the daily chat summary preview](examples/app/daily-summary.md). Neither requires a server.

To regenerate with Python 3.11 or newer (standard library only), run `python scripts/build_demo.py` from the repository root; on macOS use `python3` if needed. Run checks with `python -m unittest discover -s tests -v`. The generator reads only the bundled synthetic fixture and has no private-data input option. A synthetic label is not an anonymization mechanism: never replace the fixture with collected data.

Reference artifacts were generated with Python 3.14.5 on Windows. macOS execution and rendered visual checks remain to be verified. Demo checks cover totals, duplicate identifiers, invalid token counts, and refusal of inputs not labeled synthetic. The separate collector tests cover real-log measurement rules using synthetic records. Automated coaching detection is not implemented.

- [Project brief](docs/project-brief.md)
- [Implementation plan](docs/implementation-plan.md)
- [Data privacy standard](docs/data-privacy.md)
- [Confirmed interview decisions](docs/design-decisions.md)

## Copyright and licensing

Copyright (c) 2026 Oracle.

The project license is undecided; no open-source license is granted by this repository. Third-party dependency license review remains on the implementation punch list before team rollout or distribution. Installed dependencies and private runtime artifacts are not included.
