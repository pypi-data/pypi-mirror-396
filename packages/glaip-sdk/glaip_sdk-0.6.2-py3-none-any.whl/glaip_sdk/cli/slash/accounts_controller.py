"""Accounts controller for the /accounts slash command.

Provides a lightweight Textual list with fallback Rich snapshot to switch
between stored accounts using the shared AccountStore and CLI validation.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from rich.console import Console

from glaip_sdk.branding import ERROR_STYLE, INFO_STYLE, SUCCESS_STYLE, WARNING_STYLE
from glaip_sdk.cli.account_store import AccountStore, AccountStoreError, get_account_store
from glaip_sdk.cli.commands.common_config import check_connection_with_reason
from glaip_sdk.cli.masking import mask_api_key_display
from glaip_sdk.cli.slash.accounts_shared import build_account_status_string
from glaip_sdk.cli.slash.tui.accounts_app import TEXTUAL_SUPPORTED, AccountsTUICallbacks, run_accounts_textual
from glaip_sdk.rich_components import AIPPanel, AIPTable

if TYPE_CHECKING:  # pragma: no cover
    from glaip_sdk.cli.slash.session import SlashSession

TEXTUAL_AVAILABLE = bool(TEXTUAL_SUPPORTED)


class AccountsController:
    """Controller for listing and switching accounts inside the palette."""

    def __init__(self, session: SlashSession) -> None:
        """Initialize the accounts controller.

        Args:
            session: The slash session context.
        """
        self.session = session
        self.console: Console = session.console
        self.ctx = session.ctx

    def handle_accounts_command(self, args: list[str]) -> bool:
        """Handle `/accounts` with optional `/accounts <name>` quick switch."""
        store = get_account_store()
        env_lock = bool(os.getenv("AIP_API_URL") or os.getenv("AIP_API_KEY"))
        accounts = store.list_accounts()

        if not accounts:
            self.console.print(f"[{WARNING_STYLE}]No accounts found. Use `/login` to add credentials.[/]")
            return self.session._continue_session()

        if args:
            name = args[0]
            self._switch_account(store, name, env_lock)
            return self.session._continue_session()

        rows = self._build_rows(accounts, store.get_active_account(), env_lock)

        if self._should_use_textual():
            self._render_textual(rows, store, env_lock)
        else:
            self._render_rich(rows, env_lock)

        return self.session._continue_session()

    def _should_use_textual(self) -> bool:
        """Return whether Textual UI should be used."""
        if not TEXTUAL_AVAILABLE:
            return False

        def _is_tty(stream: Any) -> bool:
            isatty = getattr(stream, "isatty", None)
            if not callable(isatty):
                return False
            try:
                return bool(isatty())
            except Exception:
                return False

        return _is_tty(sys.stdin) and _is_tty(sys.stdout)

    def _build_rows(
        self,
        accounts: dict[str, dict[str, str]],
        active_account: str | None,
        env_lock: bool,
    ) -> list[dict[str, str | bool]]:
        """Normalize account rows for display."""
        rows: list[dict[str, str | bool]] = []
        for name, account in sorted(accounts.items()):
            rows.append(
                {
                    "name": name,
                    "api_url": account.get("api_url", ""),
                    "masked_key": mask_api_key_display(account.get("api_key", "")),
                    "active": name == active_account,
                    "env_lock": env_lock,
                }
            )
        return rows

    def _render_rich(self, rows: Iterable[dict[str, str | bool]], env_lock: bool) -> None:
        """Render a Rich snapshot with columns matching TUI."""
        if env_lock:
            self.console.print(
                f"[{WARNING_STYLE}]Env credentials detected (AIP_API_URL/AIP_API_KEY); switching is disabled.[/]"
            )

        table = AIPTable(title="AIP Accounts")
        table.add_column("Name", style=INFO_STYLE, width=20)
        table.add_column("API URL", style=SUCCESS_STYLE, width=40)
        table.add_column("Key (masked)", style="dim", width=20)
        table.add_column("Status", style=SUCCESS_STYLE, width=14)

        for row in rows:
            status = build_account_status_string(row, use_markup=True)
            # pylint: disable=duplicate-code
            # Similar to accounts_app.py but uses Rich AIPTable API
            table.add_row(
                str(row.get("name", "")),
                str(row.get("api_url", "")),
                str(row.get("masked_key", "")),
                status,
            )

        self.console.print(table)

    def _render_textual(self, rows: list[dict[str, str | bool]], store: AccountStore, env_lock: bool) -> None:
        """Launch the Textual accounts browser."""
        callbacks = AccountsTUICallbacks(switch_account=lambda name: self._switch_account(store, name, env_lock))
        active = next((row["name"] for row in rows if row.get("active")), None)
        run_accounts_textual(rows, active_account=active, env_lock=env_lock, callbacks=callbacks)
        # Exit snapshot: show active account + host after closing the TUI
        active_after = store.get_active_account() or "default"
        host_after = ""
        account_after = store.get_account(active_after) if hasattr(store, "get_account") else None
        if account_after:
            host_after = account_after.get("api_url", "")
        host_suffix = f" • {host_after}" if host_after else ""
        self.console.print(f"[dim]Active account: {active_after}{host_suffix}[/]")
        # Surface a success banner when a switch occurred inside the TUI
        if active_after != active:
            self.console.print(
                AIPPanel(
                    f"[{SUCCESS_STYLE}]Active account ➜ {active_after}[/]{host_suffix}",
                    title="✅ Account Switched",
                    border_style=SUCCESS_STYLE,
                )
            )

    def _switch_account(self, store: AccountStore, name: str, env_lock: bool) -> tuple[bool, str]:
        """Validate and switch active account; returns (success, message)."""
        if env_lock:
            msg = "Env credentials detected (AIP_API_URL/AIP_API_KEY); switching is disabled."
            self.console.print(f"[{WARNING_STYLE}]{msg}[/]")
            return False, msg

        account = store.get_account(name)
        if not account:
            msg = f"Account '{name}' not found."
            self.console.print(f"[{ERROR_STYLE}]{msg}[/]")
            return False, msg

        api_url = account.get("api_url", "")
        api_key = account.get("api_key", "")
        if not api_url or not api_key:
            edit_cmd = f"aip accounts edit {name}"
            msg = f"Account '{name}' is missing credentials. Use `/login` or `{edit_cmd}`."
            self.console.print(f"[{ERROR_STYLE}]{msg}[/]")
            return False, msg

        ok, error_reason = check_connection_with_reason(api_url, api_key, abort_on_error=False)
        if not ok:
            code, detail = self._parse_error_reason(error_reason)
            if code == "connection_failed":
                msg = f"Switch aborted: cannot reach {api_url}. Check URL or network."
            elif code == "api_failed":
                msg = f"Switch aborted: API error for '{name}'. Check credentials."
            else:
                detail_suffix = f": {detail}" if detail else ""
                msg = f"Switch aborted: {code or 'Validation failed'}{detail_suffix}"
            self.console.print(f"[{WARNING_STYLE}]{msg}[/]")
            return False, msg

        try:
            store.set_active_account(name)
            masked_key = mask_api_key_display(api_key)
            self.console.print(
                AIPPanel(
                    f"[{SUCCESS_STYLE}]Active account ➜ {name}[/]\nAPI URL: {api_url}\nKey: {masked_key}",
                    title="✅ Account Switched",
                    border_style=SUCCESS_STYLE,
                )
            )
            return True, f"Switched to '{name}'."
        except AccountStoreError as exc:
            msg = f"Failed to set active account: {exc}"
            self.console.print(f"[{ERROR_STYLE}]{msg}[/]")
            return False, msg
        except Exception as exc:  # NOSONAR(S1045) - catch-all needed for unexpected errors
            msg = f"Unexpected error while switching to '{name}': {exc}"
            self.console.print(f"[{ERROR_STYLE}]{msg}[/]")
            return False, msg

    @staticmethod
    def _parse_error_reason(reason: str | None) -> tuple[str, str]:
        """Parse error reason into (code, detail) to avoid fragile substring checks."""
        if not reason:
            return "", ""
        if ":" in reason:
            code, _, detail = reason.partition(":")
            return code.strip(), detail.strip()
        return reason.strip(), ""
