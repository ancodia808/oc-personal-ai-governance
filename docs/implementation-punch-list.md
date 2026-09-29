# Initial implementation punch list

Maintain this checklist as work completes. A checked item requires working artifacts and validation; configuration does not imply active monitoring.

- [x] Reusable local Codex Desktop collector and initial measurement validation.
  - Account/origin filtering; per-response deduplication; conflict exclusion; subset accounting; timezone-aware intervals; private output guard; synthetic tests.
  - Local log compatibility remains version-dependent. macOS validation is still pending.
- [x] Reusable HTML/Markdown reporting pipeline using collector output, with coverage and diagnostics.
  - Deterministic renderer, reconciliation checks, escaped content, private output guard, and current private report regenerated. Browser visual verification and macOS execution remain pending.
- [x] Thinking/Working proxy detection for two-hour and Friday advisories under the revised policy.
  - Structured live-status adapter, elapsed-turn labeling, freshness gating, deduplication keys, synthetic tests, and one live Desktop check complete. See `docs/active-processing.md`. Scheduled monitoring within the recent-50-plus-pinned scope and delivery remain in the scheduling item below.
- [x] Verify Slack identity and perform authorized delivery tests for DM and email.
  - Synthetic Slack DM and email sent successfully; the pilot owner confirmed both arrived. Receipts and recipient identity remain private.
- [x] Enable daily 06:00 Eastern reports, 30-minute checks, and Friday 18:00 Eastern advisories; complete accepted scheduled-operation validation.
  - Accelerated scheduled validation completed: real daily collection/rendering and email connector acceptance; synthetic two-hour and Friday Slack connector acceptance; evaluator and delivery-ledger duplicate suppression. Original failures are retained privately. Timezone package sandbox access was repaired and scheduled retries passed.
  - All three normal schedules are restored and ACTIVE. A subsequent normal 30-minute check completed within the approved recent-50-plus-pinned scope. Completed latest turns on notLoaded chats are now classified as offloaded and non-running; ambiguous observations remain unknown. No real long-running alert was observed.
  - Acceptance: the pilot owner accepted the successful accelerated pre-checks as sufficient and closed this validation item without waiting for normal scheduled events. Normal morning/Friday wall-clock runs, sleep/offline recovery, and sustained operation were not tested; these remain operational limitations rather than acceptance blockers. The pilot owner confirmed receipt of the scheduled email and both Slack test DMs. Earlier 36-test suite passed with elevation; the latest normal-sandbox full-suite attempt had temporary-directory permission errors, while all nine proxy tests passed after the offloaded-classification update. See `docs/scheduled-pilot.md` and `docs/timezone-troubleshooting.md`.
- [ ] Package reporting/monitoring skills and complete Windows/macOS onboarding, updates, disabling, retention, and deletion workflows.
- [ ] Review third-party dependency licenses for intended enterprise use before team rollout or distribution.
  - Inventory direct and transitive packages, bundled assets, copied code, and distributed runtimes at their exact versions; include the timezone-data package in `requirements.txt`.
  - Verify license texts and provenance from authoritative package/source distributions. Check commercial/internal use, modification, redistribution, attribution/notice requirements, copyleft obligations, and conflicting or missing license information.
  - Record findings and required notices in a reusable dependency/license inventory. Keep employer-specific policies, legal assessments, and approval records private and out of Git.
  - Resolve issues by replacing/removing dependencies, satisfying applicable obligations, or obtaining the appropriate organizational review. Do not treat an automated scanner result as legal approval.
  - Repeat the review when dependencies, versions, bundled content, or distribution methods change. Track unresolved findings as rollout blockers where applicable.
- [ ] Run a representative baseline pilot, tune useful alerts, and agree a weekly budget.
- [ ] Review shareable contents, commit, and publish only to an approved GitHub destination.

Model/workflow coaching initially identifies candidates with explicit uncertainty. Comparative validation precedes recommendations to switch defaults. VS Code and browser ChatGPT remain deferred.
