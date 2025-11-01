"""Manages multiple worker sessions with background polling"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from .jules_client import JulesAPIClient
from .state import WorkerState, WorkerSession, Activity

logger = logging.getLogger(__name__)


class WorkerManager:
    """Manages multiple Jules worker sessions with background polling"""

    def __init__(self, jules_client: JulesAPIClient, poll_interval: int, stuck_timeout: int):
        """
        Initialize worker manager

        Args:
            jules_client: Jules API client
            poll_interval: Seconds between polls for active workers
            stuck_timeout: Seconds of no activity before marking as stuck
        """
        self.jules_client = jules_client
        self.poll_interval = poll_interval
        self.stuck_timeout = stuck_timeout

        # Worker tracking
        self.workers: dict[str, WorkerSession] = {}
        self.polling_task: Optional[asyncio.Task] = None
        self.running = False

    async def start(self) -> None:
        """Start background polling task"""
        if self.running:
            logger.warning("Worker manager already running")
            return

        self.running = True
        self.polling_task = asyncio.create_task(self._polling_loop())
        logger.info("Worker manager started")

    async def stop(self) -> None:
        """Stop background polling task"""
        if not self.running:
            return

        self.running = False

        # Cancel and wait for polling task
        if self.polling_task:
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass

        logger.info("Worker manager stopped")

    async def create_worker(
        self,
        prompt: str,
        source: str,
        title: str,
        github_branch: str = "main"
    ) -> str:
        """
        Create a new worker Jules session

        Args:
            prompt: Task description for worker
            source: GitHub source (e.g., "sources/github/owner/repo")
            title: Short title for session
            github_branch: Branch to work on (default: "main")

        Returns:
            Session ID

        Raises:
            Exception: If session creation fails
        """
        # Create session via Jules API
        response = await self.jules_client.create_session(
            prompt=prompt,
            source=source,
            title=title,
            github_branch=github_branch
        )

        # Extract session ID
        session_id = response.get("name", "").split("/")[-1]

        if not session_id:
            raise Exception("Failed to extract session ID from response")

        # Create WorkerSession object
        now = datetime.now()
        worker = WorkerSession(
            session_id=session_id,
            task_description=prompt,
            source=source,
            state=WorkerState.PLANNING,
            created_at=now,
            last_activity_time=now,
            activities_buffer=[],
            pending_plan_id=None,
            error_message=None
        )

        # Add to workers dict
        self.workers[session_id] = worker

        logger.info(f"Created worker session: {session_id}")
        return session_id

    async def approve_worker_plan(self, session_id: str) -> None:
        """
        Approve a worker's generated plan

        Args:
            session_id: Worker session ID

        Raises:
            Exception: If worker not found or approval fails
        """
        if session_id not in self.workers:
            raise Exception(f"Worker not found: {session_id}")

        worker = self.workers[session_id]

        if worker.state != WorkerState.WAITING_APPROVAL:
            raise Exception(f"Worker is not waiting for approval (state: {worker.state})")

        # Approve plan via Jules API
        await self.jules_client.approve_plan(session_id)

        # Update worker state
        worker.state = WorkerState.EXECUTING
        worker.pending_plan_id = None

        logger.info(f"Approved plan for worker: {session_id}")

    async def send_worker_message(self, session_id: str, message: str) -> dict:
        """
        Send a message to a worker session

        Args:
            session_id: Worker session ID
            message: Message text

        Returns:
            Activity response

        Raises:
            Exception: If worker not found or message fails
        """
        if session_id not in self.workers:
            raise Exception(f"Worker not found: {session_id}")

        # Send message via Jules API
        response = await self.jules_client.send_message(session_id, message)

        logger.info(f"Sent message to worker: {session_id}")
        return response

    async def cancel_worker(self, session_id: str) -> None:
        """
        Cancel a worker session

        Args:
            session_id: Worker session ID

        Raises:
            Exception: If worker not found
        """
        if session_id not in self.workers:
            raise Exception(f"Worker not found: {session_id}")

        worker = self.workers[session_id]
        worker.state = WorkerState.CANCELLED

        logger.info(f"Cancelled worker: {session_id}")

    async def get_worker_activities(self, session_id: str, limit: int = 10) -> list[Activity]:
        """
        Get recent activities for a worker

        Args:
            session_id: Worker session ID
            limit: Maximum number of activities to return

        Returns:
            List of recent activities

        Raises:
            Exception: If worker not found
        """
        if session_id not in self.workers:
            raise Exception(f"Worker not found: {session_id}")

        worker = self.workers[session_id]
        return worker.activities_buffer[:limit]

    def get_all_workers(self) -> list[WorkerSession]:
        """
        Get all worker sessions

        Returns:
            List of all workers, sorted by created_at descending (newest first)
        """
        return sorted(
            self.workers.values(),
            key=lambda w: w.created_at,
            reverse=True
        )

    def get_worker_status(self, session_id: str) -> dict:
        """
        Get formatted status for a worker

        Args:
            session_id: Worker session ID

        Returns:
            Status dictionary with all relevant information

        Raises:
            Exception: If worker not found
        """
        if session_id not in self.workers:
            raise Exception(f"Worker not found: {session_id}")

        worker = self.workers[session_id]

        return {
            "session_id": session_id,
            "task": worker.task_description,
            "state": worker.state.value,
            "is_blocked": worker.is_blocked(),
            "blocker_reason": worker.get_blocker_reason(),
            "pending_plan_id": worker.pending_plan_id,
            "error_message": worker.error_message,
            "last_activity": worker.last_activity_time.isoformat(),
            "created_at": worker.created_at.isoformat()
        }

    async def _polling_loop(self) -> None:
        """Background polling loop to fetch activities for active workers"""
        logger.info("Polling loop started")

        while self.running:
            try:
                # Get active workers (not completed, failed, or cancelled)
                active_states = {
                    WorkerState.PLANNING,
                    WorkerState.WAITING_APPROVAL,
                    WorkerState.EXECUTING
                }

                active_workers = [
                    worker for worker in self.workers.values()
                    if worker.state in active_states
                ]

                # Poll each active worker
                for worker in active_workers:
                    try:
                        # Fetch latest activities
                        response = await self.jules_client.list_activities(
                            worker.session_id,
                            page_size=50
                        )

                        # Parse activities
                        activities_data = response.get("activities", [])
                        activities = [
                            Activity.from_api_response(data)
                            for data in activities_data
                        ]

                        # Update worker state
                        if activities:
                            worker.update_from_activities(
                                activities,
                                stuck_timeout=self.stuck_timeout
                            )

                    except Exception as e:
                        logger.error(f"Error polling worker {worker.session_id}: {e}")
                        # Continue polling other workers

                # Sleep before next poll
                await asyncio.sleep(self.poll_interval)

            except asyncio.CancelledError:
                logger.info("Polling loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                # Continue polling despite errors
                await asyncio.sleep(self.poll_interval)

        logger.info("Polling loop stopped")
