# office-extras

Yesterday Daily Stack -- **extras tier**. Optional integrations that need external SaaS accounts or API keys.

## Scope

Wrapper bundle (no own skills). Installs Daily-Stack add-ons that aren't useful without an external account / key, kept out of `office` core so users without those services don't see broken integrations.

## Cross-marketplace plugins (4, auto-pulled via plugin.json)

| Plugin | Purpose | Requires |
|---|---|---|
| [figma-console-mcp](../../skills/productivity/figma-console-mcp) | Figma + FigJam + Slides automation | Figma account + token |
| [miro-board](../../skills/productivity/miro-board) | Miro MCP client | Miro account + token |
| [voxtral-tts-api](../../skills/capabilities/tts/voxtral-tts-api) | Mistral Voxtral TTS | Mistral API key |
| [vrr-efa-api](../../skills/travel/vrr-efa-api) | VRR regional transit (Germany) | none -- but only useful in DE/NRW |

## Install

```bash
/plugin marketplace add Yesterday-AI/skills
/plugin install office-extras@yesterday-public-plugins
```

Typically alongside `office` (core); `office-extras` alone works too if you only want these integrations.
