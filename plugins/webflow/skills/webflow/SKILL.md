---
name: webflow
description: >
  Manage Webflow sites via the official Webflow MCP server -- pages, CMS,
  assets, components, styles, variables, custom code, comments, localization,
  and publishing. Covers the headless Data API tools and the Designer API
  tools (which need the Webflow Designer open in the foreground). Use when:
  reading, auditing, or editing a Webflow site; building or duplicating pages;
  managing CMS collections or assets; or adding legal/marketing pages.
  This plugin ships the Webflow MCP server; just authenticate (OAuth).
metadata:
  category: productivity
  author: Yesterday
  version: "1.0"
  upstream: https://github.com/webflow/mcp-server
compatibility: >
  This plugin ships the Webflow MCP server via .mcp.json (remote HTTP). It
  auto-registers when the plugin is enabled; authenticate with OAuth on first
  use. No API key.
---

# Webflow 🪂

Read and edit Webflow sites through the official Webflow MCP server: pages,
CMS, assets, components, styles, variables, custom code, comments,
localization, and publishing.

## Setup

This plugin **ships the Webflow MCP server** (`.mcp.json` → `webflow`, remote
HTTP at `https://mcp.webflow.com/mcp`). It registers automatically when the
plugin is enabled — no `claude mcp add`, no API key.

You only need to **authenticate (OAuth)** once:

1. Call the `authenticate` tool, open the returned URL, authorize.
2. The real tools load automatically once the flow completes. If the
   `localhost/callback` page errors, pass the full address-bar URL to
   `complete_authentication`.

Verify with a real call before claiming success — e.g. `data_sites_tool`
→ `list_sites`. "Connected" in `/mcp` is not proof; run a tool.

> Standalone (no plugin)? Add the server by hand:
> `claude mcp add webflow --transport http https://mcp.webflow.com/mcp`.

## Two tool tiers — read this first

| Tier | Tools | Needs Designer open? |
|---|---|---|
| **Data API** (REST) | `data_sites_tool`, `data_pages_tool`, `data_cms_tool`, `data_assets_tool`, `data_scripts_tool`, `data_comments_tool`, `data_localization_tool` | No — works headless |
| **Designer API** (live canvas) | `de_page_tool`, `de_component_tool`, `element_tool`, `element_builder`, `whtml_builder`, `style_tool`, `variable_tool`, `asset_tool`, `element_snapshot_tool` | **Yes** |

Designer tools require the **Webflow Designer open in a browser tab, in the
foreground**, with the MCP Bridge app running. When the tab goes to the
background or idle, calls **time out / "Unable to connect"** — the server
returns a Bridge-app link; share it as a markdown link and ask the user to
reopen the Designer and keep it foreground, then retry.

Always call `webflow_guide_tool` **once** at the start of a Designer session
(the server requires it before other tools). `ask_webflow_ai` answers
Webflow how-to questions.

## Core workflows

### Inventory / audit (headless)

`data_sites_tool list_sites` → per site: `data_pages_tool list_pages`,
`data_cms_tool get_collection_list`, `data_scripts_tool get_registered_scripts`
+ `get_site_scripts`, `data_comments_tool list_comment_threads`. Assets,
components, styles, variables need the Designer (`asset_tool`,
`de_component_tool get_all_components`, `style_tool get_styles`,
`variable_tool get_variable_collections`).

### Create a page

There is **no Data-API create-page**. Either `de_page_tool create_page`
(blank — no nav/footer, since those are per-page unless componentized), or
have the user **duplicate** an existing page in the Pages panel (keeps
nav/footer/styles), then edit content via MCP. Set slug/SEO with
`data_pages_tool update_page_settings`.

### Replace rich-text body

`whtml_builder` into the content container with one root `<div>` (`<p>`,
`<strong>`, `<br>`, `<a href="mailto:…">`), supply matching CSS via the `css`
param, then `remove_element` the old block. Verify with `element_snapshot_tool`.

### Add a link across pages (no components)

If the footer/nav is duplicated per page, repeat per page: `switch_page` →
**verify** with `get_current_page` → `query_elements` (filter by style) to
find the wrapper → `element_builder` a `TextLink` with the existing style +
`set_link` (page). Snapshot to confirm.

### Publish

`data_sites_tool publish_site` (or the user clicks Publish). **Publishing
pushes every staged change since the last publish**, not just yours — warn the
user and have them preview first.

## Gotchas

- **Never assume `site_id`** — `list_sites` and confirm. Data tools require it explicitly.
- **`get_all_elements` output is huge** — it often exceeds the token limit and is saved to a file; slice it with python (`read()[A:B]`) or parse in a subagent. Prefer `query_elements` with filters when you can.
- **Active-page drift**: `switch_page` does not always stick; element ops fail with "parent not found" if the canvas is on another page. Always `get_current_page` to verify before building.
- **`set_text` on a RichText** collapses formatting — use `whtml_builder` for structured content.
- **Inherited styles**: new plain blocks can inherit `text-align: justify`, bold display fonts, etc. from the body. Set `font-family` / `font-weight` / `text-align` explicitly and snapshot.
- **Verify visually**: `element_snapshot_tool` after every structural edit. Don't trust the success message alone.
- **Nothing is live until published.** Treat publish as outward-facing — get explicit confirmation; never publish unprompted.

## Safety

Read-only Data tools (`list_*`, `get_*`) are always safe. Treat any
write (create/update/delete elements, CMS items, scripts) and `publish_site`
as consequential and outward-facing — confirm scope first, and let the user
own the publish.
