# PAIGe - Personal AI Governance

PAIGe provides private Codex Desktop usage reports and Slack advisories for chats that appear to be running too long. Reusable project skills guide setup, reporting and monitoring; actual usage data and personal settings stay in ignored `private/` files, outside Git.

## Requirements

With this repository already cloned and Codex configured, you need:

- Python 3.11+ available to Codex. No additional Python packages or server are required.
- Slack and Outlook Email connectors in Codex for the delivery channels you choose.
- The laptop awake and Codex running for local scheduled checks.

This solution has been validated in Windows and macOS. Reports and notification times use Eastern Time (ET), with daylight-saving rules supplied by the operating system.

## Setup

1. **Open the cloned folder as a local Codex project** and start a new chat.
2. **Start the interview** with this message:

   ```text
   Use $governance-onboarding to set up PAIGe for me. Interview me for my email address, Slack workspace and username, host timezone, schedules and privacy preferences. Save my settings privately and show me the example report. Do not send messages or enable schedules yet.
   ```

   If the skill is unavailable, ask Codex to read `.agents/skills/governance-onboarding/SKILL.md` and follow it. Connect any chosen Slack or Outlook integration when prompted.

3. **Review your settings, then activate** in the same chat:

   ```text
   Activate PAIGe with my approved settings. Prepare my runtime configuration, generate a private report, and send a test to each chosen delivery channel. After I confirm receipt, enable my schedules and confirm their Eastern times.
   ```

Codex handles the private account and recipient configuration. Daily emails include the HTML report as an attachment; download and open it in a browser. Reports rank high-level external payload sources and destinations by observed tool-request messages, with coverage limits stated. Slack DMs contain alerts only. Defaults are a daily report in a new project chat at **6:00 am ET**, chat activity detection every **30 minutes**, and a Friday advisory at **6:00 pm ET**. Thinking/Working duration of **two hours** triggers a long-run advisory; Friday advisories apply regardless of duration. These are activity proxies, not verified processing or cost measurements.

Monitoring covers eligible local Desktop chats among the **50 most recent chats plus pinned chats**. Usage reports read eligible local Desktop logs. Keep personal configuration and generated reports out of Git. HTML report links open locally on the laptop. If the laptop's timezone changes, ask Codex to adjust the schedules to preserve ET timing.

## Validation

After activation, visually check the deployment:

1. **Your settings:** Ask the setup chat to show your saved configuration summary. Confirm your email, Slack workspace/user, selected delivery channels and ET schedules.
2. **Scheduled tasks:** Open **Scheduled** and confirm one active instance of each task below. Open each task to check its project or target chat and next-run time. If the app displays laptop-local time, confirm it corresponds to the ET time shown here. Temporary validation tasks should be paused or removed after testing.

   | Task | Expected schedule | Expected destination |
   | --- | --- | --- |
   | PAIGe - Daily review | Every day, 6:00 am ET | New chat in your PAIGe project; email if selected |
   | PAIGe - Long-run checks | Every 30 minutes | Your designated monitoring chat; Slack DM for new advisories if selected |
   | PAIGe - Friday check | Fridays, 6:00 pm ET | Your designated monitoring chat; Slack DM for new advisories if selected |

3. **Report and delivery:** Open the private report generated during activation. Confirm its ET cutoff and coverage, and that **Open local details** renders the HTML report. Confirm each opted-in test email/DM arrived at your own account with a `PAIGe - ` prefix.
4. **Run results:** After a run, review its status in Scheduled and its report or monitoring record with Codex. Investigate errors or missing outputs in the setup chat. A quiet activity check is normal when no advisory is due; no Slack message alone does not prove the check ran. Confirm any temporary test timings have returned to the schedules above.

## Example and reference

Open the [synthetic HTML report](examples/app/daily-report.html) or [chat summary](examples/app/daily-summary.md). To rebuild the example, run `python scripts/build_demo.py` (`python3` on macOS).

- [Implementation punch list](docs/implementation-punch-list.md)
- [Collector and measurement details](docs/collector.md)
- [Scheduling and delivery](docs/scheduled-pilot.md)
- [Team setup and maintenance](docs/team-setup.md)
- [Timezone troubleshooting](docs/timezone-troubleshooting.md)
- [Data privacy](docs/data-privacy.md)

## Copyright and licensing

Copyright (c) 2026 Oracle.

The project license is undecided; no open-source license is granted by this repository. The [third-party licensing inventory](docs/dependency-license-review.md) is complete; project licensing and organizational clearance remain separate decisions. Installed dependencies and private runtime artifacts are not included.
