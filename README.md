# human-mcp

A person-centric MCP server.

---

## This is a thought experiment

This project explores what it would look like if your personal context for AI tools lived on a server you control, portable across LLM clients, scoped by permission tiers, and fully auditable.

Everything here uses synthetic data. The reference code demonstrates what the architecture could look like, not something you should run with real data.

**[Interactive demo](https://dvelton.github.io/human-mcp/)**

---

## Limitations

**This is a concept project only. It is not designed, tested, or intended for use with real personal data.** The code exists to illustrate an architecture and can be useful for discussion about person-centric AI context. 

---

## What problem does this address

A person-centric MCP server addresses can make personal context portable, queryable, permission-scoped, and observable.

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
