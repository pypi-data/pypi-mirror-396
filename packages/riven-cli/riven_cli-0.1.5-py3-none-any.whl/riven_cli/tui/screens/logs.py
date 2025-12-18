import asyncio
import json
import pyperclip
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout
from rich.console import Group
import readchar

from riven_cli.api import client


class LogsScreen:
    def __init__(self, app):
        self.app = app
        self.logs: list[str] = []
        self.visible_logs: list[str] = []
        self.active_tab = "live"  # "live" or "historical"
        self.loading = False
        self.error: str | None = None
        self.message: str | None = None
        self.scroll_offset = 0
        self.auto_scroll = True
        self.stream_task: asyncio.Task | None = None
        # self.max_logs = 50000

    async def on_mount(self):
        if self.active_tab == "live":
            await self.start_live_stream()
        else:
            await self.fetch_historical()

    async def start_live_stream(self):
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
            self.stream_task = None

        self.logs = []
        self.error = None
        self.message = None
        self.loading = True
        self.stream_task = asyncio.create_task(self.stream_worker())

    async def stream_worker(self):
        try:
            async with client as c:
                self.loading = False
                async for line in c.stream_logs():
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue

                    if line.startswith("data: "):
                        line = line[6:]

                    try:
                        data = json.loads(line)
                        if isinstance(data, dict):
                            message = data.get("message", str(data))
                            self.add_log(message)
                        else:
                            self.add_log(str(data))
                    except json.JSONDecodeError:
                        if line and line != "data:":
                            self.add_log(line)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.error = f"Stream Error: {str(e)}"
            self.loading = False

    async def fetch_historical(self):
        if self.stream_task:
            self.stream_task.cancel()
            try:
                await self.stream_task
            except asyncio.CancelledError:
                pass
            self.stream_task = None

        self.loading = True
        self.error = None
        self.message = None
        self.logs = []
        self.auto_scroll = False

        try:
            async with client as c:
                response = await c.get_logs()
                data = response.get("data", response)
                logs = data.get("logs", []) if isinstance(data, dict) else []

                for log in logs:
                    msg = (
                        log.get("message", str(log))
                        if isinstance(log, dict)
                        else str(log)
                    )
                    self.add_log(message=msg, update_scroll=False)

            self.scroll_offset = max(0, len(self.logs) - 1)

        except Exception as e:
            self.error = f"Fetch Error: {str(e)}"
        finally:
            self.loading = False

    def add_log(self, message: str, update_scroll=True):
        self.logs.append(message)
        # if len(self.logs) > self.max_logs:
        #     self.logs.pop(0)

        if self.auto_scroll and update_scroll:
            self.scroll_to_bottom()

    def scroll_to_bottom(self):
        self.scroll_offset = max(0, len(self.logs) - 1)

    async def upload_logs(self):
        self.message = "[yellow]Uploading logs...[/yellow]"
        try:
            async with client as c:
                response = await c.upload_logs()
                data = response.get("data", response)
                url = data.get("url")

                if url:
                    try:
                        pyperclip.copy(url)
                        self.message = f"[green]Logs uploaded! URL copied to clipboard: {url}[/green]"
                    except Exception:
                        self.message = f"[green]Logs uploaded! URL: {url}[/green]"
                else:
                    self.message = (
                        f"[red]Upload failed: No URL returned. {str(response)}[/red]"
                    )
        except Exception as e:
            self.message = f"[red]Upload Error: {str(e)}[/red]"

    def render(self) -> Layout:
        # Header
        tabs = [
            ("[L] Live Logs", self.active_tab == "live"),
            ("[H] Historical", self.active_tab == "historical"),
        ]

        header_text = Text()
        for label, is_active in tabs:
            style = "bold green reverse" if is_active else "dim"
            header_text.append(f" {label} ", style=style)
            header_text.append(" ")

        header = Panel(
            Align.center(header_text),
            title="System Logs",
            style="blue",
        )

        # Body
        available_rows = max(
            5, self.app.console.size.height - 12
        )  # Adjusted for subtitle/msg

        if self.loading and not self.logs:
            body_content = Align.center(Text("Loading...", style="yellow blink"))
        elif self.error:
            body_content = Align.center(Text(self.error, style="bold red"))
        else:
            total_logs = len(self.logs)

            if self.auto_scroll:
                start_index = max(0, total_logs - available_rows)
                self.scroll_offset = start_index
            else:
                start_index = self.scroll_offset

            start_index = (
                max(0, min(start_index, total_logs - available_rows))
                if total_logs > available_rows
                else 0
            )

            if not self.auto_scroll and self.scroll_offset != start_index:
                self.scroll_offset = start_index

            end_index = start_index + available_rows
            visible_slice = self.logs[start_index:end_index]

            log_lines = []
            for log in visible_slice:
                log_lines.append(Text(log, style="grey85"))

            title_text = (
                f"Logs ({len(self.logs)}) {'[Auto-Scroll]' if self.auto_scroll else ''}"
            )

            body_content = Panel(
                Align.left(Group(*log_lines)),
                title=title_text,
                subtitle=f"lines {start_index}-{min(end_index, total_logs)}",
            )

        # Message/Notification Area
        final_body = []
        if self.message:
            final_body.append(Panel(Text.from_markup(self.message), style="bold white"))
        final_body.append(body_content)

        # Footer
        footer_text = Text()
        footer_text.append("[Q] Back  ", style="bold red")
        footer_text.append("[L] Live  ", style="bold green")
        footer_text.append("[H] Historical  ", style="bold blue")
        footer_text.append("[U] Upload  ", style="bold magenta")
        if self.active_tab == "live":
            footer_text.append("[Space] Toggle Auto-Scroll  ", style="bold yellow")
        footer_text.append("[Up/Down] Scroll", style="bold white")

        footer = Panel(Align.center(footer_text), title="Actions")

        layout = Layout()
        layout.split(
            Layout(header, size=3), Layout(Group(*final_body)), Layout(footer, size=3)
        )
        return layout

    async def handle_input(self, key: str):
        if key.lower() == "q":
            if self.stream_task:
                self.stream_task.cancel()
            self.app.switch_to("dashboard")
            return

        if key.lower() == "l":
            if self.active_tab != "live":
                self.active_tab = "live"
                self.auto_scroll = True
                await self.start_live_stream()

        elif key.lower() == "h":
            if self.active_tab != "historical":
                self.active_tab = "historical"
                self.auto_scroll = False
                await self.fetch_historical()

        elif key.lower() == "u":
            await self.upload_logs()

        elif key == " ":
            if self.active_tab == "live":
                self.auto_scroll = not self.auto_scroll
                if self.auto_scroll:
                    self.scroll_to_bottom()

        elif key == readchar.key.UP:
            self.auto_scroll = False
            self.scroll_offset = max(0, self.scroll_offset - 1)

        elif key == readchar.key.DOWN:
            self.auto_scroll = False
            self.scroll_offset = min(len(self.logs) - 1, self.scroll_offset + 1)
