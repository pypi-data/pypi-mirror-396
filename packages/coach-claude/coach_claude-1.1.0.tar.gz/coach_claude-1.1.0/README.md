# Coach Claude MCP Server

The MCP (Model Context Protocol) server component of Coach Claude. Provides health and wellness tracking capabilities through a SQLite database.

## Installation

```bash
pip install coach-claude
```

## Usage

The MCP server runs as a background service and exposes tools for tracking water intake and workouts.

### Running the Server

The server supports two transport modes: **stdio** (default) and **SSE** (for remote/daemon use).

```bash
# Start with stdio transport (default, for local use)
coach-claude

# Start with SSE transport (for remote/daemon use)
coach-claude --transport sse --port 8787

# Custom host binding (default: 127.0.0.1)
coach-claude --transport sse --host 0.0.0.0 --port 8787
```

### MCP Configuration (stdio)

For local use, add to your `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "coach-claude": {
      "command": "coach-claude"
    }
  }
}
```

### MCP Configuration (SSE) - For Devcontainers

Run the server as a daemon on your host machine, then configure devcontainers to connect via SSE:

**On host machine:**
```bash
# Run as a background daemon
coach-claude --transport sse --port 8787 &
```

**In devcontainer `~/.claude/settings.json`:**
```json
{
  "mcpServers": {
    "coach-claude": {
      "url": "http://host.docker.internal:8787/sse"
    }
  }
}
```

This allows all your devcontainers to share the same workout/water tracking database on your host machine.

## Available Tools

- `log_water(amount, unit?)` - Log water intake
- `log_workout(type, name, duration)` - Log a workout
- `get_last_water()` - Get last water intake
- `get_last_workout()` - Get last workout
- `check_reminders()` - Check what reminders are due
- `get_stats(period?)` - Get statistics
- `update_config(key, value)` - Update configuration
- `get_config(key?)` - Get configuration

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/
ruff check src/
```

## License

Apache 2.0
