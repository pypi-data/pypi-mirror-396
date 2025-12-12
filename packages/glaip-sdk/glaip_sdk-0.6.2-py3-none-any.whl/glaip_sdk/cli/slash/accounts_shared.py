"""Shared helpers for palette `/accounts`.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any


def build_account_status_string(row: dict[str, Any], *, use_markup: bool = False) -> str:
    """Build status string for an account row (active/env-lock)."""
    status_parts: list[str] = []
    if row.get("active"):
        status_parts.append("[bold green]● active[/]" if use_markup else "● active")
    if row.get("env_lock"):
        status_parts.append("[yellow]🔒 env-lock[/]" if use_markup else "🔒 env-lock")
    return " · ".join(status_parts)
