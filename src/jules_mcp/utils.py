"""Helper functions for Jules MCP server"""

from datetime import datetime
from .state import ActivityType


def detect_activity_type(activity_data: dict) -> ActivityType:
    """Examine activity JSON structure and determine type"""
    # Check for specific activity type keys
    if "planGenerated" in activity_data:
        return ActivityType.PLAN_GENERATED
    elif "planApproved" in activity_data:
        return ActivityType.PLAN_APPROVED
    elif "sessionCompleted" in activity_data:
        return ActivityType.SESSION_COMPLETED
    elif "progressUpdated" in activity_data:
        return ActivityType.PROGRESS_UPDATED
    elif "userMessage" in activity_data or "agentMessage" in activity_data:
        return ActivityType.MESSAGE
    else:
        return ActivityType.UNKNOWN


def extract_error_from_activity(activity_data: dict) -> str | None:
    """Extract error message from activity if present"""
    # Check for bash output errors in artifacts
    if "artifacts" in activity_data:
        artifacts = activity_data["artifacts"]
        if isinstance(artifacts, list):
            for artifact in artifacts:
                # Check for bash output with non-zero exit code
                if "bashOutput" in artifact:
                    bash_output = artifact["bashOutput"]
                    exit_code = bash_output.get("exitCode", 0)
                    if exit_code != 0:
                        output = bash_output.get("output", "")
                        return f"Bash command failed (exit code {exit_code}): {output[:200]}"

    # Check for error indicators in progressUpdated
    if "progressUpdated" in activity_data:
        progress = activity_data["progressUpdated"]
        description = progress.get("description", "").lower()

        # Look for error keywords
        error_keywords = ["error", "failed", "exception", "fatal"]
        if any(keyword in description for keyword in error_keywords):
            return progress.get("description", "Unknown error")

    return None


def format_timestamp(iso_string: str) -> str:
    """Parse ISO timestamp and return human-readable format"""
    try:
        # Parse ISO 8601 format (e.g., "2025-11-01T14:30:15.123Z")
        # Handle both with and without timezone
        if iso_string.endswith("Z"):
            dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(iso_string)

        # Return in human-readable format
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        # Return original string if parsing fails
        return iso_string


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max_length with ellipsis suffix"""
    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."
