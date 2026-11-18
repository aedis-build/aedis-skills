"""Checks the repository: skills are text only (no script, executable, symlink, shell injection or frontmatter key
besides name and description), no agent configuration anywhere, and the rules in the aedis-ui skill equal to the ones
Aedis UI publishes in docs.json. Exit 1 with one line per problem."""

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_URL = "https://ui.aedis.build/docs.json"
DOCS_MAX_BYTES = 5_000_000
START, END = "<!-- aedis-ui-rules:start -->", "<!-- aedis-ui-rules:end -->"
# What a skill may contain: text the agent reads. Anything that runs or configures the agent is refused.
TEXT_EXTENSIONS = {".md", ".txt"}
# Keys like allowed-tools would grant permissions when the skill loads; only these two are allowed.
FRONTMATTER_KEYS = {"name", "description"}
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# `!` followed by a backticked command runs in the shell when Claude Code loads the skill.
SHELL_INJECTION = re.compile(r"!`")
# Files that configure an agent opening this repository (hooks, MCP servers, instructions); none belong here.
AGENT_CONFIG = re.compile(
    r"(^|/)(\.claude|\.claude-plugin|\.cursor|\.codex|\.gemini)/|(^|/)(\.mcp\.json|CLAUDE\.md|AGENTS\.md|GEMINI\.md|\.cursorrules)$"
)
REGULAR, EXECUTABLE = "100644", "100755"


def tracked_files(root):
    """Path -> git mode, from the index (what CI checks out), not from the disk."""
    out = subprocess.run(["git", "ls-files", "-s", "-z"], cwd=root, check=True, capture_output=True).stdout
    files = {}
    for entry in out.decode().split("\0"):
        if entry:
            meta, path = entry.split("\t", 1)
            files[path] = meta.split()[0]
    return files


def frontmatter(text):
    """The `key: value` lines between the opening and closing `---`, or None when there is no frontmatter."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, sep, value = line.partition(":")
        if not sep or not key.strip() or key != key.strip() or key in fields:
            fields.setdefault("", []).append(line)  # refused below: multiline, comment, blank, nested or repeated
            continue
        fields[key] = value.strip()
    return None


def read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def skill_problems(root, files):
    problems = []
    for f, mode in sorted(files.items()):
        if AGENT_CONFIG.search(f):
            problems.append(f"{f}: agent configuration is not allowed in this repository")
        if not f.startswith("skills/"):
            continue
        if mode != REGULAR:
            kind = "executable files" if mode == EXECUTABLE else "symlinks and submodules"
            problems.append(f"{f}: {kind} are not allowed in a skill")
        elif os.path.splitext(f)[1].lower() not in TEXT_EXTENSIONS:
            problems.append(f"{f}: only .md and .txt files are allowed in a skill")
        elif SHELL_INJECTION.search(read(root, f)):
            problems.append(f"{f}: '!`' runs a shell command when the skill loads; not allowed")
    for f in files:
        stray_skill = os.path.basename(f) == "SKILL.md" and not re.fullmatch(r"skills/[^/]+/SKILL\.md", f)
        if stray_skill or (f.startswith("skills/") and f.count("/") == 1):
            problems.append(f"{f}: a skill lives at skills/<name>/SKILL.md")
    names = {f.split("/")[1] for f in files if f.startswith("skills/") and f.count("/") >= 2}
    for name in sorted(names):
        rel = f"skills/{name}/SKILL.md"
        if rel not in files:
            problems.append(f"skills/{name}: missing SKILL.md")
            continue
        if files[rel] != REGULAR:
            continue
        fields = frontmatter(read(root, rel))
        if fields is None:
            problems.append(f"{rel}: missing frontmatter")
            continue
        if "" in fields:
            problems.append(f"{rel}: frontmatter takes one 'key: value' per line, each key once (no multiline, comments or blank lines)")
        extra = sorted(set(fields) - FRONTMATTER_KEYS - {""})
        if extra:
            problems.append(f"{rel}: frontmatter keys not allowed: {', '.join(extra)}")
        if fields.get("name") != name or not NAME.match(name):
            problems.append(f"{rel}: name must be '{name}' (lowercase letters, digits and hyphens)")
        if not fields.get("description"):
            problems.append(f"{rel}: description is required")
    return problems


def block_rules(text):
    """The `- rule` lines of the single marked block, or None when the markers are missing, repeated or reversed."""
    if text.count(START) != 1 or text.count(END) != 1:
        return None
    start, end = text.find(START), text.find(END)
    if end < start:
        return None
    lines = [line for line in text[start + len(START):end].split("\n") if line.strip()]
    return [line[2:] if line.startswith("- ") else line for line in lines]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"redirect to {newurl} refused", headers, fp)


def published_rules(url=DOCS_URL):
    # The site's edge refuses Python's default User-Agent; name the client instead.
    request = urllib.request.Request(url, headers={"User-Agent": "aedis-skills-check"})
    with urllib.request.build_opener(_NoRedirect).open(request, timeout=20) as response:
        body = response.read(DOCS_MAX_BYTES + 1)
    if len(body) > DOCS_MAX_BYTES:
        raise ValueError(f"{url} is larger than {DOCS_MAX_BYTES} bytes")
    rules = json.loads(body).get("rules")
    if not isinstance(rules, list) or not rules or not all(isinstance(r, str) and r for r in rules):
        raise ValueError(f"{url} has no list of rules")
    return rules


def rules_problems(skill_text, published):
    ours = block_rules(skill_text)
    if ours is None:
        return [f"skills/aedis-ui/SKILL.md: needs exactly one {START} ... {END} block"]
    if ours == published:
        return []
    return [
        "skills/aedis-ui/SKILL.md: the rules differ from the ones Aedis UI publishes. Published now (check them against",
        "  apps/www/content/agent-docs.ts in aedis-build/aedis-ui before copying; a reviewer approves the change):",
    ] + [f"  - {r}" for r in published]


def main():
    files = tracked_files(ROOT)
    problems = skill_problems(ROOT, files)
    try:
        published = published_rules()
    except (urllib.error.URLError, OSError, ValueError) as err:
        problems.append(f"could not read the published rules from {DOCS_URL} ({err}); this is not a drift, retry later")
    else:
        problems += rules_problems(read(ROOT, "skills/aedis-ui/SKILL.md"), published)
    for p in problems:
        print(p)
    if not problems:
        print(f"ok: {sum(f.startswith('skills/') for f in files)} files in skills/, rules equal to {DOCS_URL}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
