# Operating-system Eastern timezone rules

PAIGe has no third-party Python runtime dependencies. Run `python scripts/eastern_time.py` (macOS: `python3`) inside the normal Codex sandbox. It must print an offset-aware timestamp labelled ET.

Windows reads the Eastern Standard Time zone through native Windows APIs, including year-specific daylight-saving rules. macOS reads America/New_York from the system IANA timezone database. Neither path falls back to a Python tzdata package or a hardcoded UTC offset. Keep OS updates current through approved corporate processes. Missing or inaccessible OS timezone rules are a setup failure; repair the OS environment rather than guessing an offset.

Report dates, daily/weekly boundaries and advisory evaluation use ET. Machine-readable source/observation timestamps stay UTC; user-facing timestamps explicitly say ET. The laptop's host timezone still matters to the app scheduler: verify the displayed next-run times after travel or host timezone changes.

Older checkouts installed tzdata under ignored private/python-deps and needed a scoped permission repair. This version does not use that installation or require PYTHONPATH. Existing ignored package files may remain; no private data is deleted during migration. Historical validation receipts retain the original failure evidence.

Windows tests cover winter/summer offsets, both DST transitions, fold/gap handling, year rollover, a historical rule and weekly boundaries. macOS execution remains unverified. Sandbox temporary-directory test errors are separate from timezone access.

References: [Windows year-specific rules](https://learn.microsoft.com/en-us/windows/win32/api/timezoneapi/nf-timezoneapi-gettimezoneinformationforyear), [Python timezone support](https://docs.python.org/3/library/zoneinfo.html).
