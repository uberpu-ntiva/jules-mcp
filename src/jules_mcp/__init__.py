"""Jules MCP Server - Orchestrate multiple Jules instances via MCP"""

__version__ = "0.1.0"

from .jules_client import JulesAPIClient
from .worker_manager import WorkerManager
from .state import WorkerState, WorkerSession, Activity, ActivityType

__all__ = [
    "JulesAPIClient",
    "WorkerManager",
    "WorkerState",
    "WorkerSession",
    "Activity",
    "ActivityType",
]
