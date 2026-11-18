# Aedis Skills

Agent skills for building with Aedis: when to use the CLI and the MCP server, the rules agents follow, and the security rules for each sink. Each skill is plain text.

| Skill | For |
| --- | --- |
| [`aedis-ui`](skills/aedis-ui/SKILL.md) | React interfaces with Aedis UI: finding and installing items, and the rules for agent and user content. |

## Install

Install from a release, never from `main`. Take the tag from [Releases](https://github.com/aedis-build/aedis-skills/releases), verify it, then copy the skill. For Claude Code, in the project:

```bash
tag=vX.Y.Z
gh release verify "$tag" -R aedis-build/aedis-skills \
  && d="$(mktemp -d)" \
  && git clone --quiet --depth 1 --branch "$tag" https://github.com/aedis-build/aedis-skills "$d" \
  && mkdir -p .claude/skills \
  && cp -R "$d/skills/aedis-ui" .claude/skills/ \
  && rm -rf "$d"
```

Releases are immutable and attested by GitHub: `gh release verify` fails for a tag that was moved or a release that was changed. Other agents that read `SKILL.md` folders take the same folder in their own skills directory.

## What keeps the skills safe to load

- Text only: `test/check.py` refuses scripts, executables, symlinks, `` !`command` `` lines (which a skill would run when it loads) and any frontmatter key besides `name` and `description`, so a skill never grants a tool permission, adds a hook or runs a command. It also refuses agent configuration anywhere in the repository (`.claude/`, `.mcp.json`, `CLAUDE.md`, `AGENTS.md`).
- The rules block in `aedis-ui` must equal the rules Aedis UI publishes at https://ui.aedis.build/docs.json. CI checks it on every pull request and daily.
- Every change to the skills, the check, CI or this README needs review from platform security. See [SECURITY.md](SECURITY.md).
