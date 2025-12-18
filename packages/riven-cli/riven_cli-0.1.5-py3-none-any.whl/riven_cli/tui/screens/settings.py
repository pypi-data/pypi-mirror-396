import asyncio
import readchar
import ast
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich import box
from rich.console import Group

from riven_cli.config import settings, CONFIG_FILE
from riven_cli.api import client


class SettingsScreen:
    def __init__(self, app):
        self.app = app
        self.active_tab = "local"  # "local" or "backend"

        # Local Settings State
        self.local_items = ["api_url", "api_key"]

        # Backend Settings State
        self.backend_items: list[
            dict
        ] = []  # List of {"key": str, "value": Any, "type": str}
        self.loading = False
        self.error = None

        # Navigation & Editing
        self.selected_index = 0
        self.scroll_offset = 0
        self.edit_mode = False
        self.input_buffer = ""
        self.cursor_position = 0  # Cursor position in input_buffer
        self.message = None

    async def on_mount(self):
        pass

    async def fetch_backend_settings(self):
        self.loading = True
        self.error = None
        self.message = None

        try:
            async with client as c:
                data = await c.get_all_settings()
                self.backend_items = self._flatten_settings(data)
        except Exception as e:
            self.error = str(e)
            self.backend_items = []
        finally:
            self.loading = False

    def _flatten_settings(self, data: dict, parent_key: str = "") -> list[dict]:
        items = []
        for k, v in data.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_settings(v, new_key))
            else:
                items.append({"key": new_key, "value": v, "type": type(v).__name__})
        return items

    def _unflatten_settings(self, items: list[dict]) -> dict:
        result = {}
        for item in items:
            keys = item["key"].split(".")
            current = result
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = item["value"]
        return result

    async def save_backend_setting(self):
        if not self.backend_items:
            return

        payload = self._unflatten_settings(self.backend_items)

        count = len(self.backend_items)
        self.message = f"[yellow]Saving {count} settings...[/yellow]"
        try:
            async with client as c:
                await c.set_all_settings(payload)
            self.message = "[green]Successfully saved all backend settings![/green]"
        except Exception as e:
            self.message = f"[red]Save Failed: {str(e)}[/red]"

    def render(self) -> Layout:
        # Header
        header_text = Text()
        header_text.append("Riven CLI - Settings", style="bold green")
        header_text.append(f" | Tab: {self.active_tab.upper()}", style="cyan")
        header = Panel(Align.center(header_text), style="blue")

        # Body
        if self.loading:
            body_content = Align.center(
                Text("Loading settings...", style="yellow blink")
            )
        elif self.error:
            body_content = Align.center(Text(f"Error:\n{self.error}", style="bold red"))
        elif self.edit_mode:
            body_content = self._render_edit_panel()
        elif self.active_tab == "local":
            body_content = self._render_local_tab()
        else:
            body_content = self._render_backend_tab()

        # Status Message
        final_body = []
        if self.message:
            final_body.append(
                Panel(Text.from_markup(self.message), style="bold yellow")
            )
        final_body.append(body_content)

        body = Group(*final_body)

        # Footer
        footer_text = Text()
        if self.edit_mode:
            footer_text.append("[Enter] Save  ", style="bold green")
            footer_text.append("[Ctrl+Q] Cancel", style="bold red")
        else:
            footer_text.append("[Q] Back  ", style="bold red")
            footer_text.append("[TAB] Switch Tab  ", style="bold white")
            footer_text.append("[Enter] Edit  ", style="bold yellow")
            footer_text.append("[S] Save", style="bold green")

        footer = Panel(Align.center(footer_text), title="Actions")

        layout = Layout()
        layout.split(Layout(header, size=3), Layout(body), Layout(footer, size=3))
        return layout

    def _render_local_tab(self):
        table = Table(box=box.SIMPLE, expand=True)
        table.add_column("Setting", width=20)
        table.add_column("Value", ratio=1)

        # API URL
        style_url = "reverse" if self.selected_index == 0 else ""
        table.add_row("API URL", settings.api_url, style=style_url)

        # API Key
        style_key = "reverse" if self.selected_index == 1 else ""
        key_display = "*" * 8 + settings.api_key[-4:] if settings.api_key else "Not Set"
        table.add_row("API Key", key_display, style=style_key)

        return Panel(table, title=f"Local Configuration ({CONFIG_FILE})")

    def _render_backend_tab(self):
        if not self.backend_items:
            return Align.center(
                Text("No settings found or not loaded.", style="yellow")
            )

        table = Table(box=box.SIMPLE, expand=True)
        table.add_column("Key", ratio=1)
        table.add_column("Value", ratio=1)
        table.add_column("Type", width=10)

        # Viewport Logic
        available_rows = max(5, self.app.console.size.height - 10)

        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + available_rows:
            self.scroll_offset = self.selected_index - available_rows + 1

        self.scroll_offset = max(
            0, min(self.scroll_offset, len(self.backend_items) - available_rows)
        )

        visible_items = self.backend_items[
            self.scroll_offset : self.scroll_offset + available_rows
        ]

        for i, item in enumerate(visible_items):
            # Calculate actual index
            actual_index = self.scroll_offset + i
            is_selected = actual_index == self.selected_index
            style = "reverse" if is_selected else ""

            value_str = str(item["value"])
            if item["type"] == "bool":
                value_str = "True" if item["value"] else "False"
            else:
                # Check if dirty
                original = self.backend_items[actual_index].get("original_value")
                if original is not None and original != item["value"]:
                    value_str += " *"
                    style += " bold yellow"

            table.add_row(item["key"], value_str, item["type"], style=style)

        return Panel(table, title=f"Backend Settings ({len(self.backend_items)} items)")

    def _render_edit_panel(self):
        edit_title = ""
        if self.active_tab == "local":
            edit_title = "API URL" if self.selected_index == 0 else "API Key"
        else:
            edit_title = self.backend_items[self.selected_index]["key"]

        # Show cursor at correct position
        before_cursor = self.input_buffer[: self.cursor_position]
        after_cursor = self.input_buffer[self.cursor_position :]
        display_text = Text()
        display_text.append(before_cursor, style="bold white")
        display_text.append("█", style="bold cyan blink")
        display_text.append(after_cursor, style="bold white")

        input_panel = Panel(
            Align.center(display_text),
            title=f"Editing: {edit_title}",
            style="yellow",
            border_style="red",
            padding=(2, 2),
        )
        return Align.center(input_panel, vertical="middle")

    async def handle_input(self, key: str):
        if self.edit_mode:
            await self._handle_edit_input(key)
            return

        # Navigation
        if key.lower() == "q":
            self.app.switch_to("dashboard")
            return
        elif key == readchar.key.TAB:
            self.active_tab = "backend" if self.active_tab == "local" else "local"
            self.selected_index = 0
            self.scroll_offset = 0
            self.message = None
            if self.active_tab == "backend" and not self.backend_items:
                asyncio.create_task(self.fetch_backend_settings())

        elif key == readchar.key.DOWN or key == "j":
            max_idx = 1 if self.active_tab == "local" else len(self.backend_items) - 1
            if self.selected_index < max_idx:
                self.selected_index += 1

        elif key == readchar.key.UP or key == "k":
            if self.selected_index > 0:
                self.selected_index -= 1

        elif key == readchar.key.ENTER:
            self._enter_edit_mode()

        elif key.lower() == "s":
            if self.active_tab == "local":
                settings.save()
                self.message = "[green]Local settings saved![/green]"
            else:
                await self.save_backend_setting()

    def _enter_edit_mode(self):
        self.edit_mode = True
        self.message = None

        if self.active_tab == "local":
            if self.selected_index == 0:
                self.input_buffer = settings.api_url
            else:
                self.input_buffer = settings.api_key or ""
        else:
            if self.backend_items:
                val = self.backend_items[self.selected_index]["value"]
                self.input_buffer = str(val)

        # Position cursor at end of buffer
        self.cursor_position = len(self.input_buffer)

    async def _handle_edit_input(self, key: str):
        if key == readchar.key.ENTER:
            self.edit_mode = False
            await self._save_edit_value()
        elif key == readchar.key.CTRL_Q:
            self.edit_mode = False
            self.input_buffer = ""
            self.cursor_position = 0
        elif key == readchar.key.LEFT:
            # Move cursor left
            if self.cursor_position > 0:
                self.cursor_position -= 1
        elif key == readchar.key.RIGHT:
            # Move cursor right
            if self.cursor_position < len(self.input_buffer):
                self.cursor_position += 1
        elif key == readchar.key.BACKSPACE:
            # Delete character before cursor
            if self.cursor_position > 0:
                self.input_buffer = (
                    self.input_buffer[: self.cursor_position - 1]
                    + self.input_buffer[self.cursor_position :]
                )
                self.cursor_position -= 1
        elif len(key) == 1 and key.isprintable():
            # Insert character at cursor position
            self.input_buffer = (
                self.input_buffer[: self.cursor_position]
                + key
                + self.input_buffer[self.cursor_position :]
            )
            self.cursor_position += 1

    async def _save_edit_value(self):
        new_val = self.input_buffer

        if self.active_tab == "local":
            if self.selected_index == 0:
                settings.api_url = new_val
            else:
                settings.api_key = new_val
            self.message = (
                "[yellow]Value updated locally. Press S to save to file.[/yellow]"
            )
        else:
            # Backend
            item = self.backend_items[self.selected_index]
            original_type = item["type"]

            # Basic type conversion
            try:
                if original_type == "int":
                    converted_val = int(new_val)
                elif original_type == "float":
                    converted_val = float(new_val)
                elif original_type == "bool":
                    converted_val = new_val.lower() in ["true", "1", "yes"]
                elif original_type == "list":
                    # Parse list from string representation
                    converted_val = ast.literal_eval(new_val)
                    if not isinstance(converted_val, list):
                        raise ValueError("Not a valid list")
                else:
                    converted_val = new_val

                item["value"] = converted_val
                self.message = "[yellow]Value updated in memory. Press S to push to backend.[/yellow]"

            except (ValueError, SyntaxError):
                self.message = (
                    "[red]Invalid format for type " + original_type + "[/red]"
                )
