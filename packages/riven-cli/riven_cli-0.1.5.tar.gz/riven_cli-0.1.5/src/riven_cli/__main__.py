import asyncio
import sys
from rich.console import Console

from riven_cli.tui.app import TUIApp


def main():
    console = Console()
    app = TUIApp(console)

    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
