# Windows sandbox setup: helper_sandbox_lock_failed

Use this procedure only when troubleshooting the matching Windows setup failure. It is not a routine prerequisite or an action to perform during scheduled governance checks. Keep actual diagnostic logs, account names and machine details private.

## Recognize the failure

Codex reports `sandbox provisioning failed` before Python or the requested shell command starts. The private setup error identifies:

```text
helper_sandbox_lock_failed
lock sandbox bin dir ...\.codex\.sandbox-bin failed: open directory ...
```

In the confirmed case, sandbox-user and firewall setup succeeded. Process Monitor showed `codex-windows-sandbox-setup.exe`, running as `NT AUTHORITY\SYSTEM`, receiving `ACCESS DENIED` on `.sandbox-bin`. The requested access was `Read Control, Write DAC`; sharing allowed Read, Write and Delete. SYSTEM had Modify permission but lacked Write DAC. This was an ACL access failure, not evidence of another process holding an incompatible lock. Being able to list the directory as the signed-in user did not establish the helper's access.

## Verify settings and evidence

In the existing user configuration `%USERPROFILE%\.codex\config.toml`, confirm:

```toml
# Top-level setting, before any [section].
sandbox_mode = "workspace-write"

[windows]
sandbox = "elevated"
```

Preserve other configuration and avoid duplicate sections. Save, fully quit and reopen Codex, and complete any required administrator-approved sandbox setup. Elevated refers to the sandbox implementation; sandboxed commands still run under restricted users. Full-access mode is not required. A separate error mentioning the **unelevated restricted-token sandbox** and **split writable root sets** means the selected implementation must be checked first.

Run these read-only checks in the affected user's PowerShell:

```powershell
$sandbox = Join-Path $env:USERPROFILE '.codex\.sandbox'
$bin = Join-Path $env:USERPROFILE '.codex\.sandbox-bin'

Get-Item -LiteralPath "$sandbox\setup_error.json" | Select-Object LastWriteTime
Get-Content -LiteralPath "$sandbox\setup_error.json"
Get-ChildItem -LiteralPath $sandbox -Filter '*.log' |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 3 Name, LastWriteTime

Get-Item -LiteralPath $bin -Force |
    Format-List FullName, Attributes, LinkType, Target
Get-Acl -LiteralPath $bin |
    Format-List Owner, AccessToString, AreAccessRulesProtected
icacls.exe "$bin"
```

Read the most recent setup log, not a historical attempt. If the generic message does not expose the cause, use an approved Process Monitor installation: filter Path containing `.sandbox-bin`, capture one normal sandbox attempt, and stop capture. Inspect the failed operation's Result, Desired Access and Process tab (executable, user and integrity). Do not assume this repair applies to missing paths, sharing violations, a different process identity, explicit denies or unrelated security-control failures.

## Apply the narrowly scoped repair

For the confirmed combination above, grant SYSTEM the missing **Write DAC** right on this directory only. Run as the affected user with permission to change this ACL; use administrator/IT assistance if that operation is denied. The original case's owner already had Change Permissions.

```powershell
$bin = Join-Path $env:USERPROFILE '.codex\.sandbox-bin'
$backup = Join-Path $env:USERPROFILE ("sandbox-bin-acl-before-{0}.txt" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))

icacls.exe "$bin" /save "$backup"
if ($LASTEXITCODE -ne 0) { throw 'ACL backup failed; no permissions changed' }

icacls.exe "$bin" /grant '*S-1-5-18:(WDAC)'
if ($LASTEXITCODE -ne 0) { throw 'SYSTEM Write DAC grant failed' }

icacls.exe "$bin"
Write-Output "ACL backup: $backup"
```

`S-1-5-18` identifies SYSTEM; `WDAC` permits changing the directory's discretionary ACL. `/grant` without `:r` adds to existing permissions. There is no `/T` or inheritance flag: this adds the right to the directory itself, without recursively granting it to child files. It does not change ownership, grant Full Control, or grant additional rights to CodexSandboxUsers. Preserve the printed backup path outside Git.

If rollback is required, restore the saved DACL from its parent directory. This restores the directory permissions captured in that backup; it can undo subsequent ACL changes and reintroduce the setup failure. In the same PowerShell session:

```powershell
icacls.exe (Split-Path -Parent $bin) /restore "$backup"
if ($LASTEXITCODE -ne 0) { throw 'ACL restore failed' }
```

In a new session, set `$bin` and `$backup` to the original directory and exact saved backup first. Do not delete `.sandbox-bin`, reset its entire ACL or modify endpoint protection as part of this procedure.

## Verify the repair

Ask Codex to run `whoami` using **normal sandbox permissions**, without an escalation override. In the validated configuration it ran as `CodexSandboxOffline`. Then verify a private file write/read and a SQLite transaction under the project's ignored `private/` folder. Run `python -B scripts/offline_monitor.py` without `--queue` to validate collection and private output without sending an alert.

Finally verify an actual scheduled run can collect, claim an eligible digest, send through the configured connector and save its immediate receipt. A successful interactive or escalated command alone does not prove scheduled execution. If the scheduled run is read-only, resolve its project write access separately; this ACL repair does not change the schedule's filesystem scope.

Validation on October 1, 2026: normal sandbox execution, private file/SQLite writes and offline detection succeeded after the SYSTEM Write DAC grant. A subsequent scheduled run delivered a consolidated digest and saved its receipt; two later checks remained quiet with final notices retired. These observations establish the repair for that Windows deployment, not a universal fix. No macOS change is involved.

References: [OpenAI Windows sandbox guidance](https://learn.chatgpt.com/docs/windows/windows-sandbox), [Microsoft icacls reference](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls).
