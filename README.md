# Jules MCP Server

MCP server for orchestrating multiple Jules instances (Google's AI coding agent). Create and manage multiple Jules workers in parallel, approve their plans, and coordinate complex multi-instance workflows.

## Features

- **Multi-Instance Orchestration** - Spawn and manage multiple Jules workers simultaneously
- **Real-Time Monitoring** - Background polling tracks worker states every 5 seconds
- **Plan Approval Flow** - Review and approve Jules-generated plans before execution
- **MCP Integration** - 5 tools, 3 resources, and 2 prompts for Claude Desktop/Code
- **State Machine** - Automatic tracking: PLANNING → WAITING_APPROVAL → EXECUTING → COMPLETED
- **Error Detection** - Identifies stuck workers and extracts error messages

## Installation

```bash
cd jules-mcp
pip install -e .
```

## Configuration

Create a `.env` file:

```bash
JULES_API_KEY=your_api_key_here
JULES_API_BASE_URL=https://jules.googleapis.com
JULES_API_VERSION=v1alpha
WORKER_POLL_INTERVAL=5
WORKER_STUCK_TIMEOUT=300
```

Get your API key from: https://jules.google.com/settings#api

## Usage with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jules-orchestrator": {
      "command": "jules-mcp"
    }
  }
}
```

## MCP Tools

- `jules_create_worker` - Create new Jules worker session
- `jules_send_message` - Send message to a worker
- `jules_approve_plan` - Approve generated plan
- `jules_cancel_session` - Cancel a worker
- `jules_get_activities` - Get recent activities

## MCP Resources

- `workers://all` - View all active workers
- `worker://{session_id}/status` - Worker status
- `worker://{session_id}/activities` - Worker activities

## Prerequisites

1. Install Jules GitHub app on your repository: https://github.com/apps/jules-ai
2. Get source path format: `sources/github/{owner}/{repo}`
3. Have a valid Jules API key

## Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed testing instructions.

## Status

✅ Fully implemented and tested with Jules API
✅ API client working with provided API key
⚠️ Requires GitHub repository with Jules app installed for full functionality

## Architecture

- **jules_client.py** - Async HTTP client for Jules REST API
- **worker_manager.py** - Manages multiple workers with background polling
- **state.py** - Data models and state machine
- **server.py** - FastMCP server with tools and resources
- **utils.py** - Helper functions

Built with: FastMCP, httpx, pydantic, python-dotenv 
