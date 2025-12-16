# kdenlive-mcp

MCP (Model Context Protocol) server for Kdenlive video editor automation. Enables AI assistants like Claude to control Kdenlive through natural language.

## Installation

```bash
pip install kdenlive-mcp
```

Or with uv:

```bash
uv tool install kdenlive-mcp
```

## Requirements

- Python 3.11+
- Kdenlive with WebSocket RPC server (requires kdenlive-websocket fork)
- Kdenlive must be running before starting the MCP server

## Quick Start

1. **Start Kdenlive** (with RPC server enabled)

2. **Configure your MCP client** (see below)

3. **Start using AI to control Kdenlive!**

## MCP Client Configuration

### Claude Desktop

Add to your Claude Desktop configuration file:

**Linux** (`~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "kdenlive-mcp"
    }
  }
}
```

**Windows** (`%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "kdenlive-mcp"
    }
  }
}
```

**macOS** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "kdenlive-mcp"
    }
  }
}
```

### With Custom Configuration

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "kdenlive-mcp",
      "env": {
        "KDENLIVE_WS_URL": "ws://localhost:9876",
        "KDENLIVE_AUTH_TOKEN": "your-secret-token"
      }
    }
  }
}
```

### Using uvx (no installation required)

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "uvx",
      "args": ["kdenlive-mcp"]
    }
  }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KDENLIVE_WS_URL` | WebSocket URL to Kdenlive RPC server | `ws://localhost:9876` |
| `KDENLIVE_AUTH_TOKEN` | Bearer token for authentication | None |

## Available Tools

The MCP server exposes 60+ tools for controlling Kdenlive:

### Project Management
- `project_get_info` - Get current project information
- `project_open` - Open a project file
- `project_save` - Save the current project
- `project_close` - Close the current project
- `project_new` - Create a new project
- `project_undo` / `project_redo` - Undo/redo actions

### Timeline Operations
- `timeline_get_info` - Get timeline information
- `timeline_get_tracks` - List all tracks
- `timeline_get_clips` - Get clips on timeline
- `timeline_insert_clip` - Insert clip from bin
- `timeline_move_clip` - Move a clip
- `timeline_delete_clip` - Delete a clip
- `timeline_split_clip` - Split a clip
- `timeline_resize_clip` - Trim/resize a clip
- `timeline_add_track` / `timeline_delete_track` - Manage tracks
- `timeline_seek` / `timeline_get_position` - Playhead control

### Bin/Media Management
- `bin_list_clips` / `bin_list_folders` - Browse bin contents
- `bin_get_clip_info` - Get clip details
- `bin_import_clip` / `bin_import_clips` - Import media files
- `bin_delete_clip` - Remove clips
- `bin_create_folder` - Create folders
- `bin_rename_item` / `bin_move_item` - Organize items
- `bin_add_clip_marker` / `bin_delete_clip_marker` - Manage markers

### Effects
- `effect_list_available` - List all effects
- `effect_get_info` - Get effect parameters
- `effect_add` / `effect_remove` - Add/remove effects
- `effect_get_clip_effects` - List effects on a clip
- `effect_set_property` - Modify effect parameters
- `effect_enable` / `effect_disable` - Toggle effects
- `effect_get_keyframes` / `effect_set_keyframe` / `effect_delete_keyframe` - Keyframe animation

### Rendering
- `render_get_presets` - List render presets
- `render_start` - Start rendering
- `render_stop` - Stop a render job
- `render_get_status` - Check render progress
- `render_get_jobs` / `render_get_active_job` - Monitor jobs

### Assets
- `asset_list_categories` - Browse effect categories
- `asset_search` - Search effects/transitions
- `asset_get_effects_by_category` - Filter by category
- `asset_get_favorites` / `asset_add_favorite` / `asset_remove_favorite` - Manage favorites
- `asset_get_presets` / `asset_save_preset` - Effect presets

### Transitions & Compositions
- `transition_list` - List available transitions
- `transition_add` / `transition_remove` - Manage transitions
- `composition_list` - List compositions
- `composition_add` / `composition_remove` - Manage compositions

### Utilities
- `kdenlive_ping` - Check connection
- `kdenlive_version` - Get version info

## Example Conversations

Once configured, you can ask Claude to:

> "Import all MP4 files from my Downloads folder into Kdenlive"

> "Add a blur effect to the first clip on the timeline"

> "Split the video at the 5 second mark"

> "Render the project as MP4 to my Desktop"

> "Create a new folder called 'B-Roll' in the bin and move all clips shorter than 10 seconds into it"

## Troubleshooting

### "Cannot connect to Kdenlive"

1. Make sure Kdenlive is running
2. Verify the RPC server is enabled in Kdenlive settings
3. Check that the WebSocket URL is correct (default: `ws://localhost:9876`)

### "Connection refused"

The Kdenlive RPC server might be on a different port or host. Check your Kdenlive settings and update `KDENLIVE_WS_URL` accordingly.

### Windows PATH Issues

If `kdenlive-mcp` command is not found, use the full path:

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "C:\\Users\\YourName\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\kdenlive-mcp.exe"
    }
  }
}
```

Or use uvx which handles this automatically:

```json
{
  "mcpServers": {
    "kdenlive": {
      "command": "uvx",
      "args": ["kdenlive-mcp"]
    }
  }
}
```

## Development

```bash
# Clone the repository
git clone https://github.com/IO-AtelierTech/kdenlive-automation.git
cd kdenlive-automation

# Install dependencies
uv sync

# Run the MCP server locally
uv run kdenlive-mcp
```

## Related Projects

- [kdenlive-api](https://pypi.org/project/kdenlive-api/) - Python client library for Kdenlive RPC
- [Kdenlive](https://kdenlive.org/) - Free and open source video editor
- [Model Context Protocol](https://modelcontextprotocol.io/) - Open protocol for AI tool integration

## License

MIT License - see LICENSE file for details.
