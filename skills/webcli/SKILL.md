---
name: "webcli"
description: "Drives a real Chrome window through the local webcli bridge and extension. Invoke when an agent needs to open pages, inspect DOM, click, type, extract, or debug live browser flows with webcli."
---

# webcli

Use it when an agent needs to drive a real Chrome window through the local `webcli + Chrome extension + bridge server` stack.

---

## When To Use

Invoke this skill when:

- You need to open pages and keep reusing a browser session
- You need to inspect page state, text, attributes, or HTML
- You need to click, type, switch tabs, take screenshots, read cookies, or call CDP
- You need to work with logged-in pages or a tab that a human already opened
- You need to debug bridge or extension runtime behavior
- You need to inspect command records under `record/<session>/*.md`

Do not use it:

- As a generic website scraper
- For writing reusable site adapters
- If bridge and extension are not started yet but you are pretending the browser is ready

---

## Prerequisites

Before running browser commands, confirm:

1. `webcli` is installed
2. The bridge server is running
3. Chrome has loaded the local `extension/`
4. The extension is connected to `ws://127.0.0.1:8765`

Typical startup:

```bash
webcli bridge serve
```

Then load the repo's `extension/` directory in Chrome.

---

## Session Model

- All browser commands use `webcli browser <session> <command>`
- `webcli browser` also supports `--host` and `--port`, defaulting to `127.0.0.1:8765`
- Reuse the same `session` for one multi-step task
- Use different session names for different tasks
- `bind` attaches a manually opened Chrome tab to a session
- `close` and `unbind` end the current session control flow
- Every command and result is written to `record/<session>/*.md`

Example:

```bash
webcli browser demo open https://example.com
webcli browser demo state
webcli browser demo click --css "a"
webcli browser demo close
```

Bind an already open tab:

```bash
webcli browser demo bind
webcli browser demo state
webcli browser demo unbind
```

---

## Core Rules

1. Inspect before acting. Run `state`, `find`, or `get` before `click` or `type`
2. Refresh your understanding after page changes. Do not rely on old assumptions after navigation or submit flows
3. Keep one stable `session` for one continuous workflow
4. Prefer structured commands instead of jumping straight to `eval`
5. Verify important writes, for example run `get value` after typing
6. If you see `extension_offline`, check bridge and extension first instead of guessing
7. When you need history or evidence, read the Markdown files under `record/<session>/`

---

## Common Commands

### Open And Inspect

```bash
webcli browser demo open https://example.com
webcli browser demo state
webcli browser demo frames
webcli browser demo screenshot page.png --full-page
```

### Read Content

```bash
webcli browser demo get title
webcli browser demo get url
webcli browser demo get text --css "h1"
webcli browser demo get value --css "input[name=q]"
webcli browser demo get attributes --css "a.primary"
webcli browser demo get html
webcli browser demo extract
```

### Interact

```bash
webcli browser demo click --css "button"
webcli browser demo type --css "input[name=q]" "hello"
webcli browser demo fill --css "textarea" "full replacement text"
webcli browser demo select --css "select[name=country]" "us"
webcli browser demo scroll down --amount 800
webcli browser demo wait text "Success"
webcli browser demo eval "document.title"
```

### Session Control

```bash
webcli browser demo bind
webcli browser demo tab list
webcli browser demo tab new https://example.com
webcli browser demo close
webcli browser demo unbind
```

### Debugging

```bash
webcli browser demo console
webcli browser demo analyze
webcli browser demo network
webcli browser demo cdp Runtime.evaluate --params '{"expression":"document.title"}'
webcli browser demo dialog accept --text "ok"
```

---

## Command Inventory

The current repo exposes these command groups and commands.

### Top-Level Browser Commands

- `open <url>`
- `state`
- `find --css <selector> [--limit N]`
- `extract [--css <selector>]`
- `frames`
- `screenshot [path] [--full-page] [--width N] [--height N]`
- `back`
- `eval <js>`
- `network`
- `console`
- `analyze`
- `cookies [--domain <domain>]`
- `cdp <method> [--params '{}']`
- `bind`
- `unbind`
- `close`
- `init <name>`
- `verify <name>`

### `browser get`

- `get title`
- `get url`
- `get text --css <selector>`
- `get value --css <selector>`
- `get attributes --css <selector>`
- `get html [--css <selector>]`

### Interaction Commands

- `click --css <selector>`
- `type --css <selector> <text>`
- `fill --css <selector> <text>`
- `select --css <selector> <value>`
- `keys <key>`
- `wait time|text|selector <value> [--timeout N]`
- `scroll up|down [--amount N]`
- `hover --css <selector>`
- `focus --css <selector>`
- `dblclick --css <selector>`
- `check --css <selector>`
- `uncheck --css <selector>`
- `upload --css <selector> <files...>`
- `drag --from-css <selector> --to-css <selector>`

### `browser tab`

- `tab list`
- `tab new [url]`
- `tab select [--page <page>] [--index N]`
- `tab close [--page <page>] [--index N]`

### `browser dialog`

- `dialog accept [--text <text>]`
- `dialog dismiss`

---

## Behavior Notes

- `open`, `frames`, `screenshot`, `cookies`, `cdp`, `bind`, `close`, and tab operations go through the bridge protocol
- Many other commands such as `state`, `find`, `get`, `click`, `type`, `fill`, `scroll`, and `analyze` currently run as page-side JavaScript through `exec`
- CSS selectors are the main targeting mechanism in the current implementation
- `wait` currently uses polling from the CLI side rather than a native bridge-side wait primitive
- `get html` returns an object like `{ html: ... }`, not raw HTML text
- `extract` returns a simple object with `url`, `title`, and extracted `text`
- `network` and `console` currently read from page globals such as `window.__opencli_net` and `window.__opencli_console`

### Current Lightweight Or Placeholder Areas

- `upload` currently returns a warning-style result and is not yet backed by the extension's native file-input action
- `drag` is a lightweight DOM-event fallback, not a full browser-native drag-and-drop implementation
- `dialog accept` and `dialog dismiss` expect page-side dialog helpers such as `window.__opencli_handle_dialog`
- `init` and `verify` are placeholder commands and currently return a `todo` payload instead of a real scaffold or verification flow

When writing agent instructions, treat these commands as available but lightweight, and prefer the more stable core commands first.

---

## Recommended Workflows

### Standard Page Interaction

```bash
webcli bridge serve
webcli browser task open https://example.com
webcli browser task state
webcli browser task find --css "form input"
webcli browser task type --css "input[name=q]" "webcli"
webcli browser task click --css "button[type=submit]"
webcli browser task wait text "result"
webcli browser task state
```

### Human Opens The Page First, Then Agent Continues

```bash
webcli bridge serve
webcli browser account bind
webcli browser account state
webcli browser account click --css "[data-testid=profile]"
webcli browser account extract
```

---

## Troubleshooting

### `extension_offline`

Usually caused by:

- `webcli bridge serve` is not running
- The extension is not loaded
- The extension is not connected to the local bridge

Check first:

```bash
webcli bridge serve
```

Then reopen the extension popup and verify that it shows a connected state.

### `timeout`

This means the extension did not return a result in time. Check:

- Whether the page is still loading
- Whether the extension background logic is throwing
- Whether the command hit a very slow navigation flow

### Bridge Debug Errors

If you get a `bridge_debug_*` error code, the bridge caught an exception at a specific stage.

Check first:

- The bridge logs in the current terminal
- The latest record file under `record/<session>/`
- The related logic in `extension/src/background.ts`

### Selector Errors

Many page-side commands return simple selector-based errors such as:

- `selector_not_found`
- `not_a_select`
- `not_checkable`

When that happens:

- Re-run `state` or `find --css ...`
- Confirm the selector still exists after the latest page change
- Prefer a narrower selector before retrying

---

## Agent Guidance

- Reuse the same `session` across a long workflow
- Start with `state` to build a mental model of the page
- Re-check state immediately after navigation or large DOM changes
- Verify important writes before moving to the next step
- When you need evidence, reference the matching Markdown under `record/<session>/`
- If the bug only happens at runtime, inspect bridge and extension behavior instead of relying only on static code

---

## Repo Mapping

- CLI entry: `src/webcli_main.py`
- Bridge server: `src/bridege/bridge_server.py`
- Bridge client: `src/bridege/bridge_client.py`
- Browser command modules: `src/browser_cli/`
- Browser JS helpers: `src/browser_js.py`
- Bridge action factories: `src/browser_actions.py`
- Extension background worker: `extension/src/background.ts`
- Interaction records: `record/<session>/*.md`

The goal of this skill is to make the agent work against the real `webcli` structure and command set in this repository, instead of following the old `opencli` conventions.
