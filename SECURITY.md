# Security policy

## Supported versions

One major at a time: the current one. Install the skills from a release tag (`vX.Y.Z`), never from `main` or a moving
branch, so what your agent loads is the reviewed, attested text of that release.

## Reporting a vulnerability

Use **Report a vulnerability** in this repository's Security tab (GitHub Private Vulnerability Reporting). Do not open a public issue for vulnerabilities.

- Acknowledgement within 3 business days.
- Initial severity assessment (CVSS) within 7 days.
- Fix or documented mitigation for high/critical severity within 30 days.
- Credit to the reporter in the advisory, if desired.

## Scope

The skills under `skills/`: text an agent loads and follows. A skill that tells an agent to weaken a defense, run a
command, fetch from an unexpected origin or skip a confirmation is a vulnerability here. Aedis UI itself is covered by
[aedis-build/aedis-ui](https://github.com/aedis-build/aedis-ui/security/policy); the Aedis Platform reusable workflows
this repository calls by [aedis-build/aedis-platform](https://github.com/aedis-build/aedis-platform/security/policy).

## Practices of this repository

- Skills are text only. `test/check.py` refuses scripts, executables, symlinks, `` !`command` `` lines and any
  frontmatter key besides `name` and `description` (no `allowed-tools`, no hooks), so installing a skill never grants
  a permission or runs code. Agent configuration (`.claude/`, `.mcp.json`, `CLAUDE.md`, `AGENTS.md`) is refused
  anywhere in the repository.
- The rules in the `aedis-ui` skill must equal the ones Aedis UI publishes; CI fails on any difference and runs daily.
- Every change to `skills/`, the check, CI and the README needs review from platform security. Every action and
  reusable workflow is pinned by commit SHA, and so is the platform checkout inside the reusables (`platform-ref`);
  `permissions: {}` is the default.
- Releases are immutable and attested by GitHub, and release tags cannot be moved or deleted; verify with
  `gh release verify <tag> -R aedis-build/aedis-skills` before installing.
- Dependencies updated by Dependabot; OpenSSF Scorecard published.
