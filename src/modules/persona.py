"""
Persona loader for human-mcp.

Loads YAML persona files from a persona directory and provides
structured access to each module's data.
"""

import yaml
from pathlib import Path
from typing import Any


MODULE_FILES = {
    "identity": "identity.yaml",
    "projects": "projects.yaml",
    "calendar": "calendar.yaml",
    "contacts": "contacts.yaml",
    "writing_style": "writing-style.yaml",
    "reading_list": "reading-list.yaml",
}


class Persona:
    def __init__(self, persona_dir: Path):
        self.persona_dir = persona_dir
        self.data: dict[str, Any] = {}
        self._load()

    def _load(self):
        for module_name, filename in MODULE_FILES.items():
            filepath = self.persona_dir / filename
            if filepath.exists():
                with open(filepath) as f:
                    raw = yaml.safe_load(f)
                    self.data[module_name] = raw

    def get_module(self, module: str) -> Any:
        """Get raw data for a module."""
        return self.data.get(module)

    def get_identity(self) -> dict[str, Any]:
        return self.data.get("identity", {})

    def get_projects(self) -> list[dict[str, Any]]:
        raw = self.data.get("projects", {})
        return raw.get("projects", []) if isinstance(raw, dict) else []

    def get_calendar(self) -> list[dict[str, Any]]:
        raw = self.data.get("calendar", {})
        return raw.get("events", []) if isinstance(raw, dict) else []

    def get_contacts(self) -> list[dict[str, Any]]:
        raw = self.data.get("contacts", {})
        return raw.get("contacts", []) if isinstance(raw, dict) else []

    def get_writing_style(self) -> dict[str, Any]:
        return self.data.get("writing_style", {})

    def get_reading_list(self) -> list[dict[str, Any]]:
        raw = self.data.get("reading_list", {})
        return raw.get("reading_list", []) if isinstance(raw, dict) else []

    @property
    def name(self) -> str:
        identity = self.get_identity()
        return identity.get("name", "Unknown")

    def available_modules(self) -> list[str]:
        return list(self.data.keys())
