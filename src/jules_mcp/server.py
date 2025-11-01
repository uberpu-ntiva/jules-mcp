"""Main MCP server implementation using FastMCP"""

import os
import sys
import asyncio
import logging
from typing import Optional

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

from .jules_client import JulesAPIClient
from .worker_manager import WorkerManager
from .utils import format_timestamp, truncate_text

# Load environment variables
load_dotenv()

# Configure logging to stderr (MCP uses stdout for protocol)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Read configuration from environment
api_key = os.getenv("JULES_API_KEY")
base_url = os.getenv("JULES_API_BASE_URL", "https://jules.googleapis.com")
api_version = os.getenv("JULES_API_VERSION", "v1alpha")
poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "5"))
stuck_timeout = int(os.getenv("WORKER_STUCK_TIMEOUT", "300"))

# Create FastMCP server
mcp = FastMCP("Jules MCP Server")

# Global state (will be initialized in main)
jules_client: Optional[JulesAPIClient] = None
worker_manager: Optional[WorkerManager] = None


async def initialize_server():
    """Initialize Jules client and worker manager"""
    global jules_client, worker_manager

    if not api_key:
        logger.error("JULES_API_KEY not found in environment")
        raise Exception("JULES_API_KEY environment variable is required")

    # Initialize Jules client
    jules_client = JulesAPIClient(
        api_key=api_key,
        base_url=base_url,
        api_version=api_version
    )

    # Initialize worker manager
    worker_manager = WorkerManager(
        jules_client=jules_client,
        poll_interval=poll_interval,
        stuck_timeout=stuck_timeout
    )

    # Start worker manager
    await worker_manager.start()

    logger.info("Jules MCP Server initialized")


async def shutdown_server():
    """Shutdown Jules client and worker manager"""
    global jules_client, worker_manager

    if worker_manager:
        await worker_manager.stop()

    if jules_client:
        await jules_client.close()

    logger.info("Jules MCP Server shutdown complete")


# MCP Tools

@mcp.tool()
async def jules_create_worker(
    task_description: str,
    source: str,
    title: str,
    github_branch: str = "main"
) -> dict:
    """
    Create a new Jules worker session for a task

    Args:
        task_description: Description of task for the worker
        source: GitHub source (format: "sources/github/owner/repo")
        title: Short title for the session
        github_branch: Branch to work on (optional, default: "main")

    Returns:
        Dictionary with session_id and confirmation message
    """
    try:
        session_id = await worker_manager.create_worker(
            prompt=task_description,
            source=source,
            title=title,
            github_branch=github_branch
        )

        return {
            "session_id": session_id,
            "message": f"Worker created successfully. Session ID: {session_id}",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to create worker: {e}")
        return {
            "status": "error",
            "message": f"Failed to create worker: {str(e)}"
        }


@mcp.tool()
async def jules_send_message(session_id: str, message: str) -> dict:
    """
    Send a message to an existing Jules worker session

    Args:
        session_id: Worker session ID
        message: Message text to send

    Returns:
        Dictionary with status
    """
    try:
        await worker_manager.send_worker_message(session_id, message)

        return {
            "status": "success",
            "message": f"Message sent to worker {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return {
            "status": "error",
            "message": f"Failed to send message: {str(e)}"
        }


@mcp.tool()
async def jules_approve_plan(session_id: str) -> dict:
    """
    Approve a generated plan for a Jules worker

    Args:
        session_id: Worker session ID

    Returns:
        Dictionary with status
    """
    try:
        await worker_manager.approve_worker_plan(session_id)

        return {
            "status": "success",
            "message": f"Plan approved for worker {session_id}"
        }
    except Exception as e:
        logger.error(f"Failed to approve plan: {e}")
        return {
            "status": "error",
            "message": f"Failed to approve plan: {str(e)}"
        }


@mcp.tool()
async def jules_cancel_session(session_id: str) -> dict:
    """
    Cancel a Jules worker session

    Args:
        session_id: Worker session ID

    Returns:
        Dictionary with status
    """
    try:
        await worker_manager.cancel_worker(session_id)

        return {
            "status": "success",
            "message": f"Worker {session_id} cancelled"
        }
    except Exception as e:
        logger.error(f"Failed to cancel worker: {e}")
        return {
            "status": "error",
            "message": f"Failed to cancel worker: {str(e)}"
        }


@mcp.tool()
async def jules_get_activities(session_id: str, limit: int = 10) -> dict:
    """
    Get recent activities for a Jules worker

    Args:
        session_id: Worker session ID
        limit: Maximum number of activities to return (default: 10)

    Returns:
        Dictionary with activities list
    """
    try:
        activities = await worker_manager.get_worker_activities(session_id, limit)

        # Format activities as human-readable list
        activity_list = []
        for activity in activities:
            activity_info = {
                "id": activity.id,
                "type": activity.type.value,
                "originator": activity.originator,
                "create_time": format_timestamp(activity.create_time),
                "title": activity.title,
                "description": truncate_text(activity.description or "", 200) if activity.description else None
            }
            activity_list.append(activity_info)

        return {
            "status": "success",
            "session_id": session_id,
            "activities": activity_list,
            "count": len(activity_list)
        }
    except Exception as e:
        logger.error(f"Failed to get activities: {e}")
        return {
            "status": "error",
            "message": f"Failed to get activities: {str(e)}"
        }


# MCP Resources

@mcp.resource("worker://{session_id}/status")
async def get_worker_status(session_id: str) -> str:
    """
    Get real-time status of a specific worker

    Args:
        session_id: Worker session ID

    Returns:
        Text content with worker status details
    """
    try:
        status = worker_manager.get_worker_status(session_id)

        # Format as readable text
        lines = [
            f"Worker Status: {session_id}",
            f"=" * 60,
            f"Task: {status['task']}",
            f"State: {status['state']}",
            f"Blocked: {status['is_blocked']}",
        ]

        if status['blocker_reason']:
            lines.append(f"Blocker: {status['blocker_reason']}")

        if status['pending_plan_id']:
            lines.append(f"Pending Plan ID: {status['pending_plan_id']}")

        if status['error_message']:
            lines.append(f"Error: {status['error_message']}")

        lines.extend([
            f"Last Activity: {status['last_activity']}",
            f"Created: {status['created_at']}"
        ])

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get worker status: {e}")
        return f"Error: {str(e)}"


@mcp.resource("workers://all")
async def get_all_workers() -> str:
    """
    Get summary of all active workers

    Returns:
        Text content with all workers summary
    """
    try:
        workers = worker_manager.get_all_workers()

        if not workers:
            return "No workers currently running."

        # Format as table
        lines = [
            "All Workers",
            "=" * 80,
            f"{'Session ID':<20} {'State':<20} {'Task':<40}",
            "-" * 80
        ]

        for worker in workers:
            task_short = truncate_text(worker.task_description, 37)
            lines.append(
                f"{worker.session_id:<20} {worker.state.value:<20} {task_short:<40}"
            )

        lines.append("-" * 80)
        lines.append(f"Total workers: {len(workers)}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get all workers: {e}")
        return f"Error: {str(e)}"


@mcp.resource("worker://{session_id}/activities")
async def get_worker_activities_resource(session_id: str) -> str:
    """
    Get recent activities for a specific worker

    Args:
        session_id: Worker session ID

    Returns:
        Text content with recent activities
    """
    try:
        activities = await worker_manager.get_worker_activities(session_id, limit=10)

        if not activities:
            return f"No activities found for worker {session_id}"

        # Format as chronological list
        lines = [
            f"Recent Activities for {session_id}",
            "=" * 80
        ]

        for activity in activities:
            lines.append(f"\n[{format_timestamp(activity.create_time)}] {activity.type.value}")
            lines.append(f"  Originator: {activity.originator}")

            if activity.title:
                lines.append(f"  Title: {activity.title}")

            if activity.description:
                desc = truncate_text(activity.description, 200)
                lines.append(f"  Description: {desc}")

        return "\n".join(lines)

    except Exception as e:
        logger.error(f"Failed to get worker activities: {e}")
        return f"Error: {str(e)}"


# MCP Prompts

@mcp.prompt()
async def delegate_task(complex_task: str) -> str:
    """
    Template for breaking down and delegating complex tasks to multiple workers

    Args:
        complex_task: The complex task to break down

    Returns:
        Prompt template for task delegation
    """
    return f"""You are coordinating multiple Jules worker instances. Here's a complex task:

"{complex_task}"

Analyze this task and:
1. Break it into independent subtasks
2. For each subtask, use jules_create_worker to spawn a worker
3. Monitor workers using worker:// resources
4. Approve plans when workers need it
5. Coordinate results when all workers complete

Remember to check worker status regularly and handle any blockers that arise."""


@mcp.prompt()
async def review_plan(session_id: str) -> str:
    """
    Template for reviewing a worker's generated plan

    Args:
        session_id: Worker with pending plan

    Returns:
        Prompt template for plan review
    """
    return f"""A Jules worker (session {session_id}) has generated a plan and needs approval.

1. Read the plan details using worker://{session_id}/activities
2. Review the plan steps carefully
3. If acceptable, use jules_approve_plan
4. If issues found, use jules_send_message to provide guidance

Make sure the plan is sound before approving."""


def main():
    """Entry point for MCP server"""
    try:
        # Run server in stdio mode
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()
