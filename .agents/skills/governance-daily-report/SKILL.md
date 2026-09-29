---
name: governance-daily-report
description: Generate and deliver the configured personal Codex Desktop daily usage report in an authorized scheduled project chat. Uses private configuration and delivery receipts.
---

Work from the repository root. Read `private/pilot.local.json`, `private/collector.local.json`, and `docs/collector.md`. Stop without sending if delivery_enabled is false. No real data goes into versioned files. Do not install dependencies or modify source during a scheduled run.

Use Python with the existing timezone dependency. For this pilot, add `private/python-deps` to PYTHONPATH if needed. Respect sandbox permissions; record a failure if execution cannot proceed. Do not silently change permissions or invent usage. Configuration account identity, recipient, and scheduled authorization must exist.

1. Determine today's date and current time in the configured timezone. Do not send before 06:00. If delayed, label the actual cutoff and delay. Generate only today's report; do not flood the recipient with backfilled missed days.
2. Run `scripts/collect_usage.py --config private/collector.local.json --output private/usage-snapshot.json`, then `scripts/render_review.py --input private/usage-snapshot.json --output-dir private/reports/YYYY-MM-DD` using today's configured-zone date. Use fixed dated paths so later reports do not overwrite previously linked details. Review diagnostics and surface gaps; never imply account-wide coverage. Preserve the generated summary's maximum three findings.
3. Discover the Outlook Email send tool. Send the concise plain-text summary only to daily_report.email in private configuration, with subject `PAIGe - Daily usage review - YYYY-MM-DD`. No CC/BCC or attachments. Explain that HTML details are in the project chat rather than embedding unusable local-file links in email. Do not include prompt excerpts.
4. Before sending, claim the key `daily-email|YYYY-MM-DD|RECIPIENT` with `scripts/delivery_ledger.py claim --key ...`. Send only when send_allowed is true. Use safely quoted arguments; do not print configuration. Immediately after tool-confirmed success, call `complete` with the same key and a receipt recording the successful send response. If sending fails or its outcome is ambiguous, leave pending and report the failure; do not retry blindly. Existing sent/pending claims prevent duplicate sends.
5. Return the concise report in this scheduled run's chat with an absolute local HTML link, coverage, and email send outcome. The automation already creates this chat; do not create another. Reference this skill when reporting connector sends. Do not assert inbox receipt.

No model analysis of raw logs is necessary. Use deterministic scripts, do not read other chats or search external sources for coaching. Unknown processing and unset budget remain unavailable. Failures should identify the blocked step without exposing private data outside the configured channels.
