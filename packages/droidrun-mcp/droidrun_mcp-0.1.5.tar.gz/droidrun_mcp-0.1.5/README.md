# Droidrun MCP Server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server for **Droidrun**, enabling LLMs (like OAI, Claude and Gemini) to control Android devices directly.

## Features

*   **Natural Language Control**: "Open Settings and turn on Wi-Fi".
*   **Visual Understanding**: Analyzes screenshots to navigate the UI.
*   **Trajectory Management**: Automatically saves session history and screenshots.
*   **Safe Execution**: Runs locally on your machine.

## Prerequisites

*   **Python 3.10+**
*   **ADB** installed and running (`adb devices` should show your device).


## Installation

### Option 1: Configure Your Client (Easiest setup)
Add the server to your MCP client configuration (e.g., `claude_desktop_config.json` or Gemini CLI config or Codex CLI config).

### Option 2 Using `uvx` 
This is the easiest way to run the server without managing virtual environments manually.

```bash
uvx droidrun-mcp
```

### Option 3: Using `pip`
You can also install it directly from PyPI:

```bash
pip install droidrun-mcp
```

*Note: Ensure you have ADB installed and your Android device connected.*


**Important**: You must provide your API keys and (optionally) configuration paths via environment variables.

```json
{
  "mcpServers": {
    "droidrun": {
      "command": "uvx",
      "args": [
        "droidrun-mcp"
      ],
      "env": {
        "GOOGLE_API_KEY": "your-key-here",
        "OPENAI_API_KEY": "your-key-here",
        "DROIDRUN_TRAJECTORY_PATH": "~/.droidrun-mcp/trajectories",
        "DROIDRUN_CONFIG_PATH": "~/.droidrun-mcp/config.yaml"
      }
    }
  }
}
```

> [!TIP]
> We recommend copying the default `config.yaml` to `~/.droidrun-mcp/config.yaml` so you can customize it easily.

### Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DROIDRUN_TRAJECTORY_PATH` | Where to save logs/screenshots. | `~/.droidrun-mcp/trajectories` |
| `DROIDRUN_CONFIG_PATH` | Path to a custom `config.yaml`. | `config.yaml` (in package) |
| `GOOGLE_API_KEY` | Required for Gemini models. | - |
| `OPENAI_API_KEY` | Required for OpenAI models. | - |

## Available Tools

*   **`execute_task(instruction)`**: Executes a natural language command on the device.
    *   `instruction`: "Open YouTube and search for cats"
    *   `apk_path`: (Optional) Only for testing specific APKs.
*   **`get_trajectory(session_id)`**: Retrieves the event log for a session.
*   **`get_screenshots(session_id)`**: Gets screenshots from a session.
*   **`get_single_screenshot(session_id, step)`**: Gets a specific screenshot.

## Development

To contribute to this project:

1.  Clone the repo:
    ```bash
    git clone https://github.com/droidrun/droidrun-mcp.git
    ```
2.  Install dependencies:
    ```bash
    uv sync --all-extras
    ```
3.  Run locally:
    ```bash
    fastmcp run droidrun_mcp/server.py
    ```
