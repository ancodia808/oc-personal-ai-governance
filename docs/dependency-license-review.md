# Dependency and licensing review

Review date: 2026-09-29. Scope: current shared working-tree source, skills, templates, synthetic examples and tests; base commit `b0d2924` plus local changes. This is a technical licensing inventory, not organizational legal approval. No private telemetry or recipient data was inspected for publication.

## Result

No third-party Python packages, vendored libraries, remote script dependencies, bundled fonts/images or runtime binaries were found in the current source package. Python imports resolve to standard-library modules or repository modules. HTML uses inline project CSS and system font names, not distributed font files. No third-party license incompatibility was identified for the current source-only design. That finding does not certify authorship or grant rights in PAIGe itself.

The published base still declares `tzdata==2025.2`; its removal is local and must be committed/published before describing the public version as package-free. Earlier Git history retains the declaration but contains no vendored tzdata distribution. Historical ignored installations are outside the source release and are not removed by this review.

## Inventory and obligations

| Component / reviewed version | Relationship to PAIGe | License/source | Assessment and action |
| --- | --- | --- | --- |
| CPython 3.14.5; supported minimum 3.11 | User-installed interpreter and standard library, not bundled | [PSF license and incorporated-software notices](https://docs.python.org/3/license.html); installed 3.14.5 LICENSE.txt also inspected | Permits commercial/internal use under its terms. No requirement identified to license this independent source under GPL. If distributing Python, retain its license, copyright and incorporated-component notices; review that exact distribution separately. |
| SQLite 3.50.4 | Included in the inspected Python runtime, used through sqlite3; not bundled by PAIGe | [SQLite public-domain dedication](https://www.sqlite.org/copyright.html) | No SQLite attribution requirement identified for this source package. Vendor runtime notices remain with the runtime; jurisdiction-specific public-domain questions belong to organizational review. |
| Git for Windows 2.55.0.windows.3 | Installed executable invoked for repository/privacy checks; not linked or bundled | [Exact-version COPYING](https://github.com/git-for-windows/git/blob/v2.55.0.windows.3/COPYING), GPL v2 with upstream licensing qualifications | Executing Git does not by itself make PAIGe a Git derivative. If a future installer redistributes Git, review its full distribution, notices and corresponding-source obligations. Do not assume this review covers bundling Git. |
| Windows timezone APIs | Installed OS facilities accessed through ctypes; no DLLs/SDK headers shipped | OS license; [documented API](https://learn.microsoft.com/en-us/windows/win32/api/timezoneapi/nf-timezoneapi-gettimezoneinformationforyear) | Uses the licensed workstation's APIs. No Microsoft implementation copied or redistributed was identified. Python structure declarations describe the API interface. Documentation links do not transfer a license to PAIGe. |
| macOS system timezone database | Read from the installed OS; not bundled; exact OS/data release not inspected | [IANA timezone license](https://data.iana.org/time-zones/tzdb/LICENSE) describes upstream data as public domain, with named code exceptions | No timezone data is distributed in this package. macOS vendor notices/version remain unverified until that environment is reviewed. Reassess if copying timezone files into a release. |
| tzdata 2025.2 (historical dependency) | Required by published base, removed from current requirements and runtime imports | [Exact-version license](https://raw.githubusercontent.com/python/tzdata/2025.2/LICENSE), Apache-2.0; [full license](https://raw.githubusercontent.com/python/tzdata/2025.2/licenses/LICENSE_APACHE); IANA data above | No commercial-use prohibition identified. Merely declaring the dependency is not bundling it. If redistributed, include Apache license and applicable notices, retain attribution, identify modifications and preserve any applicable NOTICE. Publish the removal to align public setup with the current implementation. |
| HTML/CSS, synthetic JSON, project skills and Python source | Repository-authored artifacts | PAIGe license undecided | No externally sourced asset or copied implementation was identified in the inspected files and creation history. This is not a comprehensive code-similarity/provenance certification. No font, image or JavaScript notices identified as necessary. |
| Codex, Slack, Outlook, GitHub and operating system | Separately supplied apps/services; connectors invoked by skills | Applicable vendor/customer agreements | Not distributed by this repository. Installed versions, account entitlements and employer agreements vary and are outside this source-license inventory. Verify authorized use through existing organizational processes, privately. |

The inspected Python distribution can itself contain components under other licenses (for example libraries supporting ctypes). This repository does not distribute that runtime or those components. A future executable, container or bundled installer needs a new transitive inventory; the source-only findings cannot be reused as runtime redistribution clearance.

## Release findings

1. **No current bundled-component notice file required by the inventory.** Do not add copied license texts for components we do not ship as though they were part of this source release. Preserve upstream notices in separately installed distributions.
2. **Project license remains undecided by owner instruction.** A public repository is not automatically open source. Obtain a license or other appropriate permission from the rights holder before representing unrestricted reuse/modification/distribution as allowed. GitHub's platform viewing/forking permissions are distinct. See [GitHub licensing guidance](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
3. **Organizational clearance remains separate.** The copyright attribution supplied by the owner is not evidence of internal approval. Keep employer-specific rights, approval and vendor-entitlement assessments private; this review does not claim they have occurred.
4. **Publish the reviewed revision.** The dependency removal and this review are not yet in the published base. Recheck the actual staged release file set before pushing.

## Repeatable review

Before release or after dependency/asset/distribution changes:

- Inventory `git ls-files --cached --others --exclude-standard`, excluding ignored private artifacts; review requirements, import statements (including dynamic imports), executable invocations, asset references and vendored files.
- Compare the actual release against the reviewed manifest in `docs/license-review-manifest.json`. It records hashes of reviewed source/assets, not personal data. Regenerate/review when implementation changes.
- Record exact versions and authoritative license texts for new components; review internal/commercial use, modification, redistribution, notices and copyleft obligations.
- Review provenance of added snippets/assets; absence of an import dependency is not proof of original authorship.
- If bundling runtimes, packages or OS data, inventory their transitive contents and include required notices/source offers. Keep unresolved release/organizational permissions visible rather than treating scanner output as approval.

No license was selected or added for PAIGe during this review. README edits were left untouched.

Release inventory refresh (2026-09-30): reviewed added payload-request parser, renderer changes and synthetic examples. Imports remain standard-library/repository-only; no new bundled assets or third-party packages. The manifest uses UTF-8 content with LF-normalized line endings for cross-platform comparison. Statements above about the published base describe the pre-release b0d2924 revision; this release includes dependency removal.
