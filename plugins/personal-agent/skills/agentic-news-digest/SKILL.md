---
name: agentic-news-digest
description: >
  End-to-end skill for curated team news digests. Covers the full pipeline: team inbox (manual
  submissions & co-authored drafts), source aggregation (RSS, Twitter, GitHub, web search),
  research & fact-checking, relevance scoring, article formatting (5 templates), and scheduled
  delivery to Slack/Discord/WhatsApp. Handles the critical handoff between conversational sessions
  (where links are received) and isolated cron sessions (where digests are built).
metadata:
  author: Yesterday-AI
  version: "2.1"
  category: productivity
compatibility: OpenClaw agent with web_search, web_fetch, message tool, and file access.
---

# Agentic News Digest 📰

Turn information overload into a curated knowledge stream. This skill enables an agent to act as
a news curator for a team -- collecting tips from conversations, researching sources, fact-checking
claims, scoring relevance, and delivering formatted digests.

## When to Use

- Running a **Daily News Digest** for a team channel
- Publishing **Breaking News** about significant industry events
- Announcing **new skills, features, or milestones** internally
- Creating a **Weekly Recap** of what happened
- Setting up a **Tech Radar** to track specific trends
- A team member **shares a link** and says "put this in the next digest"

## Setup

On first activation, create `memory/news_digest_config.json`:

```json
{
  "audience": "Team name or description",
  "goals": ["What the digest should achieve"],
  "detail_level": "Brief | Balanced | Deep-Dive",
  "sources": {
    "external": ["RSS URLs", "Twitter accounts", "blogs"],
    "internal": ["GitHub org/repos", "internal docs"]
  },
  "channel": "Channel ID for delivery",
  "schedule": "HH:MM Timezone",
  "custom_topics": []
}
```

---

## The Inbox Problem: Why This Section Exists

Agents often receive news tips in **conversational sessions** (DMs, group chats) but publish
digests from **isolated cron sessions**. These are separate processes with no shared memory.

**If you only "remember" a link in conversation, the cron job will never see it.**

The inbox is a file-based handoff mechanism that solves this. It is the ONLY reliable way to
pass items from conversation → digest pipeline. Not memory files, not MEMORY.md, not "mental
notes." The inbox file.

### Inbox File: `news/inbox.json`

```json
{
  "version": 1,
  "items": []
}
```

Also create `news/archive/` for processed items.

### Item Schema

Each inbox item looks like this:

```json
{
  "url": "https://example.com/article",
  "title": "Optional title if already known",
  "context": "Why this was shared / what the submitter said about it",
  "draft": null,
  "submitted_by": "Name of the person who sent it",
  "submitted_at": "2026-03-31T10:30:00Z",
  "priority": "normal | high",
  "target_type": "daily | breaking | skill-announcement | milestone"
}
```

### Receiving Tips During Conversation

When a team member shares a link or news tip in a DM or group chat:

1. Read `news/inbox.json`
2. Append the item with full metadata (URL, context, who sent it, timestamp)
3. Write back to `news/inbox.json` *immediately*
4. Confirm to the user that it's queued

**Do NOT:**
- Write it to a separate queue file that the cron job doesn't check
- Store it only in memory/daily notes and hope it gets picked up
- Say "vorgemerkt" without actually writing to `news/inbox.json`
- Rely on session context surviving to the next heartbeat

**The rule is simple:** If it's not in `news/inbox.json`, it doesn't exist for the digest pipeline.

### Co-Authored Drafts

Sometimes a team member doesn't just drop a link -- they collaborate with the agent on the article
text in conversation. They iterate, give feedback, adjust wording. The result is a **co-authored
draft** that both sides agreed on.

**Two submission modes:**

| Mode | What happens | Agent's job |
|------|-------------|-------------|
| *Raw input* (link, bullets, notes) | Agent writes the article from scratch | Research, summarize, format |
| *Iterated draft* (text refined in conversation) | Agent publishes as-is | Format-fix only (platform syntax, typos) |

**Rules for iterated drafts:**
- Store the final agreed text in the `draft` field of the inbox item
- Set `priority: "high"` automatically
- The digest pipeline MUST publish the draft *verbatim* -- no rewriting, no re-summarizing
- Only allowed changes: platform formatting (e.g., Slack `*bold*` syntax) and typo fixes
- Fact-checking still applies (verify claims/links work), but the text stays as agreed
- Confirm to the submitter: "Gespeichert in der Inbox -- wird genau so gepostet."

**Why this matters:** When someone invests time iterating on text with you, they chose every word
deliberately. Re-summarizing it in the cron job throws away that effort and breaks trust.

---

## The Digest Pipeline

Every digest -- daily, weekly, or breaking -- follows these 5 steps in order.

### Step 1: Read the Inbox (ALWAYS FIRST)

Before any external aggregation:

1. Read `news/inbox.json`
2. Separate items into two buckets:
   - **Draft items** (`draft` is not null): Auto-include. Skip scoring & summarization.
   - **Raw items** (`draft` is null): Feed into the normal pipeline with a +2 relevance bonus.
3. If the inbox is empty, proceed to external aggregation.

**This step is not optional.** The inbox exists because team members explicitly flagged these
items as relevant. Skipping it defeats the purpose of the entire inbox mechanism.

### Step 2: Aggregate External Sources

Gather raw candidates from configured sources:

| Source Type | Method | Notes |
|-------------|--------|-------|
| RSS/Atom feeds | `web_fetch` on feed URLs | Parse for items < 24h old |
| Twitter/X | RSS proxies or `x-reader` skill | Check configured accounts |
| GitHub repos | `gh api` for commits, PRs, releases | Last 24h for daily, 7d for weekly |
| Web search | `web_search` with specific queries | Not broad scans -- targeted topics |
| Exa AI | `exa-search-api` skill (if available) | Best for semantic discovery |
| Internal | Project files, recent team activity | Only company-public information |

**Target:** 15-25 raw candidates for a daily digest, 40-60 for a weekly.

### Step 3: Research & Fact-Check

For each candidate (external AND raw inbox items), verify:

**Freshness:**
- Extract the *publication date* from the source (not just when you found it)
- Daily: published within last 24h. Weekly: within last 7 days.
- No date available → verify via `web_search` that the topic is current
- ⚠️ NEVER present old news as new. When in doubt, drop the item.

**Source quality:**
- Is the source authoritative? (Official blog, verified account, reputable outlet)
- Can the claim be corroborated by a second source?
- For numbers/stats: trace to the original study or announcement
- For product launches: verify on the official product page

**Context enrichment:**
- What's the backstory? (Follow-up to something the team already knows?)
- Competing perspectives? (Don't present one-sided narratives)
- Actual impact vs. hype?

**Drop the item if:** No verifiable date, single anonymous source, contradicted by official
channels, clickbait with no substance, older than the time window.

### Step 4: Score & Select

Score each verified item on a 0-10 scale:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Strategic Fit | 3 | Directly relevant to team's current projects or strategy |
| Actionability | 2 | Team could act on this (adopt tool, adjust approach) |
| Novelty | 2 | Genuinely new information, not a rehash |
| Impact | 2 | Significant industry shift, major launch |
| Source Quality | 1 | Authoritative, primary source |

**Bonuses:**
- Inbox submission: +2 (team member already deemed it relevant)
- Co-authored draft: auto-include (bypasses scoring entirely)

**Thresholds:**
- ≥ 7: Include (highlight if ≥ 9)
- 4-6: Include if space permits
- < 4: Drop

**Item limits:** Daily: 5-8 items total. Weekly: 10-15. Quality over quantity -- always.

### Step 5: Format, Publish, Archive

1. Select the appropriate template (see below)
2. Apply platform-specific formatting
3. Publish to the configured channel
4. Move processed inbox items to `news/archive/inbox_YYYY-MM-DD.json`
5. Reset `news/inbox.json` items to `[]`
6. Update `memory/heartbeat-state.json` (e.g., `last_news_digest: "YYYY-MM-DD"`)
7. Log in `memory/YYYY-MM-DD.md`

---

## Article Templates

### 📰 Daily Digest

```
📰 _Yesterday Daily -- [Weekday], [DD. Month YYYY]_

--

🏠 _Intern bei Yesterday_

• _[Title]_ -- [1-2 sentence summary]. <URL|→ Details>
[If no internal news: "Ruhiger Tag intern -- keine nennenswerten Updates."]

--

🌐 _Tech & AI News_

• _[Title]_ ([Source], [DD.MM.])
  [2-3 sentences: what happened + why it matters for us]
  <URL|→ Quelle>

[Repeat for top 5-7 external items, sorted by score descending]

--

_Kuratiert von [Agent Name] 🐾 | Quellen: [X] geprüft, [Y] relevant_
```

**Rules:**
- Internal section ALWAYS comes first, NEVER skip it
- Each item: source name, date, working link
- Max 8 items total -- this is a digest, not a dump
- Inbox items with drafts: insert the draft text verbatim in the appropriate section

### ⚡ Breaking News

For single high-impact events that can't wait (score ≥ 9, at least 2 sources).

```
⚡ *Breaking: [Headline]*

[3-5 sentences: what happened with concrete details]

*Warum das wichtig ist:*
[2-3 sentences connecting to team's work]

*Quellen:*
• <URL1|[Source 1]> ([Date])
• <URL2|[Source 2]> ([Date])

_[Agent Name] 🐾 | [Timestamp]_
```

Max 1 breaking news per day. Multiple breaking items → bundle into urgent daily digest.

### 🐾 Skill / Feature Announcement

```
🐾 *Neuer Skill: [Name] -- [One-line description]*

[2-3 sentences: what it does, what problem it solves]

*Was steckt drin:*
• [Capability 1] -- [brief description]
• [Capability 2] -- [brief description]

*Warum das wichtig ist:*
[1-2 sentences: concrete benefit for the team]

→ <URL|Zum Skill>
```

Keep under 200 words. Focus on value, not implementation.

### 🏆 Milestone Update

```
🏆 *Milestone: [What was achieved]*

[2-3 sentences: significance of the achievement]

*Key Facts:*
• [Measurable detail]
• [Measurable detail]
• [What's next]

_[Agent Name] 🐾_
```

Only for genuine milestones, not routine progress.

### 📊 Weekly Recap

```
📊 _Yesterday Weekly -- KW [XX] ([DD.MM.] - [DD.MM.YYYY])_

--

🏠 _Diese Woche intern_

• _[Project/Theme]_ -- [Week summary]. <URL|→ Details>
[Group by project, not by day]

--

🌐 _Die wichtigsten Tech-News der Woche_

1. _[Title]_ ([Source], [DD.MM.])
   [Summary + relevance]
   <URL|→ Quelle>

[Top 5-8 items of the entire week, numbered by importance]

--

📈 _Zahlen der Woche_ (optional)
• [Interesting stat]
• [Interesting stat]

--

_KW [XX] Recap von [Agent Name] 🐾 | [X] Quellen ausgewertet_
```

Don't concatenate 5 daily digests -- curate the week's highlights.

---

## Platform Formatting Reference

| Platform | Bold | Italic | Links | Tables | Headers |
|----------|------|--------|-------|--------|---------|
| Slack | `*bold*` | `_italic_` | `<URL\|Text>` | ❌ No | ❌ No |
| Discord | `**bold**` | `*italic*` | `[Text](URL)` or suppress with `<URL>` | ❌ No | ✅ `#` |
| WhatsApp | `*bold*` | `_italic_` | Plain URLs | ❌ No | ❌ Use CAPS |

---

## Quality Checklist (Run Before Every Publish)

- [ ] `news/inbox.json` was read and processed (inbox items included or archived)
- [ ] Every item has a verifiable publication date
- [ ] Every item has a working source link
- [ ] No item is older than the digest's time window
- [ ] Each item has a "why this matters for us" line
- [ ] Internal section is present (even if "quiet day")
- [ ] Platform formatting is correct for the target channel
- [ ] No duplicate topics from yesterday's digest
- [ ] Co-authored drafts are published verbatim (not re-summarized)
- [ ] Total length stays reasonable (daily ≤ 500 words, weekly ≤ 800 words)
- [ ] Language matches channel config (e.g., German for Yesterday)
- [ ] Numeric claims cite a source

---

## Scheduler Integration

**With Heartbeat:**
Add to your `HEARTBEAT.md` or equivalent:
```
1. Check heartbeat-state.json → if last_news_digest == today, SKIP
2. Read news/inbox.json FIRST
3. Run aggregation pipeline
4. Publish, archive inbox, update state
```

**With Cron:**
Create a dedicated cron job that runs the digest pipeline at the configured schedule.
The cron session has NO access to main session memory -- the inbox file is the bridge.

**Key principle:** The inbox is the ONLY handoff between conversational sessions and digest runs.
Everything else (memory files, session context, "mental notes") is unreliable across session
boundaries.

---

## Maintenance

- Archive processed inbox items: `news/archive/inbox_YYYY-MM-DD.json`
- Archive daily raw items: `memory/archive/news_YYYY-MM-DD.md`
- Update `memory/heartbeat-state.json` after each publish
- Review relevance scoring weights quarterly with the team
- Rotate stale RSS sources quarterly
- Monitor inbox for items that were submitted but never published (indicates pipeline bug)

---

*"Signal over Noise. Wisdom over Data."* 📡
