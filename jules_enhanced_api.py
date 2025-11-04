#!/usr/bin/env python3
"""
Enhanced Jules API Client with comprehensive polling, throughput logging, and notifications
Based on official Google Jules API documentation and changelog analysis
"""

import os
import urllib.request
import json
import time
import hashlib
import random
import uuid
import urllib.parse
import threading
import logging
from typing import Dict, Optional, List, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, Future
from enum import Enum

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jules_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('JulesEnhancedAPI')

class SessionState(Enum):
    """Session states from Jules API"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class ActivityType(Enum):
    """Activity types from Jules API documentation"""
    PLAN_GENERATED = "PLAN_GENERATED"
    PLAN_APPROVED = "PLAN_APPROVED"
    PLAN_REJECTED = "PLAN_REJECTED"
    CODE_GENERATED = "CODE_GENERATED"
    MESSAGE_SENT = "MESSAGE_SENT"
    PROGRESS_UPDATE = "PROGRESS_UPDATE"
    ERROR = "ERROR"
    COMPLETION_NOTIFICATION = "COMPLETION_NOTIFICATION"

@dataclass
class ThroughputMetrics:
    """Comprehensive throughput tracking"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    response_times: List[float] = field(default_factory=list)
    session_creation_time: Optional[datetime] = None
    session_completion_time: Optional[datetime] = None
    activities_processed: int = 0
    polling_cycles: int = 0

    @property
    def success_rate(self) -> float:
        return self.successful_requests / max(self.total_requests, 1) * 100

    @property
    def average_response_time(self) -> float:
        return sum(self.response_times) / max(len(self.response_times), 1)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.session_creation_time and self.session_completion_time:
            return (self.session_completion_time - self.session_creation_time).total_seconds()
        return None

@dataclass
class JulesConfig:
    """Enhanced Jules API configuration"""
    api_key: str
    base_url: str = "https://jules.googleapis.com"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    polling_interval: int = 5  # seconds between polls
    max_polling_duration: int = 3600  # 1 hour max polling
    throughput_logging: bool = True
    enable_notifications: bool = True

class JulesEnhancedAPIClient:
    """Enhanced Jules API client with comprehensive monitoring and polling"""

    def __init__(self, config: Optional[JulesConfig] = None):
        self.config = config or JulesConfig()
        self.metrics = ThroughputMetrics()
        self.session_cache = {}
        self.activity_cache = {}
        self.active_pollers: Dict[str, Future] = {}
        self.notification_handlers: List[Callable] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self._setup_logging()

    def _setup_logging(self):
        """Setup comprehensive logging for throughput monitoring"""
        if self.config.throughput_logging:
            # Create throughput logger
            self.throughput_logger = logging.getLogger('JulesThroughput')
            handler = logging.FileHandler('jules_throughput.log')
            formatter = logging.Formatter(
                '%(asctime)s - REQUESTS:%(total_requests)d - SUCCESS_RATE:%(success_rate).2f%% - AVG_RESPONSE:%(avg_response).3fs'
            )
            handler.setFormatter(formatter)
            self.throughput_logger.addHandler(handler)

    def _log_throughput(self, start_time: float, bytes_sent: int, bytes_received: int, success: bool):
        """Log throughput metrics"""
        self.metrics.total_requests += 1
        self.metrics.bytes_sent += bytes_sent
        self.metrics.bytes_received += bytes_received

        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1

        response_time = time.time() - start_time
        self.metrics.response_times.append(response_time)

        if self.config.throughput_logging:
            logger.info(f"Request completed - Time: {response_time:.3f}s, Success: {success}, "
                       f"Total requests: {self.metrics.total_requests}, "
                       f"Success rate: {self.metrics.success_rate:.2f}%")

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                    headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request with comprehensive logging"""
        start_time = time.time()
        url = f"{self.config.base_url}{endpoint}"

        request_headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.config.api_key,
            'User-Agent': 'Jules-Enhanced-API-Client/2.0',
            **(headers or {})
        }

        # Prepare data and calculate bytes
        if data and method in ['POST', 'PUT', 'PATCH']:
            json_data = json.dumps(data).encode('utf-8')
            request_headers['Content-Length'] = str(len(json_data))
            bytes_sent = len(json_data)
        else:
            json_data = None
            bytes_sent = 0

        try:
            logger.debug(f"Making {method} request to {url}")

            req = urllib.request.Request(
                url,
                data=json_data,
                headers=request_headers,
                method=method.upper()
            )

            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                response_data = response.read().decode('utf-8')
                bytes_received = len(response_data)

                success = 200 <= response.status < 300

                self._log_throughput(start_time, bytes_sent, bytes_received, success)

                if success:
                    return {
                        'status': 'success',
                        'status_code': response.status,
                        'data': json.loads(response_data) if response_data else None,
                        'bytes_received': bytes_received
                    }
                else:
                    return {
                        'status': 'error',
                        'status_code': response.status,
                        'error_message': response.reason,
                        'data': None
                    }

        except urllib.error.URLError as e:
            self._log_throughput(start_time, bytes_sent, 0, False)
            logger.error(f"URL Error for {url}: {str(e)}")
            return {
                'status': 'error',
                'error_type': 'URL_ERROR',
                'error_message': str(e),
                'status_code': None
            }
        except Exception as e:
            self._log_throughput(start_time, bytes_sent, 0, False)
            logger.error(f"Exception for {url}: {str(e)}")
            return {
                'status': 'error',
                'error_type': 'EXCEPTION',
                'error_message': str(e),
                'status_code': None
            }

    def retry_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                      headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Retry request with exponential backoff and detailed logging"""
        last_error = None
        retry_count = 0

        for attempt in range(self.config.retry_attempts):
            result = self._make_request(method, endpoint, data, headers)

            if result['status'] == 'success':
                if retry_count > 0:
                    logger.info(f"Request succeeded after {retry_count} retries")
                return result

            last_error = result
            retry_count = attempt + 1

            if attempt < self.config.retry_attempts - 1:
                delay = self.config.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Request failed (attempt {retry_count}/{self.config.retry_attempts}), "
                             f"retrying in {delay:.2f}s: {result.get('error_message', 'Unknown error')}")
                time.sleep(delay)

        logger.error(f"All {self.config.retry_attempts} retry attempts failed for {method} {endpoint}")
        return last_error or {'status': 'error', 'error_message': 'All retry attempts failed'}

    # === SESSION MANAGEMENT WITH POLLING ===

    def create_session(self, session_config: Dict) -> Dict[str, Any]:
        """Create a new session with enhanced logging"""
        logger.info(f"Creating new session with title: {session_config.get('title', 'Untitled')}")

        # Add unique ID and timestamp
        session_id = str(uuid.uuid4())
        session_config['sessionId'] = session_id
        session_config['createdAt'] = datetime.now(timezone.utc).isoformat()

        result = self.retry_request('POST', '/v1alpha/sessions', session_config)

        if result['status'] == 'success':
            session_data = result['data']
            self.session_cache[session_data.get('name', session_id)] = session_data
            self.metrics.session_creation_time = datetime.now(timezone.utc)

            logger.info(f"Session created successfully: {session_data.get('name', session_id)}")

            # Start automatic polling if enabled
            if self.config.enable_notifications:
                self._start_session_polling(session_data.get('name', session_id))

            return result
        else:
            logger.error(f"Session creation failed: {result.get('error_message')}")
            return result

    def get_session(self, session_name: str) -> Dict[str, Any]:
        """Get session details with caching"""
        if session_name in self.session_cache:
            cached = self.session_cache[session_name]
            # Check if cache is fresh (less than 30 seconds old)
            if time.time() - cached.get('cached_at', 0) < 30:
                return {'status': 'success', 'data': cached['data'], 'cached': True}

        result = self.retry_request('GET', f'/v1alpha/sessions/{session_name}')

        if result['status'] == 'success':
            self.session_cache[session_name] = {
                'data': result['data'],
                'cached_at': time.time()
            }

        return result

    def _start_session_polling(self, session_name: str):
        """Start background polling for session updates"""
        if session_name in self.active_pollers:
            logger.warning(f"Polling already active for session: {session_name}")
            return

        logger.info(f"Starting session polling for: {session_name}")

        future = self.executor.submit(self._poll_session_until_complete, session_name)
        self.active_pollers[session_name] = future

    def _poll_session_until_complete(self, session_name: str) -> Dict[str, Any]:
        """Poll session until completion with comprehensive monitoring"""
        start_time = time.time()
        last_activity_count = 0
        last_activity_hash = ""

        logger.info(f"Beginning session polling for {session_name}")

        while time.time() - start_time < self.config.max_polling_duration:
            self.metrics.polling_cycles += 1

            # Get session status
            session_result = self.get_session(session_name)

            if session_result['status'] != 'success':
                logger.error(f"Failed to get session status for {session_name}: {session_result.get('error_message')}")
                time.sleep(self.config.polling_interval)
                continue

            session_data = session_result['data']
            current_state = session_data.get('state', SessionState.ACTIVE.value)

            # Get activities to check for updates
            activities_result = self.get_activities(session_name, page_size=50)

            if activities_result['status'] == 'success':
                activities = activities_result.get('data', [])
                self.metrics.activities_processed += len(activities)

                # Check for new activities
                current_activity_hash = self._hash_activities(activities)

                if len(activities) != last_activity_count or current_activity_hash != last_activity_hash:
                    new_activities = activities[last_activity_count:]

                    for activity in new_activities:
                        self._handle_activity_update(session_name, activity)

                    last_activity_count = len(activities)
                    last_activity_hash = current_activity_hash

            # Check if session is in terminal state
            if current_state in [SessionState.COMPLETED.value, SessionState.FAILED.value, SessionState.CANCELLED.value]:
                self.metrics.session_completion_time = datetime.now(timezone.utc)

                final_result = {
                    'session_name': session_name,
                    'final_state': current_state,
                    'duration_seconds': time.time() - start_time,
                    'total_activities': last_activity_count,
                    'polling_cycles': self.metrics.polling_cycles,
                    'throughput_metrics': self._serialize_metrics()
                }

                logger.info(f"Session {session_name} completed with state: {current_state}")
                self._notify_completion(session_name, final_result)

                # Clean up polling
                if session_name in self.active_pollers:
                    del self.active_pollers[session_name]

                return final_result

            # Wait before next poll
            time.sleep(self.config.polling_interval)

        # Polling timeout
        logger.warning(f"Polling timed out for session: {session_name}")

        if session_name in self.active_pollers:
            del self.active_pollers[session_name]

        return {
            'session_name': session_name,
            'status': 'TIMEOUT',
            'duration_seconds': time.time() - start_time,
            'polling_cycles': self.metrics.polling_cycles
        }

    def _hash_activities(self, activities: List[Dict]) -> str:
        """Create hash of activities for change detection"""
        activity_str = json.dumps(activities, sort_keys=True, default=str)
        return hashlib.md5(activity_str.encode()).hexdigest()

    def _handle_activity_update(self, session_name: str, activity: Dict):
        """Handle new activity with notification dispatch"""
        activity_type = activity.get('type', 'UNKNOWN')
        activity_message = activity.get('message', '')

        logger.info(f"New activity for {session_name}: {activity_type} - {activity_message[:100]}...")

        # Dispatch to notification handlers
        if self.config.enable_notifications:
            for handler in self.notification_handlers:
                try:
                    handler(session_name, activity)
                except Exception as e:
                    logger.error(f"Notification handler failed: {str(e)}")

    def _notify_completion(self, session_name: str, result: Dict):
        """Notify all handlers of session completion"""
        logger.info(f"Notifying completion for session {session_name}: {result['final_state']}")

        completion_activity = {
            'type': ActivityType.COMPLETION_NOTIFICATION.value,
            'message': f"Session completed with state: {result['final_state']}",
            'data': result
        }

        for handler in self.notification_handlers:
            try:
                handler(session_name, completion_activity)
            except Exception as e:
                logger.error(f"Completion notification handler failed: {str(e)}")

    def get_activities(self, session_name: str, page_size: int = 50, page_token: str = None) -> Dict[str, Any]:
        """Get activities with pagination support"""
        endpoint = f'/v1alpha/sessions/{session_name}/activities'
        params = {'pageSize': page_size}

        if page_token:
            params['pageToken'] = page_token

        query_string = urllib.parse.urlencode(params)
        endpoint += f'?{query_string}'

        return self.retry_request('GET', endpoint)

    def approve_plan(self, session_name: str, approval_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Approve a plan in a session"""
        if approval_data is None:
            approval_data = {
                "approvalData": {
                    "approved": True,
                    "feedback": "Plan approved, proceed with implementation"
                }
            }

        logger.info(f"Approving plan for session: {session_name}")
        endpoint = f'/v1alpha/{session_name}:approvePlan'
        return self.retry_request('POST', endpoint, approval_data)

    def reject_plan(self, session_name: str, feedback: str = "Plan rejected, please revise") -> Dict[str, Any]:
        """Reject a plan in a session"""
        approval_data = {
            "approvalData": {
                "approved": False,
                "feedback": feedback
            }
        }

        logger.info(f"Rejecting plan for session: {session_name} - {feedback}")
        endpoint = f'/v1alpha/{session_name}:approvePlan'
        return self.retry_request('POST', endpoint, approval_data)

    # === NOTIFICATION SYSTEM ===

    def add_notification_handler(self, handler: Callable[[str, Dict], None]):
        """Add a notification handler for activity updates"""
        self.notification_handlers.append(handler)
        logger.info(f"Added notification handler (total: {len(self.notification_handlers)})")

    def remove_notification_handler(self, handler: Callable[[str, Dict], None]):
        """Remove a notification handler"""
        if handler in self.notification_handlers:
            self.notification_handlers.remove(handler)
            logger.info(f"Removed notification handler (total: {len(self.notification_handlers)})")

    def stop_session_polling(self, session_name: str):
        """Stop polling for a specific session"""
        if session_name in self.active_pollers:
            future = self.active_pollers[session_name]
            future.cancel()
            del self.active_pollers[session_name]
            logger.info(f"Stopped polling for session: {session_name}")
            return True
        return False

    def get_active_polling_sessions(self) -> List[str]:
        """Get list of sessions being actively polled"""
        return list(self.active_pollers.keys())

    # === THROUGHPUT AND METRICS ===

    def _serialize_metrics(self) -> Dict[str, Any]:
        """Serialize metrics for logging/notification"""
        return {
            'total_requests': self.metrics.total_requests,
            'successful_requests': self.metrics.successful_requests,
            'failed_requests': self.metrics.failed_requests,
            'success_rate': self.metrics.success_rate,
            'average_response_time': self.metrics.average_response_time,
            'bytes_sent': self.metrics.bytes_sent,
            'bytes_received': self.metrics.bytes_received,
            'activities_processed': self.metrics.activities_processed,
            'polling_cycles': self.metrics.polling_cycles,
            'duration_seconds': self.metrics.duration_seconds
        }

    def get_throughput_metrics(self) -> Dict[str, Any]:
        """Get current throughput metrics"""
        return self._serialize_metrics()

    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = ThroughputMetrics()
        logger.info("Metrics reset")

    def generate_throughput_report(self) -> str:
        """Generate human-readable throughput report"""
        metrics = self._serialize_metrics()

        report = f"""
=== Jules API Throughput Report ===
Generated: {datetime.now(timezone.utc).isoformat()}

Request Statistics:
- Total Requests: {metrics['total_requests']}
- Successful: {metrics['successful_requests']}
- Failed: {metrics['failed_requests']}
- Success Rate: {metrics['success_rate']:.2f}%
- Average Response Time: {metrics['average_response_time']:.3f}s

Data Transfer:
- Bytes Sent: {metrics['bytes_sent']:,}
- Bytes Received: {metrics['bytes_received']:,}

Session Activity:
- Activities Processed: {metrics['activities_processed']}
- Polling Cycles: {metrics['polling_cycles']}

Duration: {metrics['duration_seconds']}s if available else 'N/A'}
Active Polling Sessions: {len(self.active_pollers)}
"""
        return report

    # === CLEANUP ===

    def shutdown(self):
        """Graceful shutdown of the client"""
        logger.info("Shutting down Jules Enhanced API Client")

        # Cancel all active polling
        for session_name in list(self.active_pollers.keys()):
            self.stop_session_polling(session_name)

        # Shutdown thread pool
        self.executor.shutdown(wait=True)

        logger.info("Shutdown complete")

# === ENHANCED WORKFLOW MANAGER ===

class JulesEnhancedWorkflowManager:
    """Enhanced workflow manager with comprehensive monitoring and automation"""

    def __init__(self, client: JulesEnhancedAPIClient):
        self.client = client
        self.active_sessions = {}
        self.branch_prefix = "jules-workflow"
        self.workflow_metrics = {}

    def generate_unique_session_id(self, task_description: str) -> str:
        """Generate unique session ID based on task description and timestamp"""
        timestamp = datetime.now(timezone.utc).isoformat()
        random_suffix = str(random.randint(1000, 9999))
        hash_input = f"{task_description[:50]}{timestamp}{random_suffix}"
        unique_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]

        safe_id = ''.join(c for c in unique_hash if c.isalnum() or c in '-_')
        return f"{self.branch_prefix}-{safe_id}"

    def generate_unique_branch_name(self, task_description: str, session_id: str = None) -> str:
        """Generate unique branch name for the session"""
        if session_id:
            base_name = session_id
        else:
            base_name = self.generate_unique_session_id(task_description)

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"{base_name}-{timestamp}"

    def create_monitored_session(self, task_description: str, source: str,
                               github_branch: str = "main",
                               title: Optional[str] = None,
                               notification_handlers: List[Callable] = None) -> Dict[str, Any]:
        """Create a session with comprehensive monitoring"""
        session_id = self.generate_unique_session_id(task_description)
        branch_name = self.generate_unique_branch_name(task_description, session_id)

        if not title:
            title = f"Task: {task_description[:50]}..."

        session_config = {
            'sessionId': session_id,
            'name': title,
            'prompt': task_description,
            'sourceContext': {
                'source': source,
                'githubRepoContext': {
                    'startingBranch': github_branch
                }
            }
        }

        # Add notification handlers if provided
        if notification_handlers:
            for handler in notification_handlers:
                self.client.add_notification_handler(handler)

        # Create session
        result = self.client.create_session(session_config)

        if result['status'] == 'success':
            session_data = result['data']
            session_key = session_data.get('name', session_id)

            self.active_sessions[session_key] = {
                'session_data': session_data,
                'branch_name': branch_name,
                'task_description': task_description,
                'source': source,
                'github_branch': github_branch,
                'title': title,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'metrics_start': ThroughputMetrics()
            }

            logger.info(f"Created monitored session: {session_key}")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"Branch Name: {branch_name}")
            logger.info(f"Source: {source}")

            return {
                'status': 'success',
                'session_id': session_id,
                'session_name': session_key,
                'branch_name': branch_name,
                'session_data': session_data
            }
        else:
            logger.error(f"Failed to create monitored session: {result.get('error_message')}")
            return result

    def wait_for_activity_with_timeout(self, session_name: str, activity_type: str,
                                     timeout_minutes: int = 10) -> Dict[str, Any]:
        """Wait for specific activity type with timeout and comprehensive logging"""
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        logger.info(f"Waiting for activity '{activity_type}' on session '{session_name}' "
                   f"(timeout: {timeout_minutes} minutes)")

        while time.time() - start_time < timeout_seconds:
            activities_result = self.client.get_activities(session_name)

            if activities_result['status'] == 'success':
                activities = activities_result.get('data', [])

                for activity in activities:
                    if activity.get('type') == activity_type:
                        duration = time.time() - start_time
                        logger.info(f"Activity '{activity_type}' found after {duration:.1f} seconds")

                        return {
                            'status': 'success',
                            'activity': activity,
                            'found_at': duration,
                            'activities_checked': len(activities)
                        }

            time.sleep(3)  # Check every 3 seconds

        duration = time.time() - start_time
        logger.warning(f"Activity '{activity_type}' not found within {timeout_minutes} minutes "
                      f"(searched for {duration:.1f} seconds)")

        return {
            'status': 'timeout',
            'message': f'Activity type {activity_type} not found within {timeout_minutes} minutes',
            'search_duration': duration
        }

# === EXAMPLE USAGE ===

def create_slack_notification_handler(webhook_url: str) -> Callable:
    """Create a Slack notification handler"""
    def slack_handler(session_name: str, activity: Dict):
        activity_type = activity.get('type', 'UNKNOWN')
        message = activity.get('message', 'No message')

        slack_payload = {
            "text": f"Jules Session Update: {session_name}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Jules Session:* `{session_name}`\n*Activity:* `{activity_type}`"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Message:* {message[:200]}..."
                    }
                }
            ]
        }

        try:
            data = json.dumps(slack_payload).encode('utf-8')
            req = urllib.request.Request(
                webhook_url,
                data=data,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    logger.info(f"Slack notification sent for {session_name}")
                else:
                    logger.error(f"Slack notification failed: {response.status}")

        except Exception as e:
            logger.error(f"Failed to send Slack notification: {str(e)}")

    return slack_handler

def main():
    """Example usage of the enhanced Jules API client"""
    print("🚀 Initializing Enhanced Jules API Client")
    print("=" * 60)

    # Get API key from environment
    api_key = os.getenv("JULES_API_KEY")
    if not api_key:
        print("⚠️ JULES_API_KEY not found in environment")
        print("Running in demo mode without API key")
        api_key = "AQ.demo_key_for_testing"  # Demo key
    else:
        print("✅ Found JULES_API_KEY in environment")

    # Create enhanced configuration
    config = JulesConfig(
        api_key=api_key,
        polling_interval=5,
        max_polling_duration=1800,  # 30 minutes
        throughput_logging=True,
        enable_notifications=True
    )

    # Create enhanced client
    client = JulesEnhancedAPIClient(config)

    # Add notification handlers
    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
    if slack_webhook:
        slack_handler = create_slack_notification_handler(slack_webhook)
        client.add_notification_handler(slack_handler)
        print("✅ Slack notifications enabled")

    # Create workflow manager
    workflow = JulesEnhancedWorkflowManager(client)

    try:
        # Example: Create a monitored session
        print("\n📝 Creating monitored session...")

        def console_notification_handler(session_name: str, activity: Dict):
            activity_type = activity.get('type', 'UNKNOWN')
            message = activity.get('message', 'No message')
            print(f"🔔 [{activity_type}] {session_name}: {message[:100]}...")

        result = workflow.create_monitored_session(
            task_description="Add user authentication with JWT tokens to the API",
            source="sources/github/example/nodejs-api-project",
            github_branch="main",
            title="JWT Authentication Implementation",
            notification_handlers=[console_notification_handler]
        )

        if result['status'] == 'success':
            print(f"✅ Session created: {result['session_name']}")

            # Monitor for a while
            print("\n🔄 Monitoring session for 30 seconds...")
            time.sleep(30)

            # Get throughput metrics
            metrics = client.get_throughput_metrics()
            print(f"\n📊 Throughput Metrics:")
            print(f"   Total Requests: {metrics['total_requests']}")
            print(f"   Success Rate: {metrics['success_rate']:.2f}%")
            print(f"   Avg Response Time: {metrics['average_response_time']:.3f}s")
            print(f"   Activities Processed: {metrics['activities_processed']}")
            print(f"   Polling Cycles: {metrics['polling_cycles']}")

            # Generate full report
            print(f"\n{client.generate_throughput_report()}")
        else:
            print(f"❌ Session creation failed: {result.get('error_message')}")

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.exception("Error in main execution")
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        client.shutdown()
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()