# Data privacy standard

Collected data is user-specific and private. Never commit it to Git, including a private repository. This rule also covers derived or redacted data: aggregates, account capability results, coaching based on real activity, reports, logs, caches, app state, generated charts, screenshots, exports, and backups.

## Storage and presentation

- Default runtime storage to a per-user application directory outside the checkout. Keep each consultant's sources, configuration, and outputs separate.
- If temporary outputs must live in the checkout, use ignored directories such as `private/`, `data/`, `reports/`, `runtime/`, or `outputs/`. Never force-add these artifacts.
- Apps and visualizations load private data at runtime. Do not embed it in source, static builds, notebooks, demo pages, or deployment bundles. Local presentation is the default; external hosting or sharing requires explicit authorization.
- Collect only necessary fields. Keep credentials and prompt bodies out of diagnostic output. Document retention and deletion controls when storage is implemented; Git exclusion alone does not provide access control or encryption.

## Shareable repository contents

Commit reusable skills, code, schemas, processes, standards, empty templates, and wholly synthetic datasets or presentations. Synthetic examples must be invented independently of collected records and clearly labeled. Redaction or aggregation does not make collected data eligible for Git.

Include representative synthetic data and reference app artifacts when they help the team reproduce results and presentation. These may include populated demo reports, charts, static demo pages, UI screenshots, and visual baselines generated exclusively from synthetic fixtures. Keep them under explicitly shareable paths such as `examples/fixtures/`, `examples/reports/`, `examples/app/`, and `tests/visual-baselines/`.

Label each example as synthetic and record its fixture, configuration, generation command, and relevant tool versions. Use fixed seeds, timestamps, and locale settings where needed for repeatable output. Example builds must run without access to private runtime storage. Compare calculated results and stable visual features against these references; document intentional updates alongside changes to code and standards.

## Maintenance and verification

Skills and app commands must route private outputs to the designated storage location. Tests and CI use synthetic fixtures. Before staging or publishing, inspect the file list and contents for embedded user data; `.gitignore` does not protect already tracked files or data copied into documentation. Do not include real usage evidence in commit messages, issues, or pull request descriptions.

If collected data is accidentally staged, unstage it and move it to private storage before committing. If it has entered Git history or been published, stop further publication and assess remediation with the user; merely adding an ignore rule does not remove historical data.

## Sole-source and network boundary

Governance evidence comes exclusively from ChatGPT/Codex records and status tools, within the supported Desktop scope. Runtime must not access the external sources/destinations observed in those records or query other services for enrichment or verification. Only configured email report delivery and triggered Slack DMs are permitted external runtime traffic; their immediate send responses and local receipts provide delivery evidence. Unknowns remain unknown. See `AGENTS.md` for the complete hard rules.
