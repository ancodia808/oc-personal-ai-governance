# Proposed implementation plan

## Repository implementation standard

Use project-specific Codex skills for repeatable procedures when appropriate, backed by executable repository artifacts. The repository is the source of truth for instructions, processes, standards, and implementation. Chat discussions should result in durable updates when they establish an accepted rule.

Proposed structure (to be created as the corresponding capability is implemented):

| Location | Responsibility |
| --- | --- |
| `AGENTS.md` | Concise project conventions, validation commands, and pointers to shared standards |
| `.agents/skills/` | Project skills for telemetry assessment, usage reporting/coaching, and validation; each defines prerequisites, inputs, procedure, outputs, and failure handling |
| `src/` and `scripts/` | Collector, deterministic calculations, report generation, and repeatable entry points invoked by skills |
| `app/` | Optional local interface if it materially improves inspection; uses the same calculation and policy implementation |
| `schemas/` and `config/` | Versioned data/report contracts and shared policy examples; explicit, validated personal overrides |
| `tests/fixtures/` and `examples/` | Versioned synthetic datasets, expected metrics, populated sample reports, and reference app/chart artifacts |
| `tests/visual-baselines/` | Reference screenshots generated exclusively from synthetic fixtures for presentation checks |
| `docs/` | Standards, setup, operating procedures, architecture decisions, and change history |
| Per-user storage outside the checkout | Collected data, private configuration, reports, app state, and generated visualizations; excluded from Git |

Keep formulas and validation logic in one tested implementation. Skills call it rather than recomputing results conversationally. Version schema and policy changes, document migrations, and record tool version, policy version, source coverage, and report cutoff with each result. A fresh checkout should support a documented fixture-based demonstration without personal account access.

Provide a reproducible demo build using only synthetic fixtures and example configuration. Commit useful reference app artifacts alongside expected numeric results so consultants can compare layout, labels, coverage indicators, and coaching structure. Include ordinary usage, threshold crossings, and missing-data examples. Record generation commands and versions, fix nondeterministic inputs where practical, and review baseline updates with implementation changes. Demo builds must not read private runtime storage.

Maintain skills, code, schemas, and examples together through reviewed changes. Evaluate skills against representative scenarios for required evidence, missing-data behavior, and output structure; test numeric results exactly. Pin implementation dependencies and record model/settings where available for coaching reproducibility, without promising identical generated prose. If a workflow cannot be expressed reliably as a skill, document the reason and keep its replacement in the repository.

Project-specific skills package the shared workflow; they do not by themselves provide account-wide telemetry or access to teammates' accounts. Each consultant runs against their own authorized sources and private configuration.

## 1. Validate telemetry and coverage

Inventory supported account usage snapshots and accessible session telemetry without collecting prompt bodies. Establish whether per-turn input, cached input, output, model, timestamps, and stable event identifiers are available. Record host/source coverage and distinguish local, remote, and cloud activity. Do not assume this desktop tool is callable from a standalone scheduled script.

Deliverable: a private capability assessment and sample records; commit only a blank capability-matrix template and wholly synthetic examples. If account-wide token coverage cannot be established, offer a clearly labeled observed-usage pilot plus account allowance snapshots when available. Never present partial local totals as account-wide totals.

Package the verified assessment procedure as a project skill with a capability-matrix template and explicit unsupported-source outcomes.

## 2. Build a local ledger and baseline

Use a small local collector and SQLite ledger, with configurable adapters and a human-readable policy file. Record source, observation time, event/turn ID, pseudonymous chat/project identifiers, model, execution duration if known, token categories, window/reset metadata, and coverage status. Keep raw prompts, credentials, and account identifiers out of Git.

Default all collected and derived data to per-user storage outside the checkout. Any temporary in-checkout outputs must use ignored private directories. Apply the [data privacy standard](data-privacy.md) to collectors, skills, apps, visualization builds, logs, and exports. Do not embed real data in committed HTML, JavaScript, notebooks, screenshots, or test fixtures.

Normalize cumulative counters into deltas only within a proven counter scope; deduplicate repeated events and resumed sessions. Validate whether cached input is a subset of input and reasoning is a subset of output before aggregation. Never add subsets twice. Keep allowance buckets separate; do not sum overlapping account snapshots. Track resets and missing observations explicitly.

Collect seven complete days before suggesting a token budget from observed demand, with the user's desired reserve/reduction shown separately. Mark atypical or incomplete weeks. Include the monitor's own measurable usage in totals.

Deliverable: baseline summary and numeric budget proposal for confirmation.

## 3. Calculate pace and generate an on-demand report

For weekly budget B and measured week-to-date usage U, let f be elapsed seconds divided by actual seconds in the configured local calendar week (including daylight-saving changes). Expected usage E = B × f; deviation = U − E; remaining = B − U. Daily soft allocation follows the same elapsed-time rule. Negative remaining indicates an overrun.

After at least one complete day and only with adequate coverage, project P = U / f. Label this a uniform-usage projection, not a forecast of work demand. Suppress budget comparisons when B is unset; suppress projections across collection gaps. Compute report-to-report deltas only inside the same week and unit. Show account allowance windows separately using their own reset boundaries.

Generate Markdown reports locally with coverage, pace, threshold crossings, and up to three coaching suggestions. Compare a suggested cheaper workflow with a comparable task's quality and completion time before endorsing it. Do not infer active runtime from chat age.

Deliverable: an on-demand report demonstrated with synthetic fixtures and any verified observations.

Expose one documented command for report generation and a project skill that runs it, checks coverage, and adds evidence-based coaching using the shared report contract.

## 4. Verify, confirm, and activate

Implement the confirmed two-hour active-processing advisory and Friday-evening active-processing warning independently of token-budget availability. Friday warnings apply regardless of run duration. Check every 30 minutes; deliver warnings by Slack DM to the affected member. Support an additional Outlook daily email. Follow the [notification design](notification-design.md) for private recipient setup, message content, deduplication, and verification. Exact Friday time and repeat-warning behavior remain to be finalized before activation. Test immediately below and at two hours, known waiting intervals, and Friday processing under two hours. Neither trigger authorizes automatic interruption.

Add synthetic scenarios for a Friday run still processing on Saturday, processing continuing through Sunday, a task waiting for approval all weekend, and stale/missing execution telemetry. Calculate execution overlap with configured weekend boundaries in the team member's timezone; do not infer continuous processing from two distant status observations. Keep known usage and unknown intervals separate, and avoid double counting runs across daily reports or weekly resets. Prioritize weekend-running findings within the daily report's three-finding limit. Design optional more frequent checks separately from the daily morning report; advisory only unless the user changes that policy explicitly.

Test meaningful failure cases: duplicate events, cumulative-counter resets, week and daylight-saving boundaries, missing/null windows, partial coverage, unavailable budget, overlapping allowance buckets, and cached-token double counting. Verify coaching distinguishes observed evidence from hypotheses and waiting time from execution.

Verify output paths resolve to private storage, app builds contain no collected data, and the staged file list excludes private outputs. Use synthetic fixtures for CI and skill evaluations. Git ignore rules are a fallback, not a substitute for reviewing staged contents.

Present a concrete sample report and final policy for confirmation of thresholds, cadence, and destination. Only then configure a supported scheduler. A daily report is explicitly requested; additional notifications should occur only on meaningful new deviations, failures, or required user action. Deduplicate repeated warnings. A daily scan cannot guarantee immediate detection of a long-running turn; continuous monitoring would require a separate design and approval.

Deliverable: approved policy, tested schedule, and a documented disable procedure. If telemetry is unavailable, deliver an honest coverage report rather than fabricated usage.

## 5. Prepare GitHub and team sharing

Keep code, documentation, synthetic fixtures, and policy examples under version control; exclude runtime databases, real reports, secrets, and identifying metadata. Add setup instructions, telemetry limitations, and a redaction checklist. Review a sanitized diff before proposing the initial commit and external publication. Confirm GitHub destination/visibility and intended audience before creating or pushing a remote repository or sending messages.

Include project skills and a consultant onboarding walkthrough. Validate the walkthrough from a fresh checkout using synthetic data, then document connecting an individual's authorized sources and applying personal policy overrides. Shared fixtures and acceptance criteria serve as the team's consistency check. Team sharing covers the implementation and standards; sharing individual usage records requires a separate explicit decision.

## Suggested backlog

1. Repository conventions, telemetry capability matrix, source contract, and assessment skill.
2. Ledger schema, adapter, deduplication, and coverage accounting.
3. Policy configuration, pace calculations, and fixture tests.
4. Report renderer, reporting skill, and evidence-based coaching rules with shared acceptance scenarios.
5. Seven-day pilot and confirmed budget.
6. Approved daily reporting, skill validation workflow, and sanitized GitHub starter kit with consultant onboarding.

The first synthetic prototype is implemented: a fixed fixture, deterministic report generator, concise Markdown summary, self-contained HTML report, and numeric/input checks. Project skill packaging, telemetry discovery, private storage, automatic coaching, and scheduling remain to be implemented. See [confirmed interview decisions](design-decisions.md) for the agreed user experience. No numeric budget, notification schedule, or publication destination has been approved.
