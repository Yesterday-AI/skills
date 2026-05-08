---
name: figma-console-mcp
description: >
  Connect AI agents to Figma via the Figma Console MCP server. Enables design system extraction,
  UI component creation, variable/token management, visual debugging, FigJam boards, and Slides
  presentations. Use when an agent needs to read, create, or modify Figma designs programmatically.
license: MIT
metadata:
  author: YessyTheCyberCat
  version: "1.0"
  category: design
compatibility: >
  Requires an MCP-capable agent runtime. For full capabilities (92+ tools): Node.js 18+ and
  Figma Desktop with Desktop Bridge plugin. Cloud Mode available for web AI clients without Node.js.
---

# Figma Console MCP

> Give your AI agent direct access to Figma -- read, create, and edit designs programmatically.

Figma Console MCP is an MCP server with **92+ tools** that bridges AI agents and Figma.
It supports design system extraction, component creation, variable management, FigJam boards,
and Slides presentations.

---

## When to Use

Use this skill when an agent needs to:

- **Extract design systems** -- pull colors, typography, spacing, components from existing Figma files
- **Create UI components** -- build frames, shapes, text, and auto-layout structures via natural language
- **Manage design tokens** -- read/create/update Figma variables and styles
- **Visual debugging** -- capture screenshots, inspect component properties for development
- **FigJam collaboration** -- create stickies, connectors, tables for brainstorming boards
- **Slides presentations** -- build and manage Figma Slides programmatically

**Don't use** when you only need static image exports (use Figma REST API directly) or
when working with non-Figma design tools.

---

## Prerequisites

### Figma Personal Access Token (PAT)

Generate at: https://www.figma.com/developers/api#access-tokens

Required scopes:
- **File content** → Read
- **Variables** → Read
- **Comments** → Read + Write

### For Write Access (creating/editing designs)

- **Figma Desktop app** (not web) with the **Desktop Bridge plugin** installed
- The Desktop Bridge plugin is a one-time import -- it auto-updates via its bootloader

### For NPX Mode

- **Node.js 18+**
- Environment variable: `ENABLE_MCP_APPS=true`

---

## Setup

Three connection modes, depending on your environment:

### Mode 1: NPX (Recommended -- Full 92+ Tools)

Best for: Local AI agents, CLI-based workflows, full read+write access.

Add to your MCP client configuration (e.g. `claude_desktop_config.json`, `mcp.json`):

```json
{
  "mcpServers": {
    "figma-console-mcp": {
      "command": "npx",
      "args": ["-y", "figma-console-mcp"],
      "env": {
        "FIGMA_PAT": "<your-figma-personal-access-token>",
        "ENABLE_MCP_APPS": "true"
      }
    }
  }
}
```

**Requirements:** Node.js 18+, Figma Desktop with Desktop Bridge plugin for write operations.

### Mode 2: Cloud Mode (82 Tools -- No Node.js)

Best for: Web-based AI clients (ChatGPT, Gemini, etc.) that support MCP but can't run Node.js.

1. Go to https://figma-console-mcp.southleft.com/
2. Connect your Figma account
3. Add the provided MCP endpoint to your AI client

**Key advantage:** Uses the Figma Plugin API instead of the REST API -- this means
**variables work on ALL Figma plans**, not just Enterprise.

**Limitation:** 82 tools (no local file system tools). Requires Figma Desktop with Desktop Bridge.

### Mode 3: Remote SSE (22 Tools -- Read-Only)

Best for: Quick read-only access, no Figma Desktop needed.

```json
{
  "mcpServers": {
    "figma-console-mcp": {
      "url": "https://figma-console-mcp.southleft.com/sse",
      "headers": {
        "Authorization": "Bearer <your-figma-pat>"
      }
    }
  }
}
```

**Limitation:** Read-only -- no design creation or editing. Uses REST API only (22 tools).

### Mode Comparison

| Feature                  | NPX (Full) | Cloud Mode | Remote SSE |
|--------------------------|:-----------:|:----------:|:----------:|
| Tools available          | 92+         | 82         | 22         |
| Read designs             | ✅          | ✅         | ✅         |
| Create/edit designs      | ✅          | ✅         | ❌         |
| Variables (all plans)    | ❌ (Enterprise only via REST) | ✅ | ❌ |
| Requires Node.js         | ✅          | ❌         | ❌         |
| Requires Figma Desktop   | ✅ (for writes) | ✅    | ❌         |

---

## Key Capabilities

### Design System Extraction

Pull complete design systems from existing Figma files:

| Tool | Purpose |
|------|---------|
| `figma_get_design_system_kit` | Extract full design system (colors, typography, spacing, effects) |
| `figma_get_variables` | Read all variables/tokens from a file |
| `figma_get_styles` | Get paint, text, effect, and grid styles |
| `figma_get_component` | Inspect a specific component's structure |

**Example -- Extract design tokens:**
```
Agent prompt: "Extract the design system from file XYZ and output it as CSS custom properties."

Tools used:
1. figma_get_design_system_kit (fileKey: "abc123") → returns colors, typography, spacing
2. Agent transforms the output into CSS variables
```

### Design Creation & Editing

Build and modify designs programmatically:

| Tool | Purpose |
|------|---------|
| `figma_execute` | Execute arbitrary Figma plugin commands (create frames, shapes, text) |
| `figma_create_variable` | Create new variables/tokens |
| `figma_arrange_component_set` | Auto-arrange component variants in a set |

**Example -- Create a button component:**
```
Agent prompt: "Create a primary button component with label text, 16px padding, rounded corners."

Tools used:
1. figma_execute → create frame with auto-layout, padding, corner radius
2. figma_execute → add text node with label
3. figma_execute → set fill color from design system
```

### Visual Context & Development Handoff

Get visual context for code implementation:

| Tool | Purpose |
|------|---------|
| `figma_get_component_for_development` | Get component specs optimized for developers (props, variants, spacing) |
| `figma_capture_screenshot` | Capture a screenshot of any node or frame |

### FigJam Boards

Create and populate FigJam boards for brainstorming and planning:

| Tool | Purpose |
|------|---------|
| `figjam_create_sticky` | Add sticky notes |
| `figjam_create_connector` | Draw connectors between elements |
| `figjam_create_table` | Create data tables |

### Slides Presentations

Build Figma Slides programmatically:

| Tool | Purpose |
|------|---------|
| `figma_create_slide` | Create a new slide |
| `figma_add_text_to_slide` | Add text content to slides |
| `figma_set_slide_transition` | Set slide transitions |

---

## Workflow Examples

### 1. Extract Design System → Implement in Code

```
Step 1: Extract the design system
  → figma_get_design_system_kit(fileKey: "your-file-key")
  → Returns: colors, typography scales, spacing tokens, effects

Step 2: Extract variables for token mapping
  → figma_get_variables(fileKey: "your-file-key")
  → Returns: all variable collections with values and modes

Step 3: Agent generates code
  → Transform tokens into CSS custom properties, Tailwind config, or design token JSON
  → Output structured token files (e.g., tokens.css, theme.ts)
```

### 2. Create UI Components via Natural Language

```
User: "Create a card component with an image placeholder, title, description, and a CTA button."

Agent workflow:
1. figma_execute → Create outer frame (auto-layout, vertical, 16px gap)
2. figma_execute → Add image placeholder rectangle (fill: gray, 16:9 ratio)
3. figma_execute → Add title text (24px, bold)
4. figma_execute → Add description text (16px, regular, secondary color)
5. figma_execute → Create button frame (auto-layout, horizontal, padding 12/24)
6. figma_execute → Add button label text
7. figma_arrange_component_set → Clean up layout
```

### 3. Manage Design Tokens / Variables

```
User: "Add a new 'warning' color token set: warning-50 through warning-900."

Agent workflow:
1. figma_get_variables → Check existing variable collections
2. figma_create_variable → Create warning-50 (#FFF8E1)
3. figma_create_variable → Create warning-100 (#FFECB3)
   ... (continue for each shade)
4. figma_get_variables → Verify all tokens were created correctly
```

### 4. "Brand Therapy" -- Inspect & Improve Existing Brand

```
User: "Analyze our current brand file and suggest improvements."

Agent workflow:
1. figma_get_design_system_kit → Extract current brand system
2. figma_capture_screenshot → Visual audit of key screens
3. Agent analyzes:
   - Color contrast ratios (accessibility)
   - Typography consistency
   - Spacing rhythm
   - Component reuse patterns
4. Agent creates a FigJam board with findings:
   - figjam_create_sticky → Add observation notes
   - figjam_create_connector → Link related findings
   - figjam_create_table → Summary matrix of issues and suggestions
```

---

## Gotchas & Tips

### Desktop Bridge Plugin

- **One-time setup:** Import the plugin into Figma Desktop via the MCP server's instructions
- **Auto-updates:** The plugin uses a bootloader pattern -- once installed, it updates itself
- **Required for:** All write operations (NPX and Cloud Mode)
- **Not needed for:** Remote SSE (read-only mode)

### Cloud Mode vs REST API

Cloud Mode connects through the **Figma Plugin API**, not the REST API. This is important because:
- **Variables work on ALL Figma plans** (Starter, Professional, Organization, Enterprise)
- REST API variable access requires Enterprise plan
- If your team isn't on Enterprise but needs variable/token access → use Cloud Mode

### Environment Variables

For NPX mode, ensure `ENABLE_MCP_APPS=true` is set:

```bash
# In your shell
export ENABLE_MCP_APPS=true

# Or in the MCP config (recommended)
"env": { "ENABLE_MCP_APPS": "true" }
```

### File Keys

Most tools require a Figma `fileKey`. Extract it from the Figma URL:

```
https://www.figma.com/design/ABC123xyz/My-Design-File
                              ^^^^^^^^^^^
                              This is the fileKey
```

### Rate Limits

- The Figma REST API has rate limits. The MCP server handles retries internally.
- For bulk operations (many variable creates), add small delays between calls.
- Cloud Mode (Plugin API) has more generous limits than REST API.

### Common Issues

| Problem | Solution |
|---------|----------|
| "Plugin not found" | Install Desktop Bridge plugin in Figma Desktop |
| Variables return empty | Check PAT has "Variables Read" scope; or use Cloud Mode for non-Enterprise |
| Write operations fail | Ensure Figma Desktop is running with Desktop Bridge active |
| NPX won't start | Check Node.js 18+ and `ENABLE_MCP_APPS=true` |
| SSE connection drops | Remote SSE is stateless -- reconnect automatically handled by MCP client |

---

## References

- **Documentation:** https://docs.figma-console-mcp.southleft.com/
- **GitHub:** https://github.com/southleft/figma-console-mcp
- **npm:** https://www.npmjs.com/package/figma-console-mcp
- **Website:** https://figma-console-mcp.southleft.com/

---

*🐾 Built for Yesterday's UI Designer Agent (Walsh persona) and any agent that needs to speak Figma.*
