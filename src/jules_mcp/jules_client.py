"""Async HTTP client for Jules REST API"""

import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class JulesAPIClient:
    """Client for interacting with Jules REST API"""

    def __init__(self, api_key: str, base_url: str, api_version: str):
        """
        Initialize Jules API client

        Args:
            api_key: Jules API key for authentication
            base_url: Base URL for Jules API (e.g., https://jules.googleapis.com)
            api_version: API version (e.g., v1alpha)
        """
        self.api_key = api_key
        self.base_url = f"{base_url}/{api_version}"

        # Create async HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-Goog-Api-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def create_session(
        self,
        prompt: str,
        source: str,
        title: str,
        github_branch: str = "main"
    ) -> dict:
        """
        Create a new Jules session

        Args:
            prompt: Task description for Jules
            source: GitHub source (e.g., "sources/github/owner/repo")
            title: Short title for the session
            github_branch: Branch to work on (default: "main")

        Returns:
            Full session response JSON

        Raises:
            Exception: If API request fails
        """
        try:
            body = {
                "prompt": prompt,
                "sourceContext": {
                    "source": source,
                    "githubRepoContext": {
                        "startingBranch": github_branch
                    }
                },
                "title": title
            }

            response = await self.client.post("/sessions", json=body)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"Failed to create session (HTTP {e.response.status_code}): {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Failed to create session (Network error): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    async def get_session(self, session_id: str) -> dict:
        """
        Get session details

        Args:
            session_id: Jules session ID

        Returns:
            Session details JSON

        Raises:
            Exception: If API request fails or session not found
        """
        try:
            response = await self.client.get(f"/sessions/{session_id}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = f"Session not found: {session_id}"
            else:
                error_msg = f"Failed to get session (HTTP {e.response.status_code}): {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Failed to get session (Network error): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    async def list_activities(
        self,
        session_id: str,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> dict:
        """
        List activities for a session

        Args:
            session_id: Jules session ID
            page_size: Number of activities to fetch (default: 50)
            page_token: Optional pagination token

        Returns:
            Response with 'activities' array and optional 'nextPageToken'

        Raises:
            Exception: If API request fails
        """
        try:
            params = {"pageSize": page_size}
            if page_token:
                params["pageToken"] = page_token

            response = await self.client.get(
                f"/sessions/{session_id}/activities",
                params=params
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"Failed to list activities (HTTP {e.response.status_code}): {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Failed to list activities (Network error): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    async def approve_plan(self, session_id: str) -> None:
        """
        Approve a generated plan

        Args:
            session_id: Jules session ID

        Raises:
            Exception: If API request fails
        """
        try:
            response = await self.client.post(f"/sessions/{session_id}:approvePlan")
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            error_msg = f"Failed to approve plan (HTTP {e.response.status_code}): {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Failed to approve plan (Network error): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    async def send_message(self, session_id: str, message: str) -> dict:
        """
        Send a message to a session

        Args:
            session_id: Jules session ID
            message: Message text to send

        Returns:
            Activity response

        Raises:
            Exception: If API request fails
        """
        try:
            body = {
                "userMessage": {
                    "message": message
                }
            }

            response = await self.client.post(
                f"/sessions/{session_id}/activities",
                json=body
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_msg = f"Failed to send message (HTTP {e.response.status_code}): {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
        except httpx.RequestError as e:
            error_msg = f"Failed to send message (Network error): {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg) from e

    async def close(self) -> None:
        """Close the HTTP client and cleanup connections"""
        await self.client.aclose()
