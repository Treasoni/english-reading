---
name: security-secret-audit
description: Audit a Git repository for exposed API keys, tokens, passwords, private keys, and other credentials without printing their values. Use when asked to check repository security, scan for leaked secrets, review files before committing or pushing, investigate a credential leak, or check Git history after a possible exposure.
---

# Security Secret Audit

Run the bundled scanner before a commit and whenever a credential leak is suspected. Treat every finding as sensitive: do not paste the matched value into messages, issues, commits, or logs.

## Workflow

1. Read the repository instructions, `.gitignore`, and `git status --short`.
2. Scan the relevant scope:

```bash
# Current tracked and non-ignored files; default mode.
.claude/skills/security-secret-audit/scripts/audit-secrets.sh

# Only the staged content; use immediately before committing.
.claude/skills/security-secret-audit/scripts/audit-secrets.sh --staged

# Every unique file version reachable from Git history; use after a suspected past leak.
.claude/skills/security-secret-audit/scripts/audit-secrets.sh --history
```

3. Report findings by file, line, rule name, and scope only. Never reveal the credential value.
4. For a current-file finding, remove the secret from tracked content, move it to an ignored local configuration file, and add a sanitized example when configuration documentation is needed.
5. For a history finding, revoke or rotate the credential first. Then explain that deleting the current file is insufficient and rewrite history only with explicit user authorization.
6. Re-run the same scan after remediation. A clean scan is required before staging or committing.

## Scanner Contract

- Exit `0`: no findings.
- Exit `2`: potential credential found; stop the commit or push.
- Exit `1`: scanner error; treat it as a failed security check and investigate before proceeding.
- Output is intentionally redacted to `scope:path:line:rule`; the scanner never prints matched content. Provider-specific formats, private keys, and JWTs are scanned in all text files; lower-confidence variable-name checks are limited to configuration-like files to avoid generated-code noise.

## Limitations

The bundled patterns are a high-signal baseline, not proof that a repository is secret-free. When a remote, CI system, or package ecosystem is available, add a maintained secret scanner there as an additional independent control. Do not add real credentials to allowlists; rotate false-positive-looking credentials only after confirming ownership and validity.
