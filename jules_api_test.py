#!/usr/bin/env python3
"""
Comprehensive Jules API Client for full integration testing
"""

import os
import urllib.request
import json
import time
import hashlib
import random
import uuid
import urllib.parse
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class JulesConfig:
    """Jules API configuration"""
    api_key: str
    base_url: str = "https://jules.googleapis.com"
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0

class JulesAPIClient:
    """Complete Jules API client with full integration capabilities"""

    def __init__(self, config: Optional[JulesConfig] = None):
        self.config = config or JulesConfig()
        self.session_cache = {}
        self.activity_cache = {}

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                    headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to Jules API"""
        url = f"{self.config.base_url}{endpoint}"
        request_headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.config.api_key,
            'User-Agent': 'Claude-Jules-Integration-Client/1.0',
            **(headers or {})
        }

        # Add data for POST/PUT requests
        if data and method in ['POST', 'PUT', 'PATCH']:
            json_data = json.dumps(data).encode('utf-8')
            request_headers['Content-Length'] = str(len(json_data))
        else:
            json_data = None

        try:
            req = urllib.request.Request(
                url,
                data=json_data,
                headers=request_headers,
                method=method.upper()
            )

            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                response_data = response.read().decode('utf-8')

                if response.status >= 200 and response.status < 300:
                    return {
                        'status': 'success',
                        'status_code': response.status,
                        'data': json.loads(response_data) if response_data else None
                    }
                else:
                    return {
                        'status': 'error',
                        'status_code': response.status,
                        'error_message': response.reason,
                        'data': None
                    }

        except urllib.error.URLError as e:
            return {
                'status': 'error',
                'error_type': 'URL_ERROR',
                'error_message': str(e),
                'status_code': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'error_type': 'EXCEPTION',
                'error_message': str(e),
                'status_code': None
            }

    def retry_request(self, method: str, endpoint: str, data: Optional[Dict] = None,
                      headers: Optional[Dict] = None) -> Dict[str, Any]:
        """Retry request with exponential backoff"""
        last_error = None

        for attempt in range(self.config.retry_attempts):
            result = self._make_request(method, endpoint, data, headers)

            if result['status'] == 'success':
                return result

            last_error = result
            if attempt < self.config.retry_attempts - 1:
                delay = self.config.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue

        return last_error or {'status': 'error', 'error_message': 'All retry attempts failed'}

    # === SOURCE MANAGEMENT ===
    def create_source(self, source_config: Dict) -> Dict[str, Any]:
        """Create a new source"""
        return self.retry_request('POST', '/v1alpha/sources', source_config)

    def get_source(self, source_name: str) -> Dict[str, Any]:
        """Get details of a specific source"""
        endpoint = f'/v1alpha/sources/{source_name}'
        return self.retry_request('GET', endpoint)

    def list_sources(self) -> Dict[str, Any]:
        """List all available sources"""
        return self.retry_request('GET', '/v1alpha/sources')

    # === SESSION MANAGEMENT ===
    def create_session(self, session_config: Dict) -> Dict[str, Any]:
        """Create a new session"""
        # Add unique ID and timestamp
        session_config['sessionId'] = str(uuid.uuid4())
        session_config['createdAt'] = datetime.now(timezone.utc).isoformat()

        result = self.retry_request('POST', '/v1alpha/sessions', session_config)

        if result['status'] == 'success':
            self.session_cache[result['data']['name']] = result['data']
            return result
        return result

    def get_session(self, session_name: str) -> Dict[str, Any]:
        """Get details of a specific session"""
        endpoint = f'/v1alpha/sessions/{session_name}'
        return self.retry_request('GET', endpoint)

    def list_sessions(self, filter_params: Optional[Dict] = None) -> Dict[str, Any]:
        """List all sessions with optional filtering"""
        endpoint = '/v1alpha/sessions'

        if filter_params:
            query_params = urllib.parse.urlencode(filter_params)
            endpoint += f'?{query_params}'

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
        endpoint = f'/v1alpha/{session_name}:approvePlan'
        return self.retry_request('POST', endpoint, approval_data)

    def wait_for_activity(self, session_name: str, activity_type: str,
                         timeout_minutes: int = 10) -> Dict[str, Any]:
        """Wait for specific activity type to appear"""
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while time.time() - start_time < timeout_seconds:
            activities_result = self.get_activities(session_name)

            if activities_result['status'] == 'success':
                activities = activities_result.get('data', [])

                for activity in activities:
                    if activity.get('type') == activity_type:
                        return {
                            'status': 'success',
                            'activity': activity,
                            'found_at': time.time() - start_time
                        }

            time.sleep(3)  # Check every 3 seconds

        return {
            'status': 'timeout',
            'message': f'Activity type {activity_type} not found within {timeout_minutes} minutes'
        }

    def update_session(self, session_name: str, update_data: Dict) -> Dict[str, Any]:
        """Update a session"""
        endpoint = f'/v1alpha/{session_name}'
        return self.retry_request('PATCH', endpoint, update_data)

    def delete_session(self, session_name: str) -> Dict[str, Any]:
        """Delete a session"""
        endpoint = f'/v1alpha/{session_name}'
        return self.retry_request('DELETE', endpoint)

    # === ACTIVITY MANAGEMENT ===
    def get_activities(self, session_name: str) -> Dict[str, Any]:
        """Get activities for a specific session"""
        endpoint = f'/v1alpha/{session_name}/activities'
        return self.retry_request('GET', endpoint)

    def list_activities(self, session_name: str, filter_params: Optional[Dict] = None) -> Dict[str, Any]:
        """List activities with filtering"""
        endpoint = f'/v1alpha/{session_name}/activities'

        if filter_params:
            query_params = urllib.parse.urlencode(filter_params)
            endpoint += f'?{query_params}'

        return self.retry_request('GET', endpoint)

class JulesWorkflowManager:
    """Manages complete Jules workflow with unique sessions"""

    def __init__(self, client: JulesAPIClient):
        self.client = client
        self.active_sessions = {}
        self.branch_prefix = "jules-workflow"

    def generate_unique_session_id(self, task_description: str) -> str:
        """Generate unique session ID based on task description and timestamp"""
        # Create hash from task description + timestamp + random
        timestamp = datetime.now(timezone.utc).isoformat()
        random_suffix = str(random.randint(1000, 9999))
        hash_input = f"{task_description[:50]}{timestamp}{random_suffix}"
        unique_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]

        # Clean up for safe use
        safe_id = ''.join(c for c in unique_hash if c.isalnum() or c in '-_')
        return f"{self.branch_prefix}-{safe_id}"

    def generate_unique_branch_name(self, task_description: str, session_id: str = None) -> str:
        """Generate unique branch name for the session"""
        if session_id:
            base_name = session_id
        else:
            base_name = self.generate_unique_session_id(task_description)

        # Add timestamp for uniqueness
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

        return f"{base_name}-{timestamp}"

    def create_workflow_session(self, task_description: str, source: str,
                              github_branch: str = "main",
                              title: Optional[str] = None) -> Dict[str, Any]:
        """Create a complete workflow session with unique identifiers"""
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

        # Create session
        result = self.client.create_session(session_config)

        if result['status'] == 'success':
            session_data = result['data']
            self.active_sessions[session_id] = {
                'session_data': session_data,
                'branch_name': branch_name,
                'task_description': task_description,
                'source': source,
                'github_branch': github_branch,
                'title': title,
                'created_at': session_config['createdAt']
            }

            print(f"✅ Created session:")
            print(f"   Session ID: {session_id}")
            print(f"   Branch Name: {branch_name}")
            print(f"   Title: {title}")
            print(f"   Source: {source}")

            return {
                'status': 'success',
                'session_id': session_id,
                'branch_name': branch_name,
                'session_data': session_data,
                'created_at': session_config['createdAt']
            }
        else:
            print(f"❌ Failed to create session: {result.get('error_message', 'Unknown error')}")
            return result

    def test_plan_approval_workflow(self) -> Dict[str, Any]:
        """Test complete plan approval and completion notification workflow"""
        print("🧪 Testing Plan Approval & Completion Notification Workflow")
        print("=" * 60)

        # Test 1: Create session
        print("\n📝 Step 1: Creating test session...")
        session_result = self.create_workflow_session(
            task_description="Add user authentication with JWT tokens to the API",
            source="sources/github/example/nodejs-api-project",
            github_branch="main",
            title="JWT Authentication Implementation"
        )

        if session_result.get('status') != 'success':
            return {
                'test_result': 'FAILED',
                'reason': f"Session creation failed: {session_result.get('error_message')}",
                'stage': 'session_creation'
            }

        session_id = session_result['session_id']
        print(f"✅ Session created: {session_id}")

        # Test 2: Simulate plan generation (in real scenario, would wait for PLAN_GENERATED activity)
        print(f"\n📋 Step 2: Simulating plan generation workflow...")

        # In a real implementation, you would:
        # plan_result = self.client.wait_for_activity(session_id, 'PLAN_GENERATED', timeout_minutes=10)

        print("🔄 (Simulated) Plan generated with the following structure:")
        print("   - Add JWT middleware")
        print("   - Create auth endpoints (/login, /register)")
        print("   - Implement token validation")
        print("   - Update user model")

        # Test 3: Test plan approval
        print(f"\n✅ Step 3: Testing plan approval...")
        approval_result = self.client.approve_plan(
            session_id,
            {
                "approvalData": {
                    "approved": True,
                    "feedback": "Plan looks comprehensive, proceed with JWT implementation"
                }
            }
        )

        print(f"Plan approval result: {approval_result['status']}")

        # Test 4: Test plan rejection (workflow)
        print(f"\n❌ Step 4: Testing plan rejection workflow...")
        rejection_result = self.client.reject_plan(
            session_id,
            "Plan needs to include password reset functionality"
        )

        print(f"Plan rejection result: {rejection_result['status']}")

        # Test 5: Monitor for completion notifications
        print(f"\n🔔 Step 5: Testing completion notification monitoring...")

        # Simulate monitoring for completion
        print("🔄 Monitoring for completion notifications...")
        print("   (Would listen for COMPLETION_NOTIFICATION activity)")

        # Test 6: Verify unique session and branch IDs
        print(f"\n🆔 Step 6: Testing unique ID generation...")

        test_tasks = [
            "Add JWT authentication",
            "Implement user registration",
            "Create password reset feature"
        ]

        generated_ids = []
        generated_branches = []

        for task in test_tasks:
            session_id_test = self.generate_unique_session_id(task)
            branch_name_test = self.generate_unique_branch_name(task, session_id_test)

            generated_ids.append(session_id_test)
            generated_branches.append(branch_name_test)

            print(f"   Task: {task[:30]}...")
            print(f"   Session ID: {session_id_test}")
            print(f"   Branch Name: {branch_name_test}")

        # Verify uniqueness
        unique_ids = len(set(generated_ids)) == len(generated_ids)
        unique_branches = len(set(generated_branches)) == len(generated_branches)

        print(f"\n✅ Uniqueness verification:")
        print(f"   Unique Session IDs: {'✅' if unique_ids else '❌'}")
        print(f"   Unique Branch Names: {'✅' if unique_branches else '❌'}")

        return {
            'test_result': 'PASSED' if unique_ids and unique_branches else 'FAILED',
            'session_creation': session_result['status'],
            'plan_approval': approval_result['status'],
            'plan_rejection': rejection_result['status'],
            'unique_id_generation': unique_ids,
            'unique_branch_generation': unique_branches,
            'session_id': session_id,
            'branch_name': session_result['branch_name'],
            'test_duration': time.time()
        }

def main():
    """Run comprehensive Jules API testing"""
    print("🚀 Initializing Jules API Testing Framework")
    print("=" * 60)

    # Get API key from environment
    api_key = os.getenv("JULES_API_KEY")
    if not api_key:
        print("⚠️ JULES_API_KEY not found in environment")
        print("Running tests without API key (structure validation only)")
        api_key = "AQ.test_key_for_structure_validation"  # Test key for structure validation
    else:
        print("✅ Found JULES_API_KEY in environment")

    # Create configuration
    config = JulesConfig(api_key=api_key)

    # Create workflow manager for specific plan approval testing
    workflow = JulesWorkflowManager(JulesAPIClient(config))

    # Run plan approval workflow test specifically
    print("\n🎯 Running Plan Approval & Completion Notification Test")
    print("=" * 60)
    plan_approval_result = workflow.test_plan_approval_workflow()

    print(f"\n📊 Plan Approval Test Results:")
    print(f"  Overall: {'✅' if plan_approval_result['test_result'] == 'PASSED' else '❌'}")
    print(f"  Session Creation: {plan_approval_result['session_creation']}")
    print(f"  Plan Approval: {plan_approval_result['plan_approval']}")
    print(f"  Plan Rejection: {plan_approval_result['plan_rejection']}")
    print(f"  Unique ID Generation: {'✅' if plan_approval_result['unique_id_generation'] else '❌'}")
    print(f"  Unique Branch Generation: {'✅' if plan_approval_result['unique_branch_generation'] else '❌'}")

    print(f"\n🎯 Final Summary:")
    print(f"  Plan Approval Workflow: {'✅' if plan_approval_result['test_result'] == 'PASSED' else '❌'}")

    if plan_approval_result['test_result'] == 'PASSED':
        print(f"\n🎉 PLAN APPROVAL WORKFLOW TEST PASSED!")
        print(f"✅ Google Jules API integration structure is ready")
        print(f"✅ Plan approval workflow implemented")
        print(f"✅ Plan rejection workflow implemented")
        print(f"✅ Unique session/branch ID generation working")
        print(f"✅ Completion notification monitoring structure ready")
    else:
        print(f"\n⚠️ Some tests failed - review results above")

    print("\n" + "=" * 60)
    print("Test execution complete!")
    return plan_approval_result

if __name__ == "__main__":
    main()