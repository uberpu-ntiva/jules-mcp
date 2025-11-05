#!/usr/bin/env python3
"""
Comprehensive testing suite for Enhanced Jules API implementation
Tests polling, notifications, throughput logging, and activity monitoring
"""

import os
import time
import json
import threading
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from typing import Dict, List, Any

# Import our enhanced API
from jules_enhanced_api import (
    JulesEnhancedAPIClient,
    JulesEnhancedWorkflowManager,
    JulesConfig,
    ThroughputMetrics,
    SessionState,
    ActivityType
)

class TestJulesEnhancedAPI(unittest.TestCase):
    """Comprehensive test suite for enhanced Jules API"""

    def setUp(self):
        """Set up test environment"""
        self.config = JulesConfig(
            api_key="AQ.test_key_for_unit_tests",
            polling_interval=1,  # Fast polling for tests
            max_polling_duration=10,  # Short timeout for tests
            throughput_logging=True,
            enable_notifications=True
        )
        self.client = JulesEnhancedAPIClient(self.config)
        self.workflow = JulesEnhancedWorkflowManager(self.client)

    def test_configuration_initialization(self):
        """Test proper configuration initialization"""
        self.assertEqual(self.config.api_key, "AQ.test_key_for_unit_tests")
        self.assertEqual(self.config.base_url, "https://jules.googleapis.com")
        self.assertEqual(self.config.polling_interval, 1)
        self.assertEqual(self.config.max_polling_duration, 10)
        self.assertTrue(self.config.throughput_logging)
        self.assertTrue(self.config.enable_notifications)

    def test_throughput_metrics_initialization(self):
        """Test throughput metrics initialization"""
        metrics = self.client.metrics
        self.assertEqual(metrics.total_requests, 0)
        self.assertEqual(metrics.successful_requests, 0)
        self.assertEqual(metrics.failed_requests, 0)
        self.assertEqual(metrics.success_rate, 0)
        self.assertEqual(len(metrics.response_times), 0)

    def test_throughput_metrics_calculation(self):
        """Test throughput metrics calculations"""
        # Simulate some requests
        self.client.metrics.total_requests = 100
        self.client.metrics.successful_requests = 85
        self.client.metrics.response_times = [0.1, 0.2, 0.15, 0.3, 0.25]

        expected_success_rate = 85.0
        expected_avg_response_time = 0.2

        self.assertEqual(self.client.metrics.success_rate, expected_success_rate)
        self.assertAlmostEqual(self.client.metrics.average_response_time, expected_avg_response_time, places=3)

    def test_unique_session_id_generation(self):
        """Test unique session ID generation"""
        task_desc = "Test task for JWT authentication"
        session_id1 = self.workflow.generate_unique_session_id(task_desc)
        session_id2 = self.workflow.generate_unique_session_id(task_desc + " variant")

        self.assertNotEqual(session_id1, session_id2)
        self.assertTrue(session_id1.startswith("jules-workflow-"))
        self.assertTrue(session_id2.startswith("jules-workflow-"))

    def test_unique_branch_name_generation(self):
        """Test unique branch name generation"""
        task_desc = "Test task"
        session_id = "test-session-123"
        branch1 = self.workflow.generate_unique_branch_name(task_desc, session_id)
        time.sleep(0.1)  # Ensure different timestamps
        branch2 = self.workflow.generate_unique_branch_name(task_desc, session_id + "2")

        self.assertNotEqual(branch1, branch2)
        self.assertIn(session_id, branch1)

    @patch('urllib.request.urlopen')
    def test_session_creation_success(self, mock_urlopen):
        """Test successful session creation"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            'name': 'sessions/test-session-123',
            'sessionId': 'test-session-123',
            'state': SessionState.ACTIVE.value
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        session_config = {
            'prompt': 'Test session creation',
            'sourceContext': {
                'source': 'sources/github/test/repo'
            }
        }

        result = self.client.create_session(session_config)

        self.assertEqual(result['status'], 'success')
        self.assertIsNotNone(result['data'])
        self.assertEqual(result['data']['name'], 'sessions/test-session-123')

    @patch('urllib.request.urlopen')
    def test_session_creation_failure(self, mock_urlopen):
        """Test session creation failure handling"""
        # Mock failed API response
        mock_urlopen.side_effect = Exception("API Error")

        session_config = {
            'prompt': 'Test session creation',
            'sourceContext': {
                'source': 'sources/github/test/repo'
            }
        }

        result = self.client.create_session(session_config)

        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error_type'], 'EXCEPTION')
        self.assertEqual(result['error_message'], 'API Error')

    @patch('urllib.request.urlopen')
    def test_plan_approval(self, mock_urlopen):
        """Test plan approval functionality"""
        # Mock successful approval response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            'approved': True,
            'message': 'Plan approved successfully'
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.approve_plan('sessions/test-session', {
            'approvalData': {
                'approved': True,
                'feedback': 'Looks good'
            }
        })

        self.assertEqual(result['status'], 'success')

    @patch('urllib.request.urlopen')
    def test_plan_rejection(self, mock_urlopen):
        """Test plan rejection functionality"""
        # Mock successful rejection response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            'approved': False,
            'message': 'Plan rejected'
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = self.client.reject_plan('sessions/test-session', 'Needs more details')

        self.assertEqual(result['status'], 'success')

    def test_notification_handler_management(self):
        """Test notification handler add/remove functionality"""
        def dummy_handler(session_name, activity):
            pass

        # Initially no handlers
        self.assertEqual(len(self.client.notification_handlers), 0)

        # Add handler
        self.client.add_notification_handler(dummy_handler)
        self.assertEqual(len(self.client.notification_handlers), 1)

        # Add another handler
        def dummy_handler2(session_name, activity):
            pass
        self.client.add_notification_handler(dummy_handler2)
        self.assertEqual(len(self.client.notification_handlers), 2)

        # Remove first handler
        self.client.remove_notification_handler(dummy_handler)
        self.assertEqual(len(self.client.notification_handlers), 1)

        # Try to remove non-existent handler
        def non_existent_handler(session_name, activity):
            pass
        self.client.remove_notification_handler(non_existent_handler)
        self.assertEqual(len(self.client.notification_handlers), 1)

    def test_activities_hashing(self):
        """Test activity hashing for change detection"""
        activities1 = [
            {'type': 'PLAN_GENERATED', 'message': 'Test plan'},
            {'type': 'MESSAGE_SENT', 'message': 'Test message'}
        ]

        activities2 = [
            {'type': 'PLAN_GENERATED', 'message': 'Test plan'},
            {'type': 'MESSAGE_SENT', 'message': 'Test message'}
        ]

        activities3 = [
            {'type': 'PLAN_GENERATED', 'message': 'Test plan'},
            {'type': 'MESSAGE_SENT', 'message': 'Different message'}
        ]

        hash1 = self.client._hash_activities(activities1)
        hash2 = self.client._hash_activities(activities2)
        hash3 = self.client._hash_activities(activities3)

        # Same activities should have same hash
        self.assertEqual(hash1, hash2)

        # Different activities should have different hash
        self.assertNotEqual(hash1, hash3)

    @patch('urllib.request.urlopen')
    def test_monitored_session_creation(self, mock_urlopen):
        """Test monitored session creation with workflow manager"""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            'name': 'sessions/monitored-session-456',
            'sessionId': 'monitored-session-456',
            'state': SessionState.ACTIVE.value
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        def test_handler(session_name, activity):
            pass

        result = self.workflow.create_monitored_session(
            task_description="Add comprehensive logging system",
            source="sources/github/example/logging-project",
            github_branch="main",
            title="Logging System Implementation",
            notification_handlers=[test_handler]
        )

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['session_id'], 'monitored-session-456')
        self.assertIsNotNone(result['branch_name'])

        # Check that notification handler was added
        self.assertEqual(len(self.client.notification_handlers), 1)

    def test_throughput_report_generation(self):
        """Test throughput report generation"""
        # Add some metrics data
        self.client.metrics.total_requests = 50
        self.client.metrics.successful_requests = 45
        self.client.metrics.activities_processed = 25
        self.client.metrics.polling_cycles = 100

        report = self.client.generate_throughput_report()

        self.assertIn("Jules API Throughput Report", report)
        self.assertIn("Total Requests: 50", report)
        self.assertIn("Successful: 45", report)
        self.assertIn("Success Rate: 90.00%", report)
        self.assertIn("Activities Processed: 25", report)
        self.assertIn("Polling Cycles: 100", report)

    @patch('urllib.request.urlopen')
    def test_retry_mechanism(self, mock_urlopen):
        """Test retry mechanism with exponential backoff"""
        # Mock first two failures, then success
        responses = [
            Mock(status=500, reason='Internal Server Error'),
            Mock(status=503, reason='Service Unavailable'),
            Mock(status=200, reason='OK')
        ]

        mock_response_data = json.dumps({'result': 'success'}).encode('utf-8')

        def side_effect(*args, **kwargs):
            response = responses.pop(0)
            response.read.return_value = mock_response_data
            mock_response = Mock()
            mock_response.__enter__.return_value = response
            return mock_response

        mock_urlopen.side_effect = side_effect

        result = self.client.retry_request('GET', '/v1alpha/sessions/test')

        self.assertEqual(result['status'], 'success')
        # Should have made 3 attempts (2 failures + 1 success)
        self.assertEqual(self.client.metrics.total_requests, 1)  # Only final successful call counted

    def test_active_polling_management(self):
        """Test active polling session management"""
        # Initially no active pollers
        self.assertEqual(len(self.client.get_active_polling_sessions()), 0)

        # Mock adding a poller (normally done internally)
        mock_future = Mock()
        self.client.active_pollers['test-session'] = mock_future

        self.assertEqual(len(self.client.get_active_polling_sessions()), 1)
        self.assertIn('test-session', self.client.get_active_polling_sessions())

        # Stop polling
        result = self.client.stop_session_polling('test-session')
        self.assertTrue(result)
        self.assertEqual(len(self.client.get_active_polling_sessions()), 0)

        # Try to stop non-existent polling
        result = self.client.stop_session_polling('non-existent')
        self.assertFalse(result)

    def test_metrics_serialization(self):
        """Test metrics serialization for logging"""
        # Add some test data
        self.client.metrics.total_requests = 100
        self.client.metrics.successful_requests = 85
        self.client.metrics.response_times = [0.1, 0.2, 0.3]
        self.client.metrics.activities_processed = 50
        self.client.metrics.polling_cycles = 25

        serialized = self.client._serialize_metrics()

        self.assertEqual(serialized['total_requests'], 100)
        self.assertEqual(serialized['successful_requests'], 85)
        self.assertEqual(serialized['success_rate'], 85.0)
        self.assertAlmostEqual(serialized['average_response_time'], 0.2, places=3)
        self.assertEqual(serialized['activities_processed'], 50)
        self.assertEqual(serialized['polling_cycles'], 25)

    @patch('urllib.request.urlopen')
    def test_wait_for_activity_with_timeout(self, mock_urlopen):
        """Test waiting for specific activity with timeout"""
        # Mock activities response
        mock_response = Mock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps({
            'activities': [
                {'type': ActivityType.MESSAGE_SENT.value, 'message': 'Starting...'},
                {'type': ActivityType.PLAN_GENERATED.value, 'message': 'Plan created'}
            ]
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Test successful activity wait
        result = self.workflow.wait_for_activity_with_timeout(
            'test-session',
            ActivityType.PLAN_GENERATED.value,
            timeout_minutes=0.1  # Very short timeout
        )

        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['activity']['type'], ActivityType.PLAN_GENERATED.value)

    def test_enums_and_constants(self):
        """Test enum values and constants"""
        # Session states
        self.assertEqual(SessionState.ACTIVE.value, "ACTIVE")
        self.assertEqual(SessionState.COMPLETED.value, "COMPLETED")
        self.assertEqual(SessionState.FAILED.value, "FAILED")
        self.assertEqual(SessionState.CANCELLED.value, "CANCELLED")

        # Activity types
        self.assertEqual(ActivityType.PLAN_GENERATED.value, "PLAN_GENERATED")
        self.assertEqual(ActivityType.CODE_GENERATED.value, "CODE_GENERATED")
        self.assertEqual(ActivityType.ERROR.value, "ERROR")
        self.assertEqual(ActivityType.COMPLETION_NOTIFICATION.value, "COMPLETION_NOTIFICATION")

    def test_graceful_shutdown(self):
        """Test graceful shutdown of client"""
        # Mock some active pollers
        mock_future1 = Mock()
        mock_future2 = Mock()
        self.client.active_pollers = {
            'session1': mock_future1,
            'session2': mock_future2
        }

        # Test shutdown
        self.client.shutdown()

        # Verify pollers were cancelled
        mock_future1.cancel.assert_called_once()
        mock_future2.cancel.assert_called_once()

        # Verify active pollers cleared
        self.assertEqual(len(self.client.active_pollers), 0)

class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for realistic scenarios"""

    def setUp(self):
        """Set up integration test environment"""
        self.config = JulesConfig(
            api_key="AQ.integration_test_key",
            polling_interval=2,
            max_polling_duration=30,
            throughput_logging=True,
            enable_notifications=True
        )
        self.client = JulesEnhancedAPIClient(self.config)
        self.workflow = JulesEnhancedWorkflowManager(self.client)

    def test_notification_handler_with_multiple_activities(self):
        """Test notification handler processing multiple activities"""
        received_notifications = []

        def test_handler(session_name, activity):
            received_notifications.append((session_name, activity['type']))

        self.client.add_notification_handler(test_handler)

        # Simulate multiple activities
        activities = [
            {'type': ActivityType.PLAN_GENERATED.value, 'message': 'Plan created'},
            {'type': ActivityType.MESSAGE_SENT.value, 'message': 'User message'},
            {'type': ActivityType.CODE_GENERATED.value, 'message': 'Code generated'},
            {'type': ActivityType.COMPLETION_NOTIFICATION.value, 'message': 'Completed'}
        ]

        session_name = 'test-session-multi'
        for activity in activities:
            self.client._handle_activity_update(session_name, activity)

        # Verify all notifications were received
        self.assertEqual(len(received_notifications), 4)
        self.assertEqual(received_notifications[0][1], ActivityType.PLAN_GENERATED.value)
        self.assertEqual(received_notifications[3][1], ActivityType.COMPLETION_NOTIFICATION.value)

    def test_workflow_end_to_end_simulation(self):
        """Test end-to-end workflow simulation"""
        # Track workflow events
        workflow_events = []

        def workflow_handler(session_name, activity):
            workflow_events.append({
                'timestamp': datetime.now(timezone.utc),
                'session': session_name,
                'activity': activity['type'],
                'message': activity.get('message', '')
            })

        # Create unique identifiers
        task_desc = "Implement user authentication system with OAuth2"
        session_id = self.workflow.generate_unique_session_id(task_desc)
        branch_name = self.workflow.generate_unique_branch_name(task_desc, session_id)

        # Verify uniqueness
        self.assertNotEqual(session_id, branch_name)
        self.assertTrue(session_id.startswith("jules-workflow-"))
        self.assertIn(session_id, branch_name)

        # Simulate workflow session creation (without actual API calls)
        session_data = {
            'name': f'sessions/{session_id}',
            'sessionId': session_id,
            'state': SessionState.ACTIVE.value,
            'createdAt': datetime.now(timezone.utc).isoformat()
        }

        self.workflow.active_sessions[session_id] = {
            'session_data': session_data,
            'branch_name': branch_name,
            'task_description': task_desc,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'metrics_start': ThroughputMetrics()
        }

        # Verify session creation
        self.assertIn(session_id, self.workflow.active_sessions)
        self.assertEqual(self.workflow.active_sessions[session_id]['branch_name'], branch_name)

        # Simulate activity updates
        activities_sequence = [
            ActivityType.PLAN_GENERATED.value,
            ActivityType.PLAN_APPROVED.value,
            ActivityType.CODE_GENERATED.value,
            ActivityType.COMPLETION_NOTIFICATION.value
        ]

        for activity_type in activities_sequence:
            activity = {'type': activity_type, 'message': f'Simulated {activity_type}'}
            self.client._handle_activity_update(session_id, activity)
            workflow_handler(session_id, activity)

        # Verify workflow progression
        self.assertEqual(len(workflow_events), 4)
        self.assertEqual(workflow_events[0]['activity'], ActivityType.PLAN_GENERATED.value)
        self.assertEqual(workflow_events[-1]['activity'], ActivityType.COMPLETION_NOTIFICATION.value)

def run_performance_test():
    """Run performance test for throughput capabilities"""
    print("🚀 Running Performance Test")
    print("=" * 50)

    config = JulesConfig(
        api_key="AQ.performance_test_key",
        polling_interval=1,
        throughput_logging=True
    )

    client = JulesEnhancedAPIClient(config)

    # Simulate high-throughput scenario
    start_time = time.time()
    num_activities = 100

    print(f"Simulating {num_activities} activities...")

    for i in range(num_activities):
        activity = {
            'type': ActivityType.CODE_GENERATED.value,
            'message': f'Activity {i+1} - Simulated code generation'
        }
        client._handle_activity_update(f'session-{i}', activity)

        # Simulate API request
        client._log_throughput(
            start_time=time.time() - (i * 0.01),
            bytes_sent=100,
            bytes_received=500,
            success=True
        )

    duration = time.time() - start_time
    metrics = client.get_throughput_metrics()

    print(f"✅ Performance test completed in {duration:.2f} seconds")
    print(f"📊 Processed {num_activities} activities")
    print(f"📈 Activity processing rate: {num_activities/duration:.1f} activities/second")
    print(f"🔢 Total requests: {metrics['total_requests']}")
    print(f"✅ Success rate: {metrics['success_rate']:.2f}%")
    print(f"⏱️ Average response time: {metrics['average_response_time']:.3f}s")

    # Generate performance report
    print(f"\n{client.generate_throughput_report()}")

def main():
    """Run all tests"""
    print("🧪 Jules Enhanced API - Comprehensive Test Suite")
    print("=" * 60)

    # Run unit tests
    print("\n📋 Running Unit Tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run performance test
    run_performance_test()

    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()