# Windows timezone dependency access

Scheduled collection and advisory evaluation require the pinned `tzdata` package on Windows. Set `PYTHONPATH` to the existing `private/python-deps` directory and verify `ZoneInfo('America/New_York')` in a normal sandbox command before enabling schedules.

A package can be complete yet unreadable to the sandbox. In the pilot, its protected ACL allowed only the owner, SYSTEM and administrators; Python reported a missing timezone rather than the underlying directory access denial. Confirm directory access and compare a normal import with an authorized elevated diagnostic before reinstalling.

The scoped repair grants the local Codex sandbox group read/execute access to the installed `private/python-deps/tzdata` tree only. This permission change requires authorized elevation. Do not broaden permissions on private reports, recipient configuration or the repository. Recheck package access after reinstalling or updating dependencies.

Validate without elevation: winter Eastern offset is UTC-5, summer is UTC-4, the two-hour and Friday proxy cases trigger correctly, and delivered keys suppress repeat advisories. Then repeat scheduled delivery validation; an interactive check alone does not prove scheduled delivery.

The test suite's temporary-directory permission errors are a separate Windows sandbox issue. Do not classify those as timezone failures or weaken private-data permissions to make them pass.
