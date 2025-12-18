# Riven CLI

A powerful Terminal User Interface (TUI) for Riven.
Manage your library, search for content, and monitor your server directly from your terminal with a sleek and fast interface.

## Features

- **Dashboard**: Get an overview of your Riven server status.
- **Library Management**: Browse and manage your media library efficiently.
- **Search**: Quickly find content.
- **Details View**: View detailed information about movies and series.
- **Settings**: Configure your Riven instance directly from the CLI.

## Installation

You can install Riven CLI directly from PyPI:

```bash
pip install riven-cli
```

Or using `uv` (recommended):

```bash
uv tool install riven-cli
```

## Usage

Once installed, simply run:

```bash
riven-cli
```

If you are running from source:

```bash
uv run riven-cli
```

## Configuration

On the first launch, you will be prompted to login to your Riven instance. You can update these settings at any time within the application's **Settings** menu.

## License

[MIT](LICENSE)
