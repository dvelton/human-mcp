"""
Permission engine for human-mcp.

Loads permission tiers from permissions.yaml and applies field-level
filtering and redaction to persona data before it reaches the LLM.
"""

import yaml
from pathlib import Path
from typing import Any


class PermissionEngine:
    def __init__(self, config_path: Path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.default_tier = self.config.get("default_tier", "standard")

    def get_tier(self, tier: str | None = None) -> str:
        tier = tier or self.default_tier
        if tier not in ("full", "standard", "minimal"):
            return self.default_tier
        return tier

    def filter_record(self, module: str, record: dict[str, Any], tier: str) -> dict[str, Any]:
        """Filter a single record based on module permissions for the given tier."""
        module_config = self.config.get("modules", {}).get(module)
        if not module_config:
            return record

        tier_config = module_config.get(tier)
        if not tier_config:
            return record

        exposed_fields = set(tier_config.get("expose", []))
        transforms = tier_config.get("transform", {})

        if not exposed_fields:
            note = tier_config.get("note", "No data available at this permission tier.")
            return {"_redacted": True, "_note": note}

        filtered = {}
        for key, value in record.items():
            if key in exposed_fields:
                if key in transforms:
                    filtered[key] = transforms[key]
                else:
                    filtered[key] = value

        return filtered

    def filter_data(self, module: str, data: Any, tier: str | None = None) -> Any:
        """Apply permission filtering to module data."""
        tier = self.get_tier(tier)

        if isinstance(data, list):
            return [self.filter_record(module, item, tier) for item in data]
        elif isinstance(data, dict):
            return self.filter_record(module, data, tier)
        return data

    def describe_exposure(self, module: str, tier: str | None = None) -> dict[str, Any]:
        """Describe what gets exposed and redacted for a module at a given tier."""
        tier = self.get_tier(tier)
        module_config = self.config.get("modules", {}).get(module, {})
        tier_config = module_config.get(tier, {})

        return {
            "module": module,
            "tier": tier,
            "exposed_fields": tier_config.get("expose", []),
            "redacted_fields": tier_config.get("redact", []),
            "transforms": tier_config.get("transform", {}),
            "note": tier_config.get("note"),
        }
