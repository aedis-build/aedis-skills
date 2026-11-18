---
name: aedis-ui
description: Use when building a React interface with Aedis UI (the @aedis/cli registry): finding and installing components, hooks or blocks, wiring agent chat, approvals, forms or the app shell, and following the security rules for agent and user content.
---

# Aedis UI

Aedis UI ships React components, hooks, libraries and blocks as source. A CLI installs them into the project after
verifying the signed release. Use what exists before writing a component yourself.

## Find the right item

1. Prefer the docs MCP server, when the project has it configured: `npx @aedis/cli@<version> mcp` (stdio, read-only),
   with the version from the first rule below. Tools: `list_components`, `search_components`, `get_component`,
   `get_install_command`.
2. Without it, read https://ui.aedis.build/llms.txt, the index, and then only the page of each item you need,
   `https://ui.aedis.build/docs/<name>` (blocks: `/blocks/<name>`). The whole set is in
   https://ui.aedis.build/llms-full.txt, which is large; read it only to search.
3. Read the entry of every item you use before writing code with it: its props, its usage example and its rules.

## Install

- Once per project: `npx @aedis/cli@<version> init`.
- Each item: `npx @aedis/cli@<version> add <name>`. It adds the item's dependencies too.
- To compare local copies with the release: `npx @aedis/cli@<version> diff`.
- Installed files are source in the project. Edit them like the rest of the code; do not reinstall over local edits.

## Rules

Follow these with every item. They are the rules Aedis UI publishes for agents, copied as they are.

<!-- aedis-ui-rules:start -->
- Install with `npx @aedis/cli@0.10.0 add <name>` (it verifies the signed release). Never run `npx aedis`: that package belongs to someone else.
- Pass agent and user content as props or text children. No prop takes markup; never use dangerouslySetInnerHTML.
- Keep text fields bounded: leave the default maxLength or set it to the server's limit, never remove it.
- Reach the backend through api() (same-origin, CSRF header, no redirects); never fetch another origin with credentials.
- Actions that delete or leave the company go through a confirmation that starts on Cancel: AlertDialog, ApprovalCard or a destructive DropdownMenuItem.
<!-- aedis-ui-rules:end -->

## Rules per item

Each entry names the sinks it touches (DOM, Input, Transport, Session) and lists the rules for them under "Rules".
The Session rule appears only there: keep it for every item that lists the Session sink.

## When an item is missing

Compose it from installed items and keep the rules above. Do not copy markup from elsewhere that renders HTML from
strings, stores tokens in the browser or calls another origin with credentials.
