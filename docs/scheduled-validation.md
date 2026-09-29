# Scheduled-operation acceptance test

Use a short, explicitly authorized test window to exercise the existing schedules. Save original automation settings and run-specific instructions in ignored private storage before changing anything. Keep production alert thresholds unchanged.

1. Stagger daily reporting, long-run monitoring and Friday monitoring so each has time to finish. Schedule a follow-up audit. Keep the app and computer available throughout the test.
2. Have each run restore its own original schedule through the app automation tool before testing. Give test sends an expiry and distinct durable ledger keys so delayed runs do not send stale tests or suppress production reports.
3. Generate a real daily report and send it to the configured private email recipient with a clearly labeled test subject. Preserve its HTML and summary privately.
4. Exercise live inventory and status collection for both monitoring schedules. Independently evaluate synthetic two-hour and Friday cases through the production evaluator; clearly label resulting test DMs as synthetic. Do not change live timestamps to force an alert.
5. After successful delivery, verify a second claim of the same delivery key denies another send. Check evaluator suppression with delivered keys too. Never resend merely to prove deduplication.
6. Record actual start/end times, coverage gaps, evaluator results, connector receipts, duplicate suppression and restoration status privately. Distinguish scheduler invocation, workflow completion, connector acceptance and user-confirmed receipt.
7. Audit all results and saved schedules, restore any remaining temporary settings, and pause the test follow-up. Report missing or incomplete runs honestly. Update the punch list only for evidenced outcomes.

An accelerated test does not establish sleep/offline recovery, the normal Friday wall-clock trigger, macOS compatibility, or continuous operation. Validate those separately. No actual usage data, recipient details, scheduler exports or run receipts belong in Git.
