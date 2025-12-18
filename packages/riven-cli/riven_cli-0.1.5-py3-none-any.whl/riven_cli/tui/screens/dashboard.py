from typing import Any
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich.console import Group
from rich.padding import Padding

from riven_cli.config import settings
from riven_cli.api import client


class DashboardScreen:
    def __init__(self, app):
        self.app = app
        self.stats: dict[str, Any] | None = None
        self.health: dict[str, Any] | None = None
        self.debrid_info: dict[str, Any] | None = None
        self.loading = True
        self.error: str | None = None

    async def on_mount(self):
        await self.fetch_stats()

    async def fetch_stats(self):
        try:
            self.loading = True
            async with client:
                self.stats = await client.get("/stats")
                try:
                    self.health = await client.get("/health")
                except Exception:
                    self.health = None
                try:
                    self.debrid_info = await client.get("/downloader_user_info")
                except Exception:
                    self.debrid_info = None
            self.error = None
        except Exception as e:
            self.error = str(e)
            self.stats = None
        finally:
            self.loading = False

    def render(self):
        # Header
        health_status = "Unknown"
        health_style = "yellow"
        if self.health:
            if str(self.health.get("message")).lower() == "true":
                health_status = "Online"
                health_style = "bold green"
            else:
                health_status = "Not Initialized"
                health_style = "bold red"

        header = Panel(
            Align.center(
                Text.from_markup(
                    f"Riven CLI - {settings.api_url} | [{health_style}]{health_status}[/]"
                )
            ),
            style="blue",
        )

        # Body
        if self.loading and not self.stats:
            body = Align.center(Text("Loading stats...", style="yellow blink"))
        elif self.error:
            body = Align.center(
                Text(f"Error fetching stats:\n{self.error}", style="bold red")
            )
        else:
            panels = []

            # 1. Stats Table
            if self.stats:
                table = Table(
                    title="Library Statistics",
                    show_header=True,
                    header_style="bold magenta",
                    expand=True,
                )
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green", justify="right")

                table.add_row("Total Items", str(self.stats.get("total_items", 0)))
                table.add_row("Movies", str(self.stats.get("total_movies", 0)))
                table.add_row("Shows", str(self.stats.get("total_shows", 0)))
                table.add_row("Episodes", str(self.stats.get("total_episodes", 0)))
                table.add_row("Incomplete", str(self.stats.get("incomplete_items", 0)))
                panels.append(table)

            # 2. Debrid Info Table
            if self.debrid_info and "services" in self.debrid_info:
                debrid_table = Table(
                    title="Debrid Services",
                    show_header=True,
                    header_style="bold magenta",
                    expand=True,
                )
                debrid_table.add_column("Service", style="cyan")
                debrid_table.add_column("User", style="yellow")
                debrid_table.add_column("Status", style="bold")
                debrid_table.add_column("Days Left", justify="right")

                for service in self.debrid_info.get("services", []):
                    status_style = (
                        "green" if service.get("premium_status") == "premium" else "red"
                    )
                    days = str(service.get("premium_days_left", "N/A"))

                    debrid_table.add_row(
                        service.get("service", "Unknown"),
                        service.get("username", "Unknown"),
                        Text(
                            service.get("premium_status", "Unknown"), style=status_style
                        ),
                        days,
                    )
                panels.append(Padding(debrid_table, (1, 0, 0, 0)))  # Add top padding

            if not panels:
                body = Align.center(Text("No data available", style="dim"))
            else:
                body = Align.center(Group(*panels))

        # Footer / Menu
        footer_text = Text()
        footer_text.append("[Q] Quit  ", style="bold red")
        footer_text.append("[L] Library  ", style="bold yellow")
        footer_text.append("[S] Settings  ", style="bold cyan")
        footer_text.append("[R] Refresh  ", style="bold green")
        footer_text.append("[F] Find New  ", style="bold magenta")
        footer_text.append("[G] Logs", style="bold white")

        footer = Panel(Align.center(footer_text), title="Menu")

        layout = Layout()
        layout.split(Layout(header, size=3), Layout(body), Layout(footer, size=3))
        return layout

    async def handle_input(self, key: str):
        if key.lower() == "q":
            self.app.running = False
        elif key.lower() == "r":
            await self.fetch_stats()
        elif key.lower() == "l":
            # Reset library state to ensure we start fresh at root
            if "library" in self.app.screens:
                self.app.screens["library"].reset_state()
            self.app.switch_to("library")
        elif key.lower() == "s":
            self.app.switch_to("settings")
        elif key.lower() == "f":
            self.app.switch_to("search")
        elif key.lower() == "g":
            self.app.switch_to("logs")
