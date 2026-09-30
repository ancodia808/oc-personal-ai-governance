# Initial implementation punch list

Maintain this checklist as work completes. A checked item requires working artifacts and validation; configuration does not imply active monitoring.

- [x] Reusable local Codex Desktop collector and initial measurement validation.
  - Account/origin filtering; per-response deduplication; conflict exclusion; subset accounting; timezone-aware intervals; private output guard; synthetic tests.
  - Local log compatibility remains version-dependent. macOS validation is still pending.
- [x] Reusable HTML/Markdown reporting pipeline using collector output, with coverage and diagnostics.
  - Added ranked payload source/destination request summaries with private aggregation, synthetic preview and tests. Counts are partial requested-access proxies, not confirmed transfers; HTML attachment test sent successfully and mailbox attachment metadata verified on 2026-09-30; recipient opening confirmation remains pending.
  - Deterministic renderer, reconciliation checks, escaped content, private output guard, and current private report regenerated. Report presentation accepted by the pilot owner; macOS execution remains unverified.
- [x] Thinking/Working proxy detection for two-hour and Friday advisories under the revised policy.
  - Structured live-status adapter, elapsed-turn labeling, freshness gating, deduplication keys, synthetic tests, and one live Desktop check complete. See `docs/active-processing.md`. Scheduled monitoring within the recent-50-plus-pinned scope and delivery remain in the scheduling item below.
- [x] Verify Slack identity and perform authorized delivery tests for DM and email.
  - Synthetic Slack DM and email sent successfully; the pilot owner confirmed both arrived. Receipts and recipient identity remain private.
- [x] Enable daily 06:00 Eastern reports, 30-minute checks, and Friday 18:00 Eastern advisories; complete accepted scheduled-operation validation.
  - Accelerated scheduled validation completed: real daily collection/rendering and email connector acceptance; synthetic two-hour and Friday Slack connector acceptance; evaluator and delivery-ledger duplicate suppression. Original failures are retained privately. Timezone package sandbox access was repaired and scheduled retries passed.
  - All three normal schedules are restored and ACTIVE. A subsequent normal 30-minute check completed within the approved recent-50-plus-pinned scope. Completed latest turns on notLoaded chats are now classified as offloaded and non-running; ambiguous observations remain unknown. No real long-running alert was observed.
  - Acceptance: the pilot owner accepted the successful accelerated pre-checks as sufficient and closed this validation item without waiting for normal scheduled events. Normal morning/Friday wall-clock runs, sleep/offline recovery, and sustained operation were not tested; these remain operational limitations rather than acceptance blockers. The pilot owner confirmed receipt of the scheduled email and both Slack test DMs. Earlier 36-test suite passed with elevation; the latest normal-sandbox full-suite attempt had temporary-directory permission errors, while all nine proxy tests passed after the offloaded-classification update. See `docs/scheduled-pilot.md` and `docs/timezone-troubleshooting.md`.
- [x] Package reporting/monitoring skills and document team onboarding, activation, updates, disabling, retention and removal.
  - Concise README interview/activation prompts and visual validation checklist; blank private configuration/readiness templates; reusable onboarding and runtime skills; detailed agent handoff in `docs/team-setup.md`. Includes channel opt-outs, account selection, duplicate-safe schedule updates, timezone conversion and multi-host migration limits.
  - Packaging deliverables complete. Fresh-user laptop and macOS execution are separate unverified platform acceptance checks; documentation does not establish execution evidence. Manual retention is supported; automatic purge is not implemented.
- [x] Complete source-package third-party licensing inventory and technical review.
  - Findings: `docs/dependency-license-review.md`; reviewed artifact hashes: `docs/license-review-manifest.json`. No third-party package or bundled asset incompatibility identified in current source-only implementation. Project license/rights-holder permission and organizational clearance remain unresolved, separate release decisions. This release removes the historical timezone-package dependency.
  - Inventory direct and transitive packages, bundled assets, copied code, and distributed runtimes at their exact versions; no third-party Python runtime packages are currently required; review operating-system/runtime prerequisites and any future additions.
  - Verify license texts and provenance from authoritative package/source distributions. Check commercial/internal use, modification, redistribution, attribution/notice requirements, copyleft obligations, and conflicting or missing license information.
  - Record findings and required notices in a reusable dependency/license inventory. Keep employer-specific policies, legal assessments, and approval records private and out of Git.
  - Resolve issues by replacing/removing dependencies, satisfying applicable obligations, or obtaining the appropriate organizational review. Do not treat an automated scanner result as legal approval.
  - Repeat the review when dependencies, versions, bundled content, or distribution methods change. Track unresolved findings as rollout blockers where applicable.
- [ ] Run a representative baseline pilot, tune useful alerts, and agree a weekly budget.
- [x] Review shareable contents, commit, and publish to the approved public repository: https://github.com/ancodia808/oc-personal-ai-governance.
  - Shared source, skills, documentation and synthetic examples published; private runtime files excluded. Copyright holder: Oracle. Project license remains undecided. All 38 tests passed with elevation before publication.

Model/workflow coaching initially identifies candidates with explicit uncertainty. Comparative validation precedes recommendations to switch defaults. VS Code and browser ChatGPT remain deferred.

Timezone packaging: removed the tzdata dependency. Reporting is fixed to ET with UTC observations and operating-system conversions. Windows validation complete; macOS validation remains open.

Release validation (2026-09-30): all 48 tests passed on Windows. Shared report refinements, attachment delivery, external activity summaries, onboarding and OS timezone support prepared for publication; private data and receipts excluded.
