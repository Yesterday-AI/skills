---
name: slack-best-practices
description: A collection of formatting rules, emoji quirks, and communication etiquette for Slack. Use when composing messages for Slack to ensure correct rendering and team-friendly communication.
metadata:
  author: YessyTheCyberCat
  version: "1.2"
  category: productivity
  source: https://docs.slack.dev/messaging/formatting-message-text/
compatibility: OpenClaw agent interacting with Slack channels.
---

# Slack Best Practices 💬🐈‍⬛

> ### 🛑 CRITICAL RULE: NEVER USE DOUBLE ASTERISKS (`**`)
> Slack does NOT support Standard Markdown bolding. Using `**` will show the literal asterisks to the user.
> *ALWAYS use single asterisks (`*`) for bold text.*
>
> *FOR AGENTS:* You are hard-wired to use `**`. You MUST run a post-processing step on your final message string to replace `**` with `*` before calling the message tool.

Slack uses a unique flavor of Markdown called *mrkdwn*. This skill captures the quirks and best practices learned by Yesterday agents to ensure our messages look perfect.

---

## Formatting Rules (mrkdwn)

| Element | mrkdwn Syntax | Standard MD (Avoid!) |
| :--- | :--- | :--- |
| *Bold* | `*text*` (single asterisk) | `**text**` |
| _Italic_ | `_text_` (underscore) | `*text*` |
| ~Strike~ | `~text~` | `~~text~~` |
| Blockquote | `> text` | same |
| Inline Code | `` `code` `` | same |
| Code Block | ` ```code block``` ` | same |
| Link | `<URL\|Label>` | `[Label](URL)` |

*Note:* Slack does NOT support `#` headers or Markdown tables. Use *ALL CAPS BOLD* to simulate headers. Use bullet lists instead of tables.

---

## Links & URLs

Auto-linking works if you paste a raw URL. To suppress the preview embed, wrap it in angle brackets:

```
<https://example.com>
```

To show custom link text:

```
<https://example.com|Click here>
```

Email links:

```
<mailto:alex@example.com|Mail Alex>
```

*Special characters* that must be escaped in text strings (not in URLs):

| Character | Use instead |
| :--- | :--- |
| `&` | `&amp;` |
| `<` | `&lt;` |
| `>` | `&gt;` |

---

## Mentions

*User mention:*
```
<@U012AB3CD>
```
Slack auto-converts the user ID to their display name. Get user IDs from their Slack profile ("Copy member ID").

*Channel mention:*
```
<#C123ABC456>
```
Slack auto-converts to the channel name. Get channel ID from the URL: `https://app.slack.com/client/E.../C123ABC456`

*User group mention:*
```
<!subteam^SAZ94GDB8>
```

*Special mentions (use sparingly!):*

| Mention | Syntax | Who gets notified |
| :--- | :--- | :--- |
| @here | `<!here>` | Active members of channel |
| @channel | `<!channel>` | All members of channel |
| @everyone | `<!everyone>` | Every workspace member (#general only) |

---

## Date & Time Formatting

Slack can auto-localize timestamps to the reader's timezone:

```
<!date^UNIX_TIMESTAMP^{date_short} at {time}|Fallback text>
```

Available tokens:

| Token | Example output |
| :--- | :--- |
| `{date_num}` | 2026-03-05 |
| `{date}` | March 5th, 2026 |
| `{date_short}` | Mar 5, 2026 |
| `{date_long}` | Thursday, March 5th, 2026 |
| `{date_pretty}` | today / yesterday / tomorrow |
| `{time}` | 2:00 PM |
| `{time_secs}` | 2:00:00 PM |

---

## Emoji

- *Standard Only:* Stick to standard Slack emojis (`:feet:`, `:sparkles:`, `:rocket:`).
- *No hallucinations:* Do not invent emoji names unless sure they exist in the workspace.
- *Tone:* Use sparingly to soften messages -- one emoji per paragraph max.
- Emoji are stored internally in colon format (`:smile:`). When posting, you can use native unicode emoji directly and Slack will convert them.

---

## Cross-Channel Posting (message Tool)

> ### 🛑 CRITICAL: Use the Correct Tool Format
> The generic `message` tool's `channel` parameter does NOT work for cross-channel posting in Slack. It always sends to the current session's DM. Use the *Slack skill* `sendMessage` action instead.

*Posting to a different channel from within a DM session:*

```json
{
  "action": "sendMessage",
  "to": "channel:C0EXAMPLE01",
  "content": "Hello from another channel"
}
```

*Posting to a user's DM:*

```json
{
  "action": "sendMessage",
  "to": "user:U012AB3CD",
  "content": "Hello via DM"
}
```

*The `to` field format:*

| Target | Format | Example |
| :--- | :--- | :--- |
| Channel by ID | `channel:C123ABC456` | `channel:C0EXAMPLE01` |
| User by ID | `user:U012AB3CD` | `user:U0EXAMPLE02` |

*Common mistake:* Using `message(action=send, channel=C123)` -- this ignores the channel parameter and posts to the DM of the current session. Always use `sendMessage` with `to: "channel:..."`.

*Prerequisites:*
- The target channel must be in `channels.slack.accounts.default.channels` with `allow: true`
- The bot must be invited to the target channel
- `groupPolicy: "allowlist"` means only explicitly listed channels are allowed

---

## Communication Etiquette

1. *Thread over Flood:* Use threads for deep-dives, detailed logs, or long explanations. Keep channels scannable.
2. *Mentions:* Use `@user` sparingly. Prefer no mentions for broad updates unless truly urgent.
3. *Headers:* Simulate with `*ALL CAPS BOLD*` -- Slack has no `#` header support.
4. *No tables:* Slack does not render Markdown tables. Use bullet lists instead.
5. *Link embeds:* Wrap links in `<>` to suppress large previews in busy channels.

---

## Troubleshooting & Common Agent Mistakes

- *The "Model Reflex" (CRITICAL):* LLMs are pre-trained on millions of Standard Markdown examples and WILL reflexively use `**bold**` even when they know better. Treat this as a high-risk failure point.
- *The "Mental Double-Check":* Before any message is sent to Slack, perform a final scan of the text string to ensure NO double-asterisks (`**`) exist. Convert to `*` if found.
- *Formatting Over Content:* High-quality content is useless if the formatting is broken. Prioritize correct mrkdwn syntax over speedy replies.
- *Self-Correction Loop:* Before calling the `message` tool, run a search-and-replace: `**` → `*`.

---

*"Clear is kind. Scannable is better."* 🐾📡
