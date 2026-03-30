# human-mcp

A person-centric MCP server. Your context, your rules.

---

## This is a thought experiment

This project explores what it would look like if your personal context for AI tools lived on a server *you* control — portable across LLM clients, scoped by permission tiers, and fully auditable.

Everything here uses synthetic data. "John Doe" is a fictional persona at a fictional company. The reference code demonstrates what the architecture would look like, not something you should run with real data.

**[View the interactive demo →](https://dvelton.github.io/human-mcp/)**

---

## Risks and limitations

Read this section before doing anything else.

**This is a concept demonstration only. It is not designed, tested, or intended for use with real personal data.** The code exists to illustrate an architecture and provoke discussion about person-centric AI context. If someone were to build this for real, the following risks would need to be addressed:

**Data leaves your machine.** When an MCP client connects to this server and queries your data, that data is sent to whichever LLM the client is using. If that's a cloud-hosted model (Claude, ChatGPT, Copilot, Gemini), your personal context now lives on that provider's infrastructure — in their inference pipeline, their logs, and potentially their debug systems. The MCP server controls what leaves your machine, but once it leaves, your control ends.

**Prompt injection is an unsolved problem.** If your persona data includes content from external sources (emails others sent you, issue comments, web pages), an attacker could embed instructions in that content. The LLM would process those instructions alongside your personal context, potentially causing it to exfiltrate data from other modules. This is not a theoretical risk — it's a well-documented attack vector across the MCP ecosystem.

**Data synthesis amplifies exposure.** Individual data points can be innocuous on their own. But giving an LLM simultaneous access to your calendar, projects, contacts, and communication patterns lets it infer things no single source reveals — strategic priorities, relationship dynamics, upcoming organizational changes. The combination is more sensitive than the parts. Permission scoping per-module does not fully address this.

**MCP client authentication is immature.** Most local MCP setups (including stdio transport) have no authentication. Any process that can talk to the server can call its tools. The MCP spec supports OAuth 2.1, but few local implementations use it. This server does not implement authentication.

**Conversation persistence re-exposes your data.** LLM conversation histories often include tool call results. Your "ephemeral" MCP context can end up as a permanent record in a cloud-hosted chat log you don't fully control.

**Scope creep is a real risk.** The initial setup might be carefully scoped. Over time, users tend to add more data sources without revisiting what's already exposed. This project includes an audit log to help with visibility, but it requires you to actually review it.

---

## What problem does this address

Today, personal context for LLMs is:

- **Vendor-locked.** Your Claude custom instructions are useless in ChatGPT. Your ChatGPT memory doesn't follow you to Copilot. Switch tools, lose context.
- **Static.** Custom instructions are text you write once and occasionally update. They don't reflect what you're actually working on right now.
- **All-or-nothing.** The model sees everything in your custom instructions, or nothing. No per-module scoping, no permission tiers.
- **Unauditable.** No vendor tells you how your context was used, what was accessed, or when.

A person-centric MCP server addresses these gaps by making personal context portable, queryable, permission-scoped, and observable.

---

## How it works

The server exposes six modules of persona data, each queryable through MCP tools:

| Module | What it contains |
|--------|-----------------|
| Identity | Name, role, expertise, communication preferences |
| Projects | Active work — names, status, priorities, blockers |
| Calendar | Weekly schedule — meetings, attendees, prep notes |
| Contacts | Key collaborators and relationship context |
| Writing Style | Tone, structure preferences, sample communications |
| Reading List | Books, articles, whitepapers being read or queued |

Every tool accepts a `tier` parameter that controls exposure:

| Tier | What the LLM sees |
|------|-------------------|
| **full** | All fields, no redaction |
| **standard** | Core fields only — no meeting notes, no contact details, no writing samples |
| **minimal** | Bare minimum — names and times, nothing contextual. Contacts fully redacted. |

Every tool call is logged to a local audit file with timestamps, exposed fields, and redacted fields.

---

## What the reference code demonstrates

The `src/` directory contains a working reference implementation using Python and FastMCP. This code exists to make the architecture concrete and inspectable — to show how permission filtering, audit logging, and module-based data serving would work in practice. It is not intended to be deployed or used with real data.

The reference server exposes these tools (all operating on John Doe's synthetic data):

| Tool | What it demonstrates |
|------|---------------------|
| `get_identity(tier)` | Serving identity data at different permission levels |
| `get_projects(tier)` | Project context with field-level redaction |
| `get_calendar(tier)` | Calendar data ranging from full detail to just time blocks |
| `get_contacts(tier)` | Contact data that is fully redacted at minimal tier |
| `get_writing_style(tier)` | Writing preferences with samples restricted to full tier |
| `get_reading_list(tier)` | Reading list with notes stripped at lower tiers |
| `get_audit_log(count)` | Reviewing what data has been exposed |
| `get_audit_summary()` | Aggregate view of all access activity |
| `describe_permissions(module, tier)` | Introspecting what gets exposed vs. redacted |

An example audit log entry:

```json
{
  "timestamp": "2026-03-30T17:14:02+00:00",
  "tool": "get_calendar",
  "module": "calendar",
  "tier": "standard",
  "exposed_fields": ["date", "start", "end", "title", "type"],
  "redacted_fields": ["attendees", "location", "notes"],
  "record_count": 10
}
```

---

## Project structure

```
human-mcp/
├── README.md
├── permissions.yaml            # Permission tier definitions
├── personas/
│   └── john-doe/               # Synthetic persona data
│       ├── identity.yaml
│       ├── projects.yaml
│       ├── calendar.yaml
│       ├── contacts.yaml
│       ├── writing-style.yaml
│       └── reading-list.yaml
├── src/
│   ├── server.py               # MCP server (FastMCP)
│   ├── permissions.py          # Permission engine
│   ├── audit.py                # Audit logger
│   └── modules/
│       └── persona.py          # Persona data loader
├── audit-log/                  # Local audit trail
└── docs/
    └── index.html              # GitHub Pages interactive demo
```

---

## License

MIT
