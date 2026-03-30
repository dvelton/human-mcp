"""
Audit logger for human-mcp.

Records every data exposure event to a local log file.
Every time the MCP server returns persona data to a client,
the audit logger captures what was exposed, what was redacted,
and when it happened.
"""

import json
import datetime
from pathlib import Path
from typing import Any


class AuditLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit.jsonl"
        self.entries: list[dict[str, Any]] = []

    def log(
        self,
        tool_name: str,
        module: str,
        tier: str,
        exposed_fields: list[str],
        redacted_fields: list[str],
        record_count: int = 1,
    ) -> dict[str, Any]:
        """Log a data exposure event and return the entry."""
        entry = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tool": tool_name,
            "module": module,
            "tier": tier,
            "exposed_fields": exposed_fields,
            "redacted_fields": redacted_fields,
            "record_count": record_count,
        }

        self.entries.append(entry)

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_recent(self, count: int = 20) -> list[dict[str, Any]]:
        """Return recent audit entries from the in-memory log."""
        return self.entries[-count:]

    def get_all_from_file(self) -> list[dict[str, Any]]:
        """Read all entries from the persistent log file."""
        if not self.log_file.exists():
            return []
        entries = []
        with open(self.log_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def get_summary(self) -> dict[str, Any]:
        """Summarize audit activity."""
        entries = self.get_all_from_file()
        if not entries:
            return {"total_requests": 0, "modules_accessed": [], "tiers_used": []}

        modules = set()
        tiers = set()
        for entry in entries:
            modules.add(entry.get("module", "unknown"))
            tiers.add(entry.get("tier", "unknown"))

        return {
            "total_requests": len(entries),
            "modules_accessed": sorted(modules),
            "tiers_used": sorted(tiers),
            "earliest": entries[0].get("timestamp"),
            "latest": entries[-1].get("timestamp"),
        }
