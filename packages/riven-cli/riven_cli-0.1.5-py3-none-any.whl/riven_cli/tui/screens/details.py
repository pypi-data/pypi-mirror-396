from typing import Any
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich.console import Group

from riven_cli.api import client


class ItemDetailsScreen:
    def __init__(self, app):
        self.app = app
        self.item_id: int | None = None
        self.item: dict[str, Any] | None = None
        self.loading = True
        self.error: str | None = None
        self.msg: str | None = None  # Status message (Success/Error of actions)

    async def on_mount(self):
        if hasattr(self.app, "context") and "item_id" in self.app.context:
            self.item_id = self.app.context["item_id"]
            await self.fetch_details()
        else:
            self.error = "No Item ID selected"
            self.loading = False

    async def fetch_details(self):
        if not self.item_id:
            return
        try:
            self.loading = True
            self.msg = None
            async with client:
                self.item = await client.get(
                    f"/items/{self.item_id}",
                    params={"extended": "true", "media_type": "item"},
                )
            self.error = None
        except Exception as e:
            self.error = str(e)
            self.item = None
        finally:
            self.loading = False

    async def reset_item(self):
        if not self.item_id:
            return

        self.msg = "Resetting..."
        try:
            async with client:
                await client.post("/items/reset", json={"ids": [str(self.item_id)]})

            self.msg = "Reset triggered"
            await self.fetch_details()
        except Exception as e:
            self.msg = f"Reset Failed: {str(e)}"

    async def delete_item(self):
        if not self.item_id:
            return

        self.msg = "Deleting..."
        try:
            async with client:
                await client.delete("/items/remove", json={"ids": [str(self.item_id)]})

            self.app.switch_to("library")
        except Exception as e:
            self.msg = f"Delete Failed: {str(e)}"

    async def retry_item(self):
        if not self.item_id:
            return

        self.msg = "Retrying..."
        try:
            async with client:
                await client.post("/items/retry", json={"ids": [str(self.item_id)]})
            self.msg = "Retry triggered"
            await self.fetch_details()
        except Exception as e:
            self.msg = f"Retry Failed: {str(e)}"

    async def pause_item(self):
        if not self.item_id:
            return

        self.msg = "Pausing..."
        try:
            async with client:
                await client.post("/items/pause", json={"ids": [str(self.item_id)]})
            self.msg = "Pause triggered"
            await self.fetch_details()
        except Exception as e:
            self.msg = f"Pause Failed: {str(e)}"

    def render(self):
        # Header
        title = "Item Details"
        if self.item:
            year = self.item.get("year")
            if not year and self.item.get("aired_at"):
                year = str(self.item.get("aired_at"))[:4]
            title = f"{self.item.get('title')} ({year or 'N/A'})"

        header = Panel(Align.center(Text(title, style="bold green")), style="blue")

        # Body
        if self.loading and not self.item:
            body = Align.center(Text("Loading details...", style="yellow blink"))
        elif self.error:
            body = Align.center(Text(f"Error:\n{self.error}", style="bold red"))
        elif self.item:
            # 1. General Info
            general_table = Table(show_header=False, box=None, padding=(0, 2))
            general_table.add_column("Key", style="cyan")
            general_table.add_column("Value", style="white")

            general_table.add_row("Type", self.item.get("type", "N/A").capitalize())
            general_table.add_row("State", self.item.get("state", "N/A"))

            # Format Date
            aired = self.item.get("aired_at")
            if aired:
                aired = str(aired).split(" ")[0]
            general_table.add_row("Aired", aired or "N/A")

            genres = self.item.get("genres", [])
            if genres:
                general_table.add_row("Genres", ", ".join(genres[:3]))

            general_table.add_row("Rating", self.item.get("content_rating", "N/A"))

            # 2. File Info
            fs_entry = self.item.get("filesystem_entry")
            file_table = Table(show_header=False, box=None, padding=(0, 2))
            file_table.add_column("Key", style="cyan")
            file_table.add_column("Value", style="white")

            if fs_entry:
                size_bytes = fs_entry.get("file_size", 0)
                size_gb = f"{size_bytes / (1024**3):.2f} GB" if size_bytes else "N/A"

                file_table.add_row(
                    "Filename",
                    Text(fs_entry.get("original_filename", "N/A"), overflow="ellipsis"),
                )
                file_table.add_row("Size", size_gb)
                file_table.add_row("Provider", fs_entry.get("provider", "N/A"))
                file_table.add_row(
                    "Updated", str(fs_entry.get("updated_at", "")).split("T")[0]
                )
            else:
                file_table.add_row("Status", "No file linked")

            # 3. Media Info
            media_meta = self.item.get("media_metadata", {})
            media_table = Table(show_header=False, box=None, padding=(0, 2))
            media_table.add_column("Key", style="cyan")
            media_table.add_column("Value", style="white")

            if media_meta:
                video = media_meta.get("video")
                if video:
                    res = f"{video.get('resolution_width', '?')}x{video.get('resolution_height', '?')}"
                    codec = video.get("codec", "N/A")
                else:
                    res = "N/A"
                    codec = "N/A"

                media_table.add_row("Resolution", res)
                media_table.add_row("Codec", codec)
                media_table.add_row(
                    "Source", media_meta.get("quality_source", "N/A") or "N/A"
                )
            else:
                media_table.add_row("Info", "No media metadata")

            # Layout grouping

            # Create panels
            p_general = Panel(general_table, title="General", border_style="blue")
            p_file = Panel(file_table, title="File", border_style="green")
            p_media = Panel(media_table, title="Media", border_style="magenta")

            # Stack them
            content = [p_general, p_file, p_media]

            if self.msg:
                content.insert(
                    0, Panel(Text(self.msg, style="bold yellow"), title="Status")
                )

            body = Group(*content)
        else:
            body = Align.center(Text("Item not found"))

        # Footer
        footer_text = Text()
        footer_text.append("[Q] Back  ", style="bold red")
        footer_text.append("[D] Delete  ", style="bold bg red")
        footer_text.append("[S] Reset  ", style="bold blue")
        footer_text.append("[T] Retry ", style="bold green")
        footer_text.append("[P] Pause ", style="bold magenta")
        footer_text.append("[R] Refresh ", style="bold cyan")

        footer = Panel(Align.center(footer_text), title="Actions")

        layout = Layout()
        layout.split(Layout(header, size=3), Layout(body), Layout(footer, size=3))
        return layout

    async def handle_input(self, key: str):
        if key.lower() == "q":
            self.app.switch_to("library")
        elif key.lower() == "r":
            await self.fetch_details()
        elif key.lower() == "s":
            await self.reset_item()
        elif key.lower() == "d":
            await self.delete_item()
        elif key.lower() == "t":
            await self.retry_item()
        elif key.lower() == "p":
            await self.pause_item()
