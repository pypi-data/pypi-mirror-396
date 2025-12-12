"""Textual UI for the /accounts command.

Provides a minimal interactive list with the same columns/order as the Rich
fallback (name, API URL, masked key, status) and keyboard navigation.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass

from glaip_sdk.cli.slash.accounts_shared import build_account_status_string
from glaip_sdk.cli.slash.tui.background_tasks import BackgroundTaskMixin
from glaip_sdk.cli.slash.tui.loading import hide_loading_indicator, show_loading_indicator

try:  # pragma: no cover - optional dependency
    from textual import events
    from textual.app import App, ComposeResult
    from textual.binding import Binding
    from textual.containers import Container, Horizontal, Vertical
    from textual.widgets import DataTable, Footer, Header, Input, LoadingIndicator, Static
except Exception:  # pragma: no cover - optional dependency
    events = None  # type: ignore[assignment]
    App = None  # type: ignore[assignment]
    ComposeResult = None  # type: ignore[assignment]
    Binding = None  # type: ignore[assignment]
    Container = None  # type: ignore[assignment]
    Horizontal = None  # type: ignore[assignment]
    Vertical = None  # type: ignore[assignment]
    DataTable = None  # type: ignore[assignment]
    Footer = None  # type: ignore[assignment]
    Header = None  # type: ignore[assignment]
    Input = None  # type: ignore[assignment]
    LoadingIndicator = None  # type: ignore[assignment]
    Static = None  # type: ignore[assignment]

TEXTUAL_SUPPORTED = App is not None and DataTable is not None

# Widget IDs for Textual UI
ACCOUNTS_TABLE_ID = "#accounts-table"
FILTER_INPUT_ID = "#filter-input"
STATUS_ID = "#status"
ACCOUNTS_LOADING_ID = "#accounts-loading"


@dataclass
class AccountsTUICallbacks:
    """Callbacks invoked by the Textual UI."""

    switch_account: Callable[[str], tuple[bool, str]]


def run_accounts_textual(
    rows: list[dict[str, str | bool]],
    *,
    active_account: str | None,
    env_lock: bool,
    callbacks: AccountsTUICallbacks,
) -> None:
    """Launch the Textual accounts browser if dependencies are available."""
    if not TEXTUAL_SUPPORTED:
        return
    app = AccountsTextualApp(rows, active_account, env_lock, callbacks)
    app.run()


class AccountsTextualApp(BackgroundTaskMixin, App[None]):  # pragma: no cover - interactive
    """Textual application for browsing accounts."""

    CSS_PATH = "accounts.tcss"
    BINDINGS = [
        Binding("enter", "switch_row", "Switch", show=True),
        Binding("return", "switch_row", "Switch", show=False),
        Binding("/", "focus_filter", "Filter", show=True),
        # Esc clears filter when focused/non-empty; otherwise exits
        Binding("escape", "clear_or_exit", "Close", priority=True),
        Binding("q", "app_exit", "Close", priority=True),
    ]

    def __init__(
        self,
        rows: list[dict[str, str | bool]],
        active_account: str | None,
        env_lock: bool,
        callbacks: AccountsTUICallbacks,
    ) -> None:
        """Initialize the Textual accounts app.

        Args:
            rows: Account data rows to display.
            active_account: Name of the currently active account.
            env_lock: Whether environment credentials are locking account switching.
            callbacks: Callbacks for account switching operations.
        """
        super().__init__()
        self._all_rows = rows
        self._active_account = active_account
        self._env_lock = env_lock
        self._callbacks = callbacks
        self._filter_text: str = ""
        self._is_switching = False

    def compose(self) -> ComposeResult:
        """Build the Textual layout."""
        header_text = self._header_text()
        yield Static(header_text, id="header-info")
        if self._env_lock:
            yield Static(
                "Env credentials detected (AIP_API_URL/AIP_API_KEY); switching is disabled.",
                id="env-lock",
            )
        filter_bar = Container(
            Static("Filter (/):", id="filter-label"),
            Input(placeholder="Type to filter by name or host", id="filter-input"),
            id="filter-container",
        )
        filter_bar.styles.padding = (0, 0)
        main = Vertical(
            filter_bar,
            DataTable(id=ACCOUNTS_TABLE_ID.lstrip("#")),
        )
        # Avoid large gaps; keep main content filling available space
        main.styles.height = "1fr"
        main.styles.padding = (0, 0)
        yield main
        yield Horizontal(
            LoadingIndicator(id=ACCOUNTS_LOADING_ID.lstrip("#")),
            Static("", id=STATUS_ID.lstrip("#")),
            id="status-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Configure table columns and load rows."""
        table = self.query_one(ACCOUNTS_TABLE_ID, DataTable)
        table.add_column("Name", width=20)
        table.add_column("API URL", width=40)
        table.add_column("Key (masked)", width=20)
        table.add_column("Status", width=14)
        table.cursor_type = "row"
        table.zebra_stripes = True
        table.styles.height = "1fr"  # Fill available space below the filter
        table.styles.margin = 0
        self._reload_rows()
        table.focus()
        # Keep the filter tight to the table
        main = self.query_one(Vertical)
        main.styles.gap = 0

    def _header_text(self) -> str:
        """Build header text with active account and host."""
        host = self._get_active_host() or "Not configured"
        lock_icon = " [yellow]🔒[/]" if self._env_lock else ""
        active = self._active_account or "None"
        return f"[green]Active:[/] [bold]{active}[/] ([cyan]{host}[/]){lock_icon}"

    def _get_active_host(self) -> str | None:
        """Return the API host for the active account (shortened)."""
        return self._get_host_for_name(self._active_account)

    def _get_host_for_name(self, name: str | None) -> str | None:
        """Return shortened API URL for a given account name."""
        if not name:
            return None
        for row in self._all_rows:
            if row.get("name") == name:
                url = str(row.get("api_url", ""))
                return url if len(url) <= 40 else f"{url[:37]}..."
        return None

    def action_focus_filter(self) -> None:
        """Focus the filter input and clear previous text."""
        filter_input = self.query_one(FILTER_INPUT_ID, Input)
        filter_input.value = self._filter_text
        filter_input.focus()

    def action_switch_row(self) -> None:
        """Switch to the currently selected account."""
        if self._env_lock:
            self._set_status("Switching disabled: env credentials in use.", "yellow")
            return
        table = self.query_one(ACCOUNTS_TABLE_ID, DataTable)
        if table.cursor_row is None:
            self._set_status("No account selected.", "yellow")
            return
        try:
            row_key = table.get_row_at(table.cursor_row)[0]
        except Exception:
            self._set_status("Unable to read selected row.", "red")
            return
        name = str(row_key)
        if self._is_switching:
            self._set_status("Already switching...", "yellow")
            return
        self._is_switching = True
        host = self._get_host_for_name(name)
        if host:
            self._show_loading(f"Connecting to '{name}' ({host})...")
        else:
            self._show_loading(f"Connecting to '{name}'...")
        self._queue_switch(name)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:  # type: ignore[override]
        """Handle mouse click selection by triggering switch."""
        table = self.query_one(ACCOUNTS_TABLE_ID, DataTable)
        try:
            # Move cursor to clicked row then switch
            table.cursor_coordinate = (event.cursor_row, 0)
        except Exception:
            return
        self.action_switch_row()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Apply filter when user presses Enter inside filter input."""
        self._filter_text = (event.value or "").strip()
        self._reload_rows()
        table = self.query_one(ACCOUNTS_TABLE_ID, DataTable)
        table.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Apply filter live as the user types."""
        self._filter_text = (event.value or "").strip()
        self._reload_rows()

    def on_key(self, event: events.Key) -> None:  # type: ignore[override]
        """Let users start typing to filter without pressing '/' first."""
        if not getattr(event, "is_printable", False):
            return
        if not event.character:
            return
        filter_input = self.query_one(FILTER_INPUT_ID, Input)
        if filter_input.has_focus:
            return
        filter_input.focus()
        filter_input.value = (filter_input.value or "") + event.character
        filter_input.cursor_position = len(filter_input.value)
        self._filter_text = filter_input.value.strip()
        self._reload_rows()
        event.stop()

    def _reload_rows(self) -> None:
        """Refresh table rows based on current filter/active state."""
        # Work on a copy to avoid mutating the backing rows list
        rows_copy = [dict(row) for row in self._all_rows]
        for row in rows_copy:
            row["active"] = row.get("name") == self._active_account

        table = self.query_one(ACCOUNTS_TABLE_ID, DataTable)
        table.clear()
        filtered = self._filtered_rows(rows_copy)
        for row in filtered:
            row_for_status = dict(row)
            row_for_status["active"] = row_for_status.get("name") == self._active_account
            # Use markup to align status colors with Rich fallback (green active badge).
            status = build_account_status_string(row_for_status, use_markup=True)
            # pylint: disable=duplicate-code
            # Reuses shared status builder; columns mirror accounts_controller Rich table.
            table.add_row(
                str(row.get("name", "")),
                str(row.get("api_url", "")),
                str(row.get("masked_key", "")),
                status,
            )
        # Move cursor to active or first row
        cursor_idx = 0
        for idx, row in enumerate(filtered):
            if row.get("name") == self._active_account:
                cursor_idx = idx
                break
        if filtered:
            table.cursor_coordinate = (cursor_idx, 0)
        else:
            self._set_status("No accounts match the current filter.", "yellow")
            return

        # Update status to reflect filter state
        if self._filter_text:
            self._set_status(f"Filtered: {self._filter_text}", "cyan")
        else:
            self._set_status("", "white")

    def _filtered_rows(self, rows: list[dict[str, str | bool]] | None = None) -> list[dict[str, str | bool]]:
        """Return rows filtered by name or API URL substring."""
        base_rows = rows if rows is not None else [dict(row) for row in self._all_rows]
        if not self._filter_text:
            return list(base_rows)
        needle = self._filter_text.lower()
        filtered = [
            row
            for row in base_rows
            if needle in str(row.get("name", "")).lower() or needle in str(row.get("api_url", "")).lower()
        ]

        # Sort so name matches surface first, then URL matches, then alphabetically
        def score(row: dict[str, str | bool]) -> tuple[int, str]:
            name = str(row.get("name", "")).lower()
            url = str(row.get("api_url", "")).lower()
            name_hit = needle in name
            url_hit = needle in url
            # Extract nested conditional into clear statement
            if name_hit:
                priority = 0
            elif url_hit:
                priority = 1
            else:
                priority = 2
            return (priority, name)

        return sorted(filtered, key=score)

    def _set_status(self, message: str, style: str) -> None:
        """Update status line with message."""
        status = self.query_one(STATUS_ID, Static)
        status.update(f"[{style}]{message}[/]")

    def _show_loading(self, message: str | None = None) -> None:
        """Show the loading indicator and optional status message."""
        show_loading_indicator(self, ACCOUNTS_LOADING_ID, message=message, set_status=self._set_status)

    def _hide_loading(self) -> None:
        """Hide the loading indicator."""
        hide_loading_indicator(self, ACCOUNTS_LOADING_ID)

    def _queue_switch(self, name: str) -> None:
        """Run switch in background to keep UI responsive."""

        async def perform() -> None:
            try:
                switched, message = await asyncio.to_thread(self._callbacks.switch_account, name)
            except Exception as exc:  # pragma: no cover - defensive
                self._set_status(f"Switch failed: {exc}", "red")
                return
            finally:
                self._hide_loading()
                self._is_switching = False

            if switched:
                self._active_account = name
                self._set_status(message or f"Switched to '{name}'.", "green")
                self._update_header()
                self._reload_rows()
            else:
                self._set_status(message or "Switch failed; kept previous account.", "yellow")

        try:
            self.track_task(perform(), logger=logging.getLogger(__name__))
        except Exception as exc:
            # If scheduling the task fails, clear loading/switching state and surface the error.
            self._hide_loading()
            self._is_switching = False
            self._set_status(f"Switch failed to start: {exc}", "red")
            logging.getLogger(__name__).debug("Failed to schedule switch task", exc_info=exc)

    def _update_header(self) -> None:
        """Refresh header text to reflect active/lock state."""
        header = self.query_one("#header-info", Static)
        header.update(self._header_text())

    def action_clear_or_exit(self) -> None:
        """Clear filter when focused/non-empty; otherwise exit.

        UX note: helps users reset the list without leaving the TUI.
        """
        filter_input = self.query_one(FILTER_INPUT_ID, Input)
        # Extract nested conditional into clear statement
        should_clear = filter_input.has_focus and (filter_input.value or self._filter_text)
        if should_clear:
            filter_input.value = ""
            self._filter_text = ""
            self._reload_rows()
            table = self.query_one(ACCOUNTS_TABLE_ID, DataTable)
            table.focus()
            return
        self.exit()
