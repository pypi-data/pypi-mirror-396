import asyncio
import readchar
from rich.console import Console
from rich.live import Live
from rich.layout import Layout

from riven_cli.config import settings
from riven_cli.tui.screens.login import LoginScreen
from riven_cli.tui.screens.dashboard import DashboardScreen
from riven_cli.tui.screens.library import LibraryScreen
from riven_cli.tui.screens.details import ItemDetailsScreen
from riven_cli.tui.screens.settings import SettingsScreen
from riven_cli.tui.screens.search import SearchScreen
from riven_cli.tui.screens.logs import LogsScreen


class TUIApp:
    def __init__(self, console: Console):
        self.console = console
        self.layout = Layout()
        self.running = True
        self.current_screen = None
        self.context = {}  # Shared context for passing data between screens
        self.screens = {
            "login": LoginScreen(self),
            "dashboard": DashboardScreen(self),
            "library": LibraryScreen(self),
            "details": ItemDetailsScreen(self),
            "settings": SettingsScreen(self),
            "search": SearchScreen(self),
            "logs": LogsScreen(self),
        }

    async def refresh_loop(self):
        while self.running:
            self.layout.update(self.current_screen.render())
            await asyncio.sleep(0.033)  # 30 FPS update rate

    async def run(self):
        # Initial Route
        if not settings.api_key:
            self.switch_to("login")
        else:
            self.switch_to("dashboard")

        # Main Loop
        with Live(
            self.layout, console=self.console, screen=True, refresh_per_second=30
        ):
            # Start the refresh loop background task
            render_task = asyncio.create_task(self.refresh_loop())

            try:
                while self.running:
                    # Check for input

                    key = await asyncio.get_event_loop().run_in_executor(
                        None, readchar.readkey
                    )

                    if key == readchar.key.CTRL_C:
                        self.running = False
                        break

                    # Pass input to current screen
                    await self.current_screen.handle_input(key)
            finally:
                self.running = False
                await render_task

                # Cleanup screens
                for screen in self.screens.values():
                    if hasattr(screen, "shutdown"):
                        await screen.shutdown()

    def switch_to(self, screen_name: str):
        self.current_screen = self.screens[screen_name]
        if hasattr(self.current_screen, "on_mount"):
            asyncio.create_task(self.current_screen.on_mount())


class Screen:
    def __init__(self, app: TUIApp):
        self.app = app

    def render(self):
        raise NotImplementedError

    async def handle_input(self, key: str):
        pass
