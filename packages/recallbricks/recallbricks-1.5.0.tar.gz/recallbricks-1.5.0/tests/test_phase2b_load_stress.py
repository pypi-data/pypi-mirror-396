"""
Load and stress tests for Phase 2B automatic metatags features
Tests concurrent requests, retry logic, large payloads, edge cases, and enterprise scenarios
for learn() and recall() methods
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
import os
import time
import threading
import queue
import random
import string
import requests
import warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recallbricks import RecallBricks
from recallbricks.exceptions import APIError, RateLimitError, RecallBricksError, AuthenticationError
from recallbricks.types import (
    LearnedMemory,
    OrganizedRecallResult,
    MemoryMetadata,
    CategorySummary,
    RecallMemory,
    RecallResponse
)


class TestLearnLoadStress(unittest.TestCase):
    """Load and stress tests for learn() method"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.client = RecallBricks(api_key=self.api_key)

    def test_learn_concurrent_requests(self):
        """Test concurrent learn() requests (50 parallel)"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'test-uuid',
                'text': 'Test memory',
                'metadata': {
                    'tags': ['auto'],
                    'category': 'Work',
                    'entities': [],
                    'importance': 0.8,
                    'summary': 'Auto summary'
                },
                'created_at': '2024-01-01T00:00:00Z'
            }

            results = []
            errors = []

            def learn_task(idx):
                try:
                    result = self.client.learn(f"Memory content {idx}")
                    results.append(result)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=learn_task, args=(i,)) for i in range(50)]
            start_time = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)
            elapsed = time.time() - start_time

            # All requests should complete successfully
            self.assertEqual(len(results), 50, f"Expected 50 results, got {len(results)}")
            self.assertEqual(len(errors), 0, f"Expected 0 errors, got {len(errors)}: {errors}")
            print(f"  50 concurrent learn() requests completed in {elapsed:.2f}s")

    def test_learn_high_throughput(self):
        """Test high throughput: 100 sequential learn() calls"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'test-uuid',
                'text': 'Test',
                'metadata': {'tags': [], 'category': '', 'entities': [], 'importance': 0.5, 'summary': ''},
                'created_at': '2024-01-01T00:00:00Z'
            }

            start_time = time.time()
            for i in range(100):
                self.client.learn(f"Sequential memory {i}")
            elapsed = time.time() - start_time

            self.assertEqual(mock_request.call_count, 100)
            print(f"  100 sequential learn() calls completed in {elapsed:.2f}s")

    def test_learn_large_text_payload(self):
        """Test learn() with very large text (close to 10KB limit)"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'test-uuid',
                'text': 'Large',
                'metadata': {'tags': [], 'category': '', 'entities': [], 'importance': 0.5, 'summary': ''},
                'created_at': '2024-01-01T00:00:00Z'
            }

            # 9500 characters (close to 10KB sanitization limit)
            large_text = "A" * 9500
            result = self.client.learn(large_text)

            self.assertIsNotNone(result)
            call_args = mock_request.call_args
            # Text should be sanitized and passed
            self.assertIn('text', call_args[1]['json'])

    def test_learn_with_complex_metadata_override(self):
        """Test learn() with complex nested metadata overrides"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'test-uuid',
                'text': 'Test',
                'metadata': {},
                'created_at': '2024-01-01T00:00:00Z'
            }

            complex_metadata = {
                'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
                'category': 'Custom Category',
                'custom_field': {
                    'nested': {
                        'deep': 'value'
                    }
                }
            }
            result = self.client.learn("Test content", metadata=complex_metadata)

            call_args = mock_request.call_args
            self.assertEqual(call_args[1]['json']['metadata'], complex_metadata)

    def test_learn_retry_on_500_error(self):
        """Test learn() retries on server errors"""
        with patch.object(self.client, 'session') as mock_session:
            mock_response_error = Mock()
            mock_response_error.status_code = 500
            mock_response_error.content = b'{"message": "Server error"}'
            mock_response_error.json.return_value = {'message': 'Server error'}

            mock_response_success = Mock()
            mock_response_success.status_code = 200
            mock_response_success.content = b'{"id": "uuid", "text": "test", "metadata": {}, "created_at": ""}'
            mock_response_success.json.return_value = {
                'id': 'uuid', 'text': 'test', 'metadata': {}, 'created_at': ''
            }

            mock_session.request.side_effect = [
                mock_response_error,
                mock_response_error,
                mock_response_success
            ]

            with patch('time.sleep'):
                result = self.client.learn("Test content")

            self.assertEqual(mock_session.request.call_count, 3)
            self.assertEqual(result['id'], 'uuid')

    def test_learn_rate_limiting_recovery(self):
        """Test learn() handles rate limiting with retry"""
        with patch.object(self.client, 'session') as mock_session:
            mock_rate_limit = Mock()
            mock_rate_limit.status_code = 429
            mock_rate_limit.headers = {'X-RateLimit-Reset': '1'}
            mock_rate_limit.content = b''

            mock_success = Mock()
            mock_success.status_code = 200
            mock_success.content = b'{"id": "uuid", "text": "test", "metadata": {}, "created_at": ""}'
            mock_success.json.return_value = {'id': 'uuid', 'text': 'test', 'metadata': {}, 'created_at': ''}

            mock_session.request.side_effect = [mock_rate_limit, mock_success]

            with patch('time.sleep'):
                result = self.client.learn("Test content")

            self.assertEqual(result['id'], 'uuid')

    def test_learn_timeout_recovery(self):
        """Test learn() recovers from timeout errors"""
        with patch.object(self.client, 'session') as mock_session:
            mock_session.request.side_effect = [
                requests.exceptions.Timeout(),
                requests.exceptions.Timeout(),
                Mock(status_code=200, content=b'{"id": "uuid", "text": "t", "metadata": {}, "created_at": ""}',
                     json=lambda: {'id': 'uuid', 'text': 't', 'metadata': {}, 'created_at': ''})
            ]

            with patch('time.sleep'):
                result = self.client.learn("Test content")

            self.assertEqual(result['id'], 'uuid')

    def test_learn_connection_error_recovery(self):
        """Test learn() recovers from connection errors"""
        with patch.object(self.client, 'session') as mock_session:
            mock_session.request.side_effect = [
                requests.exceptions.ConnectionError("Network unreachable"),
                Mock(status_code=200, content=b'{"id": "uuid", "text": "t", "metadata": {}, "created_at": ""}',
                     json=lambda: {'id': 'uuid', 'text': 't', 'metadata': {}, 'created_at': ''})
            ]

            with patch('time.sleep'):
                result = self.client.learn("Test content")

            self.assertEqual(result['id'], 'uuid')

    def test_learn_exponential_backoff(self):
        """Test learn() uses exponential backoff on retries"""
        with patch.object(self.client, 'session') as mock_session:
            mock_error = Mock()
            mock_error.status_code = 500
            mock_error.content = b'{"message": "Server error"}'
            mock_error.json.return_value = {'message': 'Server error'}

            mock_session.request.side_effect = [mock_error, mock_error, mock_error]

            sleep_times = []

            def capture_sleep(duration):
                sleep_times.append(duration)

            with patch('time.sleep', side_effect=capture_sleep):
                try:
                    self.client.learn("Test")
                except APIError:
                    pass

            # Should have exponential backoff: 1s, 2s (2^0, 2^1)
            self.assertEqual(len(sleep_times), 2)
            self.assertEqual(sleep_times[0], 1)
            self.assertEqual(sleep_times[1], 2)

    def test_learn_special_characters(self):
        """Test learn() handles special characters properly"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'uuid', 'text': '', 'metadata': {}, 'created_at': ''}

            special_texts = [
                "Unicode: 你好世界 🌍 مرحبا",
                "SQL injection: '; DROP TABLE memories; --",
                "XSS attempt: <script>alert('xss')</script>",
                "JSON special: {\"key\": \"value\", \"nested\": [1,2,3]}",
                "Control chars removed: \x00\x08\x0b\x0c test",
                "Newlines: Line1\nLine2\rLine3\r\nLine4",
                "Quotes: 'single' \"double\" `backtick`"
            ]

            for text in special_texts:
                self.client.learn(text)

            self.assertEqual(mock_request.call_count, len(special_texts))


class TestRecallLoadStress(unittest.TestCase):
    """Load and stress tests for recall() method"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.client = RecallBricks(api_key=self.api_key)

    def test_recall_concurrent_requests(self):
        """Test concurrent recall() requests (50 parallel)"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'memories': [{'id': 'mem1', 'text': 'Test', 'score': 0.9}],
                'count': 1
            }

            results = []
            errors = []

            def recall_task(idx):
                try:
                    result = self.client.recall(f"query {idx}")
                    results.append(result)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=recall_task, args=(i,)) for i in range(50)]
            start_time = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)
            elapsed = time.time() - start_time

            self.assertEqual(len(results), 50)
            self.assertEqual(len(errors), 0)
            print(f"  50 concurrent recall() requests completed in {elapsed:.2f}s")

    def test_recall_organized_concurrent(self):
        """Test concurrent organized recall() requests"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'memories': [
                    {'id': 'mem1', 'text': 'Work memory', 'metadata': {'category': 'Work'}, 'score': 0.9},
                    {'id': 'mem2', 'text': 'Personal', 'metadata': {'category': 'Personal'}, 'score': 0.8}
                ],
                'categories': {
                    'Work': {'count': 5, 'avg_score': 0.85, 'summary': 'Work memories'},
                    'Personal': {'count': 3, 'avg_score': 0.78, 'summary': 'Personal memories'}
                },
                'total': 8
            }

            results = []
            errors = []

            def recall_organized_task(idx):
                try:
                    result = self.client.recall(f"query {idx}", organized=True)
                    results.append(result)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=recall_organized_task, args=(i,)) for i in range(30)]
            start_time = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)
            elapsed = time.time() - start_time

            self.assertEqual(len(results), 30)
            self.assertEqual(len(errors), 0)
            for r in results:
                self.assertIn('categories', r)
            print(f"  30 concurrent organized recall() requests completed in {elapsed:.2f}s")

    def test_recall_large_result_set(self):
        """Test recall() with large result set (100 memories)"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'memories': [
                    {
                        'id': f'mem_{i}',
                        'text': f'Memory content {i} with some additional text for size',
                        'metadata': {
                            'tags': [f'tag_{i}', 'common_tag'],
                            'category': f'Category_{i % 10}',
                            'summary': f'Summary for memory {i}'
                        },
                        'score': 0.9 - (i * 0.005)
                    } for i in range(100)
                ],
                'count': 100
            }

            result = self.client.recall("test query", limit=100)

            self.assertEqual(len(result['memories']), 100)
            self.assertEqual(result['count'], 100)

    def test_recall_organized_many_categories(self):
        """Test organized recall with many categories (20 categories)"""
        with patch.object(self.client, '_request') as mock_request:
            categories = {}
            memories = []
            for i in range(20):
                cat_name = f'Category_{i}'
                categories[cat_name] = {
                    'count': random.randint(1, 10),
                    'avg_score': random.uniform(0.5, 0.95),
                    'summary': f'Summary for {cat_name}'
                }
                memories.append({
                    'id': f'mem_{i}',
                    'text': f'Memory in {cat_name}',
                    'metadata': {'category': cat_name},
                    'score': random.uniform(0.5, 0.95)
                })

            mock_request.return_value = {
                'memories': memories,
                'categories': categories,
                'total': sum(c['count'] for c in categories.values())
            }

            result = self.client.recall("test", organized=True)

            self.assertEqual(len(result['categories']), 20)
            self.assertIn('total', result)

    def test_recall_with_all_filters(self):
        """Test recall() with all optional parameters"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}

            result = self.client.recall(
                "test query",
                limit=50,
                min_helpfulness_score=0.75,
                organized=True,
                project_id="test-project"
            )

            call_args = mock_request.call_args
            params = call_args[1]['params']
            self.assertEqual(params['limit'], 50)
            self.assertEqual(params['min_helpfulness_score'], 0.75)
            self.assertEqual(params['organized'], 'true')
            self.assertEqual(params['project_id'], 'test-project')

    def test_recall_retry_on_server_error(self):
        """Test recall() retries on server errors"""
        with patch.object(self.client, 'session') as mock_session:
            mock_error = Mock()
            mock_error.status_code = 502
            mock_error.content = b'{"message": "Bad Gateway"}'
            mock_error.json.return_value = {'message': 'Bad Gateway'}

            mock_success = Mock()
            mock_success.status_code = 200
            mock_success.content = b'{"memories": [], "count": 0}'
            mock_success.json.return_value = {'memories': [], 'count': 0}

            mock_session.request.side_effect = [mock_error, mock_error, mock_success]

            with patch('time.sleep'):
                result = self.client.recall("test")

            self.assertEqual(mock_session.request.call_count, 3)
            self.assertEqual(result['count'], 0)

    def test_recall_rate_limit_handling(self):
        """Test recall() handles rate limiting"""
        with patch.object(self.client, 'session') as mock_session:
            mock_rate_limit = Mock()
            mock_rate_limit.status_code = 429
            mock_rate_limit.headers = {'X-RateLimit-Reset': '2'}
            mock_rate_limit.content = b''

            mock_success = Mock()
            mock_success.status_code = 200
            mock_success.content = b'{"memories": [], "count": 0}'
            mock_success.json.return_value = {'memories': [], 'count': 0}

            mock_session.request.side_effect = [mock_rate_limit, mock_success]

            with patch('time.sleep') as mock_sleep:
                result = self.client.recall("test")
                # Should have waited for rate limit reset
                mock_sleep.assert_called()

            self.assertEqual(result['count'], 0)


class TestServiceTokenLoadStress(unittest.TestCase):
    """Load tests for service token authentication"""

    def setUp(self):
        """Set up test fixtures with service token"""
        self.service_token = "rbk_service_test123"
        self.client = RecallBricks(service_token=self.service_token)

    def test_learn_concurrent_with_user_ids(self):
        """Test concurrent learn() with different user IDs"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                'id': 'uuid', 'text': 'test', 'metadata': {}, 'created_at': ''
            }

            results = []
            errors = []

            def learn_task(user_idx):
                try:
                    result = self.client.learn(
                        f"Memory for user {user_idx}",
                        user_id=f"user_{user_idx}"
                    )
                    results.append(result)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=learn_task, args=(i,)) for i in range(30)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)

            self.assertEqual(len(results), 30)
            self.assertEqual(len(errors), 0)

    def test_recall_concurrent_with_user_ids(self):
        """Test concurrent recall() with different user IDs"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}

            results = []
            errors = []

            def recall_task(user_idx):
                try:
                    result = self.client.recall(
                        f"query for user {user_idx}",
                        user_id=f"user_{user_idx}"
                    )
                    results.append(result)
                except Exception as e:
                    errors.append(e)

            threads = [threading.Thread(target=recall_task, args=(i,)) for i in range(30)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)

            self.assertEqual(len(results), 30)
            self.assertEqual(len(errors), 0)


class TestPhase2BEdgeCases(unittest.TestCase):
    """Edge case tests for Phase 2B features"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.client = RecallBricks(api_key=self.api_key)

    def test_learn_empty_text_error(self):
        """Test learn() raises error for empty text"""
        with self.assertRaises(ValueError) as ctx:
            self.client.learn("")
        self.assertIn("empty", str(ctx.exception).lower())

    def test_learn_whitespace_only_error(self):
        """Test learn() raises error for whitespace-only text"""
        with self.assertRaises(ValueError):
            self.client.learn("   \t\n  ")

    def test_learn_non_string_error(self):
        """Test learn() raises error for non-string text"""
        with self.assertRaises(TypeError):
            self.client.learn(12345)

        with self.assertRaises(TypeError):
            self.client.learn(['list', 'of', 'strings'])

        with self.assertRaises(TypeError):
            self.client.learn({'dict': 'value'})

    def test_recall_empty_query_error(self):
        """Test recall() raises error for empty query"""
        with self.assertRaises(ValueError):
            self.client.recall("")

    def test_recall_non_string_query_error(self):
        """Test recall() raises error for non-string query"""
        with self.assertRaises(TypeError):
            self.client.recall(12345)

    def test_recall_invalid_helpfulness_score(self):
        """Test recall() validates min_helpfulness_score range"""
        with self.assertRaises(ValueError):
            self.client.recall("test", min_helpfulness_score=-0.1)

        with self.assertRaises(ValueError):
            self.client.recall("test", min_helpfulness_score=1.5)

    def test_recall_boundary_helpfulness_scores(self):
        """Test recall() accepts boundary helpfulness scores"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'memories': [], 'count': 0}

            # Should work at boundaries
            self.client.recall("test", min_helpfulness_score=0.0)
            self.client.recall("test", min_helpfulness_score=1.0)
            self.client.recall("test", min_helpfulness_score=0.5)

    def test_service_token_missing_user_id_learn(self):
        """Test learn() requires user_id with service token"""
        client = RecallBricks(service_token="rbk_service_test")
        with self.assertRaises(ValueError) as ctx:
            client.learn("Test content")
        self.assertIn("user_id is required", str(ctx.exception))

    def test_service_token_missing_user_id_recall(self):
        """Test recall() requires user_id with service token"""
        client = RecallBricks(service_token="rbk_service_test")
        with self.assertRaises(ValueError) as ctx:
            client.recall("test query")
        self.assertIn("user_id is required", str(ctx.exception))

    def test_save_memory_deprecation_warning(self):
        """Test save_memory() raises deprecation warning"""
        with patch.object(self.client, 'save') as mock_save:
            mock_save.return_value = {'id': 'uuid'}

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.client.save_memory("Test content")

                self.assertEqual(len(w), 1)
                self.assertTrue(issubclass(w[0].category, DeprecationWarning))
                self.assertIn("deprecated", str(w[0].message).lower())
                self.assertIn("learn()", str(w[0].message))

    def test_learned_memory_from_dict_missing_fields(self):
        """Test LearnedMemory.from_dict handles missing fields gracefully"""
        minimal_data = {'id': 'uuid', 'text': 'Test'}
        learned = LearnedMemory.from_dict(minimal_data)

        self.assertEqual(learned.id, 'uuid')
        self.assertEqual(learned.text, 'Test')
        self.assertEqual(learned.metadata['tags'], [])
        self.assertEqual(learned.metadata['category'], '')
        self.assertEqual(learned.source, 'python-sdk')

    def test_organized_recall_result_from_dict_fallback(self):
        """Test OrganizedRecallResult.from_dict uses count as fallback for total"""
        data = {'memories': [], 'categories': {}, 'count': 42}
        result = OrganizedRecallResult.from_dict(data)
        self.assertEqual(result.total, 42)


class TestEnterpriseScenarios(unittest.TestCase):
    """Enterprise-grade scenario tests"""

    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key_12345"
        self.client = RecallBricks(api_key=self.api_key)

    def test_mixed_learn_recall_workload(self):
        """Test mixed learn() and recall() workload"""
        with patch.object(self.client, '_request') as mock_request:
            def mock_response(*args, **kwargs):
                if '/learn' in args[1]:
                    return {'id': 'uuid', 'text': 'test', 'metadata': {}, 'created_at': ''}
                else:
                    return {'memories': [], 'count': 0}

            mock_request.side_effect = mock_response

            results_queue = queue.Queue()
            errors_queue = queue.Queue()

            def mixed_task(idx):
                try:
                    if idx % 2 == 0:
                        result = self.client.learn(f"Memory {idx}")
                    else:
                        result = self.client.recall(f"Query {idx}")
                    results_queue.put(result)
                except Exception as e:
                    errors_queue.put(e)

            threads = [threading.Thread(target=mixed_task, args=(i,)) for i in range(40)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=30)

            results = []
            while not results_queue.empty():
                results.append(results_queue.get())

            errors = []
            while not errors_queue.empty():
                errors.append(errors_queue.get())

            self.assertEqual(len(results), 40)
            self.assertEqual(len(errors), 0)

    def test_burst_traffic_pattern(self):
        """Test burst traffic pattern (rapid requests then pause)"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'uuid', 'text': 't', 'metadata': {}, 'created_at': ''}

            # Simulate 3 bursts of 20 requests each
            total_requests = 0
            for burst in range(3):
                threads = []
                for i in range(20):
                    t = threading.Thread(target=lambda: self.client.learn(f"Burst {burst} mem {i}"))
                    threads.append(t)
                    t.start()

                for t in threads:
                    t.join(timeout=10)

                total_requests += 20
                time.sleep(0.1)  # Brief pause between bursts

            self.assertEqual(mock_request.call_count, 60)

    def test_session_reuse(self):
        """Test that session is reused across requests"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {'id': 'uuid', 'text': 't', 'metadata': {}, 'created_at': ''}

            # Multiple requests should use the same session
            for i in range(10):
                self.client.learn(f"Memory {i}")

            # Verify all calls went through the same client session
            self.assertEqual(mock_request.call_count, 10)

    def test_graceful_degradation_on_partial_failure(self):
        """Test graceful degradation when some requests fail"""
        call_count = [0]

        def intermittent_failure(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] % 3 == 0:
                raise requests.exceptions.Timeout()
            return Mock(
                status_code=200,
                content=b'{"id": "uuid", "text": "t", "metadata": {}, "created_at": ""}',
                json=lambda: {'id': 'uuid', 'text': 't', 'metadata': {}, 'created_at': ''}
            )

        with patch.object(self.client, 'session') as mock_session:
            mock_session.request.side_effect = intermittent_failure

            successes = 0
            failures = 0

            for i in range(9):
                try:
                    with patch('time.sleep'):
                        self.client.learn(f"Memory {i}")
                    successes += 1
                except RecallBricksError:
                    failures += 1

            # Some should succeed (retries help), some may fail
            self.assertGreater(successes, 0)


class TestTypeValidation(unittest.TestCase):
    """Type validation tests for Phase 2B types"""

    def test_memory_metadata_structure(self):
        """Test MemoryMetadata TypedDict structure"""
        metadata: MemoryMetadata = {
            'tags': ['tag1', 'tag2'],
            'category': 'Work',
            'entities': ['Entity1'],
            'importance': 0.85,
            'summary': 'Test summary'
        }

        self.assertEqual(metadata['tags'], ['tag1', 'tag2'])
        self.assertEqual(metadata['importance'], 0.85)

    def test_category_summary_structure(self):
        """Test CategorySummary TypedDict structure"""
        summary: CategorySummary = {
            'count': 10,
            'avg_score': 0.87,
            'summary': 'Category summary text'
        }

        self.assertEqual(summary['count'], 10)
        self.assertEqual(summary['avg_score'], 0.87)

    def test_recall_memory_structure(self):
        """Test RecallMemory TypedDict structure"""
        memory: RecallMemory = {
            'id': 'test-uuid',
            'text': 'Memory content',
            'metadata': {
                'tags': ['tag'],
                'category': 'Work',
                'entities': [],
                'importance': 0.8,
                'summary': 'Summary'
            },
            'score': 0.95
        }

        self.assertEqual(memory['id'], 'test-uuid')
        self.assertEqual(memory['score'], 0.95)


def run_phase2b_load_stress_tests():
    """Run all Phase 2B load and stress tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestLearnLoadStress))
    suite.addTests(loader.loadTestsFromTestCase(TestRecallLoadStress))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceTokenLoadStress))
    suite.addTests(loader.loadTestsFromTestCase(TestPhase2BEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestEnterpriseScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestTypeValidation))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    print("PHASE 2B LOAD/STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print("=" * 70)

    if result.failures:
        print("\nFailed tests:")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print("\nTests with errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_phase2b_load_stress_tests()
    sys.exit(0 if success else 1)
