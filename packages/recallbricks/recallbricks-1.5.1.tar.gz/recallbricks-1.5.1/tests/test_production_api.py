"""
Production API Integration Tests for RecallBricks Python SDK
Tests SDK compatibility with the production API at https://api.recallbricks.com/api/v1

These tests verify:
1. Endpoint availability and correct URL structure
2. Error response parsing matches production format
3. Authentication header handling
4. Request/response schema compatibility
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recallbricks import RecallBricks
from recallbricks.exceptions import (
    AuthenticationError,
    RateLimitError,
    APIError,
    RecallBricksError,
    ValidationError,
    NotFoundError
)


class TestProductionAPIErrorFormat(unittest.TestCase):
    """Test that SDK correctly parses production API error format"""

    def setUp(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_test_key")

    def test_parse_production_auth_error(self):
        """Test parsing production authentication error response"""
        with patch.object(self.client, 'session') as mock_session:
            # Exact production error format
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.content = json.dumps({
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "The API key provided is invalid or does not exist",
                    "hint": "Check that your key starts with 'rb_live_' and is active in the dashboard",
                    "requestId": "8e233368-b6b1-4475-9f58-b280a9e2d4a3",
                    "timestamp": "2025-12-13T20:26:39.841Z"
                }
            }).encode()
            mock_response.json.return_value = {
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "The API key provided is invalid or does not exist",
                    "hint": "Check that your key starts with 'rb_live_' and is active in the dashboard",
                    "requestId": "8e233368-b6b1-4475-9f58-b280a9e2d4a3",
                    "timestamp": "2025-12-13T20:26:39.841Z"
                }
            }
            mock_session.request.return_value = mock_response

            with self.assertRaises(AuthenticationError) as ctx:
                self.client.learn("test")

            error = ctx.exception
            self.assertEqual(error.code, "INVALID_API_KEY")
            self.assertIn("invalid", error.message.lower())
            self.assertIn("rb_live_", error.hint)
            self.assertEqual(error.request_id, "8e233368-b6b1-4475-9f58-b280a9e2d4a3")

    def test_parse_production_rate_limit_error(self):
        """Test parsing production rate limit error response"""
        with patch.object(self.client, 'session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.headers = {'X-RateLimit-Reset': '60'}
            mock_response.content = json.dumps({
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down.",
                    "hint": "Wait 60 seconds before retrying",
                    "requestId": "rate-limit-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }).encode()
            mock_response.json.return_value = {
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please slow down.",
                    "hint": "Wait 60 seconds before retrying",
                    "requestId": "rate-limit-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }
            mock_session.request.return_value = mock_response

            with self.assertRaises(RateLimitError) as ctx:
                self.client.learn("test")

            error = ctx.exception
            self.assertEqual(error.code, "RATE_LIMIT_EXCEEDED")
            self.assertEqual(error.retry_after, '60')

    def test_parse_production_not_found_error(self):
        """Test parsing production 404 error response"""
        with patch.object(self.client, 'session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.content = json.dumps({
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Memory not found",
                    "requestId": "not-found-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }).encode()
            mock_response.json.return_value = {
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Memory not found",
                    "requestId": "not-found-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }
            mock_session.request.return_value = mock_response

            with self.assertRaises(NotFoundError) as ctx:
                self.client.get("non-existent-id")

            error = ctx.exception
            self.assertEqual(error.status_code, 404)

    def test_parse_production_validation_error(self):
        """Test parsing production validation error response"""
        with patch.object(self.client, 'session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.content = json.dumps({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Text field is required",
                    "requestId": "validation-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }).encode()
            mock_response.json.return_value = {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Text field is required",
                    "requestId": "validation-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }
            mock_session.request.return_value = mock_response

            with self.assertRaises(ValidationError) as ctx:
                self.client._request("POST", "/memories", json={})

            error = ctx.exception
            self.assertEqual(error.code, "VALIDATION_ERROR")

    def test_parse_production_server_error(self):
        """Test parsing production 500 error response"""
        with patch.object(self.client, 'session') as mock_session:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.content = json.dumps({
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "hint": "Please try again later or contact support",
                    "requestId": "server-error-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }).encode()
            mock_response.json.return_value = {
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "hint": "Please try again later or contact support",
                    "requestId": "server-error-123",
                    "timestamp": "2025-12-13T20:30:00.000Z"
                }
            }
            mock_session.request.return_value = mock_response

            with patch('time.sleep'):  # Skip retry delays
                with self.assertRaises(APIError) as ctx:
                    self.client.learn("test")

            error = ctx.exception
            self.assertEqual(error.status_code, 500)
            self.assertEqual(error.code, "INTERNAL_SERVER_ERROR")


class TestProductionAPIEndpoints(unittest.TestCase):
    """Test that SDK calls correct production API endpoints"""

    def setUp(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_test_key")

    def test_learn_endpoint(self):
        """Test learn() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'uuid',
                'text': 'test',
                'metadata': {},
                'created_at': ''
            }
            self.client.learn("Test memory")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "POST")
            self.assertEqual(args[0][1], "/memories/learn")

    def test_recall_endpoint(self):
        """Test recall() calls correct endpoint with POST"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}
            self.client.recall("test query")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "POST")
            self.assertEqual(args[0][1], "/memories/recall")

    def test_save_endpoint(self):
        """Test save() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'uuid', 'text': 'test'}
            self.client.save("Test memory")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "POST")
            self.assertEqual(args[0][1], "/memories")

    def test_search_endpoint(self):
        """Test search() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}
            self.client.search("test query")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "POST")
            self.assertEqual(args[0][1], "/memories/search")

    def test_get_all_endpoint(self):
        """Test get_all() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}
            self.client.get_all()

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "GET")
            self.assertEqual(args[0][1], "/memories")

    def test_get_endpoint(self):
        """Test get() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'test-id', 'text': 'test'}
            self.client.get("test-id")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "GET")
            self.assertEqual(args[0][1], "/memories/test-id")

    def test_delete_endpoint(self):
        """Test delete() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'success': True}
            self.client.delete("test-id")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "DELETE")
            self.assertEqual(args[0][1], "/memories/test-id")

    def test_update_endpoint(self):
        """Test update() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'test-id', 'text': 'updated'}
            self.client.update("test-id", text="updated")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "PUT")
            self.assertEqual(args[0][1], "/memories/test-id")

    def test_health_endpoint(self):
        """Test health() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'status': 'healthy'}
            self.client.health()

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "GET")
            self.assertEqual(args[0][1], "/health")

    def test_rate_limit_endpoint(self):
        """Test get_rate_limit() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'limit': 100, 'remaining': 99}
            self.client.get_rate_limit()

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "GET")
            self.assertEqual(args[0][1], "/rate-limit")

    def test_relationships_endpoint(self):
        """Test get_relationships() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'relationships': [], 'count': 0}
            self.client.get_relationships("test-id")

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "GET")
            self.assertEqual(args[0][1], "/relationships/memory/test-id")

    def test_graph_context_endpoint(self):
        """Test get_graph_context() calls correct endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'nodes': [], 'edges': []}
            self.client.get_graph_context("test-id", depth=3)

            mock_request.assert_called_once()
            args = mock_request.call_args
            self.assertEqual(args[0][0], "GET")
            self.assertEqual(args[0][1], "/relationships/graph/test-id")


class TestProductionAPIHeaders(unittest.TestCase):
    """Test that SDK sends correct headers to production API"""

    def test_api_key_header(self):
        """Test API key authentication header"""
        client = RecallBricks(api_key="rb_live_test123")
        self.assertEqual(client.session.headers['X-API-Key'], 'rb_live_test123')
        self.assertEqual(client.session.headers['Content-Type'], 'application/json')
        self.assertNotIn('X-Service-Token', client.session.headers)

    def test_service_token_header(self):
        """Test service token authentication header"""
        client = RecallBricks(service_token="rbk_service_test123")
        self.assertEqual(client.session.headers['X-Service-Token'], 'rbk_service_test123')
        self.assertEqual(client.session.headers['Content-Type'], 'application/json')
        self.assertNotIn('X-API-Key', client.session.headers)


class TestProductionAPIBaseURL(unittest.TestCase):
    """Test production API base URL configuration"""

    def test_default_base_url(self):
        """Test default production base URL"""
        client = RecallBricks(api_key="test")
        self.assertEqual(client.base_url, "https://api.recallbricks.com/api/v1")

    def test_custom_base_url(self):
        """Test custom base URL override"""
        client = RecallBricks(api_key="test", base_url="https://custom.api.com/v2")
        self.assertEqual(client.base_url, "https://custom.api.com/v2")

    def test_base_url_trailing_slash_removed(self):
        """Test trailing slash is removed from base URL"""
        client = RecallBricks(api_key="test", base_url="https://api.example.com/")
        self.assertEqual(client.base_url, "https://api.example.com")


class TestProductionAPIRequestPayloads(unittest.TestCase):
    """Test that SDK sends correct request payloads to production API"""

    def setUp(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_test_key")

    def test_learn_request_payload(self):
        """Test learn() sends correct payload"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'uuid', 'text': 'test', 'metadata': {}, 'created_at': ''}

            self.client.learn(
                "Test memory content",
                project_id="my-project",
                source="custom-source",
                metadata={"tags": ["custom"]}
            )

            call_args = mock_request.call_args
            payload = call_args[1]['json']

            self.assertEqual(payload['text'], "Test memory content")
            self.assertEqual(payload['project_id'], "my-project")
            self.assertEqual(payload['source'], "custom-source")
            self.assertEqual(payload['metadata'], {"tags": ["custom"]})

    def test_recall_request_payload(self):
        """Test recall() sends correct JSON payload"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}

            self.client.recall(
                "search query",
                limit=20,
                min_helpfulness_score=0.8,
                organized=True,
                project_id="my-project"
            )

            call_args = mock_request.call_args
            payload = call_args[1]['json']

            self.assertEqual(payload['query'], "search query")
            self.assertEqual(payload['limit'], 20)
            self.assertEqual(payload['min_helpfulness_score'], 0.8)
            self.assertEqual(payload['organized'], True)
            self.assertEqual(payload['project_id'], "my-project")

    def test_save_request_payload(self):
        """Test save() sends correct payload"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'uuid', 'text': 'test'}

            self.client.save(
                "Test memory",
                source="api",
                project_id="default",
                tags=["tag1", "tag2"],
                metadata={"key": "value"}
            )

            call_args = mock_request.call_args
            payload = call_args[1]['json']

            self.assertEqual(payload['text'], "Test memory")
            self.assertEqual(payload['source'], "api")
            self.assertEqual(payload['project_id'], "default")
            self.assertEqual(payload['tags'], ["tag1", "tag2"])
            self.assertEqual(payload['metadata'], {"key": "value"})


class TestProductionAPIResponseParsing(unittest.TestCase):
    """Test that SDK correctly parses production API responses"""

    def setUp(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_test_key")

    def test_parse_learn_response(self):
        """Test parsing learn() response with auto-generated metadata"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'uuid-123',
                'text': 'Test memory',
                'metadata': {
                    'tags': ['auto', 'generated'],
                    'category': 'Work',
                    'entities': ['Test'],
                    'importance': 0.85,
                    'summary': 'Auto-generated summary'
                },
                'created_at': '2025-01-01T00:00:00Z',
                'source': 'python-sdk',
                'project_id': 'default'
            }

            result = self.client.learn("Test memory")

            self.assertEqual(result['id'], 'uuid-123')
            self.assertEqual(result['metadata']['category'], 'Work')
            self.assertIn('tags', result['metadata'])
            self.assertIn('importance', result['metadata'])

    def test_parse_recall_organized_response(self):
        """Test parsing organized recall() response"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'memories': [
                    {
                        'id': 'mem-1',
                        'text': 'Work memory',
                        'metadata': {'category': 'Work'},
                        'score': 0.95
                    }
                ],
                'categories': {
                    'Work': {
                        'count': 5,
                        'avg_score': 0.85,
                        'summary': 'Work-related memories'
                    }
                },
                'total': 5
            }

            result = self.client.recall("test", organized=True)

            self.assertIn('memories', result)
            self.assertIn('categories', result)
            self.assertIn('Work', result['categories'])
            self.assertEqual(result['categories']['Work']['count'], 5)

    def test_parse_health_response(self):
        """Test parsing health() response"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'status': 'healthy',
                'version': '1.0.0',
                'timestamp': '2025-12-13T20:26:25.732Z'
            }

            result = self.client.health()

            self.assertEqual(result['status'], 'healthy')
            self.assertIn('version', result)


class TestExceptionStringRepresentation(unittest.TestCase):
    """Test exception string representations for debugging"""

    def test_auth_error_str(self):
        """Test AuthenticationError string representation"""
        error = AuthenticationError(
            message="Invalid API key",
            code="INVALID_API_KEY",
            hint="Check your key format",
            request_id="req-123"
        )
        error_str = str(error)
        self.assertIn("Invalid API key", error_str)
        self.assertIn("Check your key format", error_str)
        self.assertIn("req-123", error_str)

    def test_api_error_str(self):
        """Test APIError string representation"""
        error = APIError(
            message="Server error",
            status_code=500,
            code="SERVER_ERROR",
            request_id="req-456"
        )
        error_str = str(error)
        self.assertIn("Server error", error_str)
        self.assertIn("req-456", error_str)

    def test_error_without_optional_fields(self):
        """Test error string with only message"""
        error = RecallBricksError(message="Simple error")
        error_str = str(error)
        self.assertEqual(error_str, "Simple error")


def run_production_api_tests():
    """Run all production API tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestProductionAPIErrorFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionAPIEndpoints))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionAPIHeaders))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionAPIBaseURL))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionAPIRequestPayloads))
    suite.addTests(loader.loadTestsFromTestCase(TestProductionAPIResponseParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptionStringRepresentation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("PRODUCTION API COMPATIBILITY TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_production_api_tests()
    sys.exit(0 if success else 1)
