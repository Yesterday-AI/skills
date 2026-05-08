# Mermaid Patterns for Consulting

Quick-reference for common consulting diagram types using Mermaid syntax.

## When to Use Mermaid

- Diagrams embedded in Markdown docs (GitHub, Obsidian, Notion render natively)
- Quick iteration — no external tools needed
- Version-controlled diagrams (text-based diffs)
- Documentation-first workflows

## Supported Diagram Types

### Flowchart (Process, Decision Trees)
```mermaid
graph TD
    A[Start] --> B{Decision?}
    B -->|Yes| C[Action A]
    B -->|No| D[Action B]
    C --> E[Result]
    D --> E
```

### Sequence (API Calls, User Journeys)
```mermaid
sequenceDiagram
    participant U as User
    participant A as App
    participant DB as Database
    U->>A: Request
    A->>DB: Query
    DB-->>A: Result
    A-->>U: Response
```

### State (Lifecycle, Status Machines)
```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Review: Submit
    Review --> Approved: Accept
    Review --> Draft: Reject
    Approved --> Published: Deploy
    Published --> [*]
```

### Entity-Relationship (Data Models)
```mermaid
erDiagram
    CLIENT ||--o{ PROJECT : has
    PROJECT ||--|{ DELIVERABLE : produces
    CONSULTANT }|--|| PROJECT : works_on
```

### Gantt (Timelines, Roadmaps)
```mermaid
gantt
    title Project Phases
    dateFormat YYYY-MM-DD
    section Discovery
    Interviews    :a1, 2026-01-06, 5d
    Analysis      :a2, after a1, 5d
    section Design
    Architecture  :b1, after a2, 10d
    Prototyping   :b2, after b1, 10d
```

### Quadrant (Prioritization, Effort/Impact)
```mermaid
quadrantChart
    title Initiative Prioritization
    x-axis Low Effort --> High Effort
    y-axis Low Impact --> High Impact
    Automate Onboarding: [0.2, 0.85]
    Rebuild Dashboard: [0.75, 0.9]
    Update Docs: [0.15, 0.3]
    Custom CRM: [0.85, 0.25]
```

### Mindmap (Brainstorming, Topic Exploration)
```mermaid
mindmap
  root((Strategy))
    Growth
      New Markets
      Partnerships
    Efficiency
      Automation
      Process Optimization
    Innovation
      R&D
      AI Integration
```

### C4 Context (System Architecture)
```mermaid
C4Context
    title System Context Diagram
    Person(user, "End User")
    System(core, "Core Platform", "Main application")
    System_Ext(payment, "Payment Gateway", "Stripe")
    System_Ext(email, "Email Service", "SendGrid")
    Rel(user, core, "Uses", "HTTPS")
    Rel(core, payment, "Processes payments")
    Rel(core, email, "Sends notifications")
```

## Styling Tips

- Use `classDef` for semantic coloring:
  ```
  classDef highlight fill:#e1f5fe,stroke:#0288d1
  class A,B highlight
  ```
- Keep labels short (max 4-5 words per node)
- Use `:::` for inline classes: `A[Start]:::highlight`
- Vertical (`TD`) for hierarchies, horizontal (`LR`) for processes

## PNG Export

```bash
# Single file
mmdc -i diagram.md -o diagram.png -t dark -b transparent

# With custom width
mmdc -i diagram.md -o diagram.png -w 1200
```
