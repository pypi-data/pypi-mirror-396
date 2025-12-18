from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.console import Group
import readchar

from riven_cli.config import settings


class LoginScreen:
    def __init__(self, app):
        self.app = app
        self.step = "url"  # url or key
        self.api_url_input = settings.api_url
        self.api_key_input = ""
        self.error_message = ""

    def render(self):
        title = Text("Riven CLI", style="bold magenta", justify="center")

        content = [title, Text("")]

        if self.step == "url":
            instructions = Text("Enter Backend URL:", justify="center")
            input_display = Panel(
                Align.center(
                    Text(
                        self.api_url_input if self.api_url_input else " ",
                        style="white on blue",
                    )
                ),
                title="Backend URL",
                border_style="green" if not self.error_message else "red",
                padding=(1, 2),
            )
            content.extend([instructions, input_display])
        else:
            instructions = Text("Enter API Key:", justify="center")
            masked_input = "*" * len(self.api_key_input)
            input_display = Panel(
                Align.center(
                    Text(masked_input if masked_input else " ", style="white on blue")
                ),
                title="API Key",
                border_style="green" if not self.error_message else "red",
                padding=(1, 2),
            )
            content.extend([instructions, input_display])

        if self.error_message:
            content.append(
                Text(
                    f"\nError: {self.error_message}", style="bold red", justify="center"
                )
            )

        return Align.center(Group(*content), vertical="middle")

    async def handle_input(self, key: str):
        if key == readchar.key.ENTER:
            if self.step == "url":
                if not self.api_url_input:
                    self.error_message = "URL cannot be empty"
                    return
                self.step = "key"
                self.error_message = ""
            elif self.step == "key":
                if not self.api_key_input:
                    self.error_message = "API Key cannot be empty"
                    return

                # Save Settings
                settings.api_url = self.api_url_input
                settings.api_key = self.api_key_input
                settings.save()

                self.app.switch_to("dashboard")

        elif key == readchar.key.BACKSPACE:
            if self.step == "url":
                self.api_url_input = self.api_url_input[:-1]
            else:
                self.api_key_input = self.api_key_input[:-1]
        elif len(key) == 1 and key.isprintable():
            if self.step == "url":
                self.api_url_input += key
            else:
                self.api_key_input += key
