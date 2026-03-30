"""
human-mcp: A person-centric MCP server.

This is the main MCP server that exposes persona data through
permission-scoped tools with full audit logging.
"""

import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

from src.modules.persona import Persona
from src.permissions import PermissionEngine
from src.audit import AuditLogger


PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_PERSONA = PROJECT_ROOT / "personas" / "john-doe"
PERMISSIONS_FILE = PROJECT_ROOT / "permissions.yaml"
AUDIT_DIR = PROJECT_ROOT / "audit-log"

mcp = FastMCP(
    "human-mcp",
    instructions=(
        "This server provides access to a person's context — identity, projects, "
        "calendar, contacts, writing style, and reading list. All data is synthetic "
        "(John Doe is a fictional persona). Data is filtered through permission tiers: "
        "full, standard, or minimal. Use the tier parameter to control exposure level. "
        "Every query is logged in the audit trail."
    ),
)

persona = Persona(DEFAULT_PERSONA)
permissions = PermissionEngine(PERMISSIONS_FILE)
audit = AuditLogger(AUDIT_DIR)


def _serve_module(
    tool_name: str,
    module: str,
    data,
    tier: str | None = None,
) -> str:
    """Filter data through permissions, log the access, return JSON."""
    resolved_tier = permissions.get_tier(tier)
    exposure = permissions.describe_exposure(module, resolved_tier)
    filtered = permissions.filter_data(module, data, resolved_tier)

    record_count = len(filtered) if isinstance(filtered, list) else 1
    audit.log(
        tool_name=tool_name,
        module=module,
        tier=resolved_tier,
        exposed_fields=exposure["exposed_fields"],
        redacted_fields=exposure["redacted_fields"],
        record_count=record_count,
    )

    return json.dumps(filtered, indent=2, default=str)


@mcp.tool()
def get_identity(tier: str | None = None) -> str:
    """Get the persona's identity information — name, role, expertise, preferences.

    Args:
        tier: Permission tier (full, standard, minimal). Controls how much detail is returned.
    """
    return _serve_module("get_identity", "identity", persona.get_identity(), tier)


@mcp.tool()
def get_projects(tier: str | None = None) -> str:
    """Get the persona's active projects — names, status, priorities, blockers.

    Args:
        tier: Permission tier (full, standard, minimal). Controls how much detail is returned.
    """
    return _serve_module("get_projects", "projects", persona.get_projects(), tier)


@mcp.tool()
def get_calendar(tier: str | None = None) -> str:
    """Get the persona's calendar events for the current week.

    Args:
        tier: Permission tier (full, standard, minimal). Controls how much detail is returned.
              At minimal tier, only time blocks are shown (no titles, attendees, or notes).
    """
    return _serve_module("get_calendar", "calendar", persona.get_calendar(), tier)


@mcp.tool()
def get_contacts(tier: str | None = None) -> str:
    """Get the persona's key contacts and collaborators.

    Args:
        tier: Permission tier (full, standard, minimal). Controls how much detail is returned.
              At minimal tier, contacts are fully redacted.
    """
    return _serve_module("get_contacts", "contacts", persona.get_contacts(), tier)


@mcp.tool()
def get_writing_style(tier: str | None = None) -> str:
    """Get the persona's writing style preferences and sample communications.

    Args:
        tier: Permission tier (full, standard, minimal). Controls how much detail is returned.
              Samples are only available at full tier.
    """
    data = persona.get_writing_style()
    resolved_tier = permissions.get_tier(tier)
    exposure = permissions.describe_exposure("writing_style", resolved_tier)

    # Writing style has nested structure — handle top-level and samples separately
    filtered = {}
    exposed_fields = set(exposure["exposed_fields"])

    style_data = data.get("writing_style", {})
    for key, value in style_data.items():
        if key in exposed_fields:
            filtered[key] = value

    if "samples" in exposed_fields:
        filtered["samples"] = data.get("samples", [])

    audit.log(
        tool_name="get_writing_style",
        module="writing_style",
        tier=resolved_tier,
        exposed_fields=exposure["exposed_fields"],
        redacted_fields=exposure["redacted_fields"],
    )

    return json.dumps(filtered, indent=2, default=str)


@mcp.tool()
def get_reading_list(tier: str | None = None) -> str:
    """Get the persona's current reading list — books, articles, whitepapers.

    Args:
        tier: Permission tier (full, standard, minimal). Controls how much detail is returned.
    """
    return _serve_module("get_reading_list", "reading_list", persona.get_reading_list(), tier)


@mcp.tool()
def get_audit_log(count: int = 20) -> str:
    """View the audit trail — see exactly what data has been exposed and when.

    Args:
        count: Number of recent entries to return (default 20).
    """
    recent = audit.get_recent(count)
    return json.dumps(recent, indent=2, default=str)


@mcp.tool()
def get_audit_summary() -> str:
    """Get a summary of all audit activity — total requests, modules accessed, tiers used."""
    summary = audit.get_summary()
    return json.dumps(summary, indent=2, default=str)


@mcp.tool()
def describe_permissions(module: str, tier: str | None = None) -> str:
    """Describe what gets exposed and redacted for a specific module at a given tier.

    Args:
        module: The module to describe (identity, projects, calendar, contacts, writing_style, reading_list).
        tier: Permission tier to describe (full, standard, minimal).
    """
    exposure = permissions.describe_exposure(module, tier)
    return json.dumps(exposure, indent=2, default=str)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
