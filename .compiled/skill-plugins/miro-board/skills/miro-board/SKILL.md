---
name: miro-board
description: >
  Create and read Miro board content via MCP tools. Diagrams (flowcharts,
  mindmaps, UML, ER), documents (markdown), tables, and context extraction.
  Use when: user asks to create or read diagrams, documents, or tables on
  Miro boards, or to extract structured content from existing boards.
  Requires: Miro MCP server connected (npx miro-mcp).
metadata:
  category: design
  author: ManniTheRaccoon
  version: "1.0"
  upstream: https://github.com/miroapp/miro-ai
compatibility: >
  Requires Miro MCP server. Setup: npx miro-mcp with MIRO_ACCESS_TOKEN.
  Based on official miroapp/miro-ai skills.
---

# Miro Board 🎨

Create diagrams, documents, tables on Miro boards and extract board content -- via MCP tools.

## Setup

### 1. Miro Access Token

Get a token from [Miro Developer Settings](https://miro.com/app/settings/user-profile/) → REST API.

### 2. MCP Server Config

Add to your MCP config (`.mcp.json`, `claude_desktop_config.json`, or `openclaw.json`):

```json
{
  "mcpServers": {
    "miro": {
      "command": "npx",
      "args": ["-y", "miro-mcp"],
      "env": {
        "MIRO_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

### 3. Alternative: Install via npx skills

```bash
npx skills add miroapp/miro-ai --skill=miro-mcp
```

## MCP Tools

### Content Creation

| Tool | Purpose |
|---|---|
| `diagram_create` | Flowcharts, mindmaps, UML, ER diagrams from text/Mermaid |
| `doc_create` | Markdown documents on boards |
| `table_create` | Tables with text and select columns |
| `table_sync_rows` | Add/update table rows (upsert) |
| `diagram_get_dsl` | Get DSL format spec before creating diagrams |

### Content Reading

| Tool | Purpose |
|---|---|
| `context_explore` | Discover board contents (frames, docs, tables, diagrams) |
| `context_get` | Extract detailed content from specific items |
| `board_list_items` | List items with type/container filters |
| `table_list_rows` | Read table data with column filters |
| `doc_get` | Read document content + version |
| `image_get_data` | Get image content |

### Document Editing

| Tool | Purpose |
|---|---|
| `doc_update` | Edit document via find-and-replace |

## Diagram Types

| Type | Use Case | Example |
|---|---|---|
| `flowchart` | Processes, workflows, decisions | User registration flow |
| `mindmap` | Brainstorming, hierarchies | Product feature ideation |
| `uml_class` | Class structures, inheritance | API model design |
| `uml_sequence` | Component interactions | Auth flow sequence |
| `entity_relationship` | Database schemas | Data model design |

### Creating Diagrams

Natural language works:
```
User registration flow: start -> enter email -> validate email ->
send verification -> user confirms -> create account -> dashboard
```

Or Mermaid for precision:
```
flowchart TD
    A[Start] --> B{Valid Email?}
    B -->|Yes| C[Send Verification]
    B -->|No| D[Show Error]
    C --> E[Create Account]
```

## Documents

Markdown → Miro document:
```markdown
# Sprint Planning -- Week 12

## Goals
- Complete auth module
- Fix critical bugs

## Team
1. **Scotty** -- Implementation
2. **Rémy** -- Code Review
3. **Manni** -- PM + Triage
```

## Tables

Create structured tables with typed columns (`text` or `select` with color-coded options). Use `table_sync_rows` with `key_column` for upsert behavior.

## Board Context Extraction

**Workflow:**
1. `context_explore` → discover what's on the board
2. Pick items of interest
3. `context_get` → extract detailed content

| Item Type | Returns |
|---|---|
| Documents | HTML markup |
| Prototype screens | UI/layout HTML |
| Frames | AI-generated summary |
| Tables | Formatted data |
| Diagrams | AI-generated description |

## Board URLs

Tools accept Miro URLs directly:
- `https://miro.com/app/board/uXjVK123abc=/` -- board
- `https://miro.com/app/board/uXjVK123abc=/?moveToWidget=3458764612345` -- specific item

## Positioning

Board coordinates: center at `(0,0)`, X→right, Y→down.

| Content | Spacing |
|---|---|
| Diagrams | 2000-3000 units apart |
| Documents | 500-1000 units |
| Tables | 1500-2000 units |

Use `parent_id` to place content inside a frame.

## Use Cases for Agents

| Scenario | Tools |
|---|---|
| Visualize architecture | `diagram_create` (flowchart/UML) |
| Create project status board | `table_create` + `doc_create` |
| Extract specs from design board | `context_explore` + `context_get` |
| Generate meeting notes on board | `doc_create` |
| Update project tracker table | `table_sync_rows` |
| Create customer journey map | `diagram_create` (flowchart) |
| Read existing board content | `board_list_items` + `context_get` |

---
*v1.0 -- Based on [miroapp/miro-ai](https://github.com/miroapp/miro-ai). ManniTheRaccoon 2026-03-31.* 🎨
