"""
Test recall() functionality for RecallBricks Python SDK
Tests enhanced /api/v1/memories/recall endpoint with organized results
"""

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

from unittest.mock import Mock, patch
from recallbricks import RecallBricks
from recallbricks.types import (
    RecallResponse,
    CategorySummary,
    RecallMemory,
    OrganizedRecallResult
)


class TestRecallMethod:
    """Test the recall() method"""

    def setup_method(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_dev_test123")

    def test_recall_calls_correct_endpoint(self):
        """Test that recall() calls /api/v1/memories/recall endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "memories": [],
                "count": 0
            }

            self.client.recall("test query")

            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "GET"
            assert call_args[0][1] == "/memories/recall"

    def test_recall_basic_query(self):
        """Test basic recall query"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "memories": [
                    {"id": "mem1", "text": "Test memory", "score": 0.95}
                ],
                "count": 1
            }

            result = self.client.recall("test query")

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["query"] == "test query"
            assert params["limit"] == 10  # default
            assert "memories" in result
            assert result["count"] == 1

    def test_recall_with_limit(self):
        """Test recall with custom limit"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"memories": [], "count": 0}

            self.client.recall("query", limit=5)

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["limit"] == 5

    def test_recall_with_min_helpfulness_score(self):
        """Test recall with min_helpfulness_score filter"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"memories": [], "count": 0}

            self.client.recall("query", min_helpfulness_score=0.7)

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["min_helpfulness_score"] == 0.7

    def test_recall_organized_mode(self):
        """Test recall with organized=True returns category summaries"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "memories": [
                    {
                        "id": "mem1",
                        "text": "Work memory",
                        "metadata": {
                            "tags": ["work"],
                            "category": "Work",
                            "summary": "Work related"
                        },
                        "score": 0.92
                    },
                    {
                        "id": "mem2",
                        "text": "Personal memory",
                        "metadata": {
                            "tags": ["personal"],
                            "category": "Personal",
                            "summary": "Personal note"
                        },
                        "score": 0.78
                    }
                ],
                "categories": {
                    "Work": {
                        "count": 5,
                        "avg_score": 0.85,
                        "summary": "Work-related memories about Python development"
                    },
                    "Personal": {
                        "count": 2,
                        "avg_score": 0.78,
                        "summary": "Personal notes and preferences"
                    }
                },
                "total": 7
            }

            result = self.client.recall("test", organized=True)

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["organized"] == "true"

            assert "categories" in result
            assert "Work" in result["categories"]
            assert result["categories"]["Work"]["count"] == 5
            assert result["total"] == 7

    def test_recall_with_project_id(self):
        """Test recall with project_id filter"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"memories": [], "count": 0}

            self.client.recall("query", project_id="my-project")

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["project_id"] == "my-project"

    def test_recall_empty_query_raises_error(self):
        """Test that empty query raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.recall("")
            assert "query cannot be empty" in str(exc_info.value)
        else:
            try:
                self.client.recall("")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "query cannot be empty" in str(e)

    def test_recall_whitespace_query_raises_error(self):
        """Test that whitespace-only query raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.recall("   ")
            assert "query cannot be empty" in str(exc_info.value)
        else:
            try:
                self.client.recall("   ")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "query cannot be empty" in str(e)

    def test_recall_non_string_query_raises_error(self):
        """Test that non-string query raises TypeError"""
        if HAS_PYTEST:
            with pytest.raises(TypeError) as exc_info:
                self.client.recall(123)
            assert "query must be a string" in str(exc_info.value)
        else:
            try:
                self.client.recall(123)
                raise AssertionError("Expected TypeError")
            except TypeError as e:
                assert "query must be a string" in str(e)

    def test_recall_invalid_helpfulness_score_raises_error(self):
        """Test that invalid min_helpfulness_score raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.recall("query", min_helpfulness_score=1.5)
            assert "min_helpfulness_score must be between 0.0 and 1.0" in str(exc_info.value)
        else:
            try:
                self.client.recall("query", min_helpfulness_score=1.5)
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "min_helpfulness_score must be between 0.0 and 1.0" in str(e)

    def test_recall_negative_helpfulness_score_raises_error(self):
        """Test that negative min_helpfulness_score raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.recall("query", min_helpfulness_score=-0.5)
            assert "min_helpfulness_score must be between 0.0 and 1.0" in str(exc_info.value)
        else:
            try:
                self.client.recall("query", min_helpfulness_score=-0.5)
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "min_helpfulness_score must be between 0.0 and 1.0" in str(e)

    def test_recall_sanitizes_query(self):
        """Test that recall() sanitizes query input"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"memories": [], "count": 0}

            # Query with control characters
            self.client.recall("Test\x00query\x08here")

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            # Control characters should be removed
            assert "\x00" not in params["query"]
            assert "\x08" not in params["query"]


class TestRecallWithServiceToken:
    """Test recall() with service token authentication"""

    def setup_method(self):
        """Set up test client with service token"""
        self.client = RecallBricks(service_token="rbk_service_test123")

    def test_recall_requires_user_id_with_service_token(self):
        """Test that user_id is required when using service token"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.recall("test query")
            assert "user_id is required" in str(exc_info.value)
        else:
            try:
                self.client.recall("test query")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "user_id is required" in str(e)

    def test_recall_with_user_id_succeeds(self):
        """Test that recall() succeeds with user_id when using service token"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"memories": [], "count": 0}

            self.client.recall("test query", user_id="user_123")

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert params["user_id"] == "user_123"


class TestOrganizedRecallResultType:
    """Test OrganizedRecallResult dataclass"""

    def test_from_dict_full_response(self):
        """Test OrganizedRecallResult.from_dict with full response"""
        data = {
            "memories": [
                {
                    "id": "mem1",
                    "text": "Test memory",
                    "metadata": {
                        "tags": ["tag1"],
                        "category": "Work",
                        "summary": "Test"
                    },
                    "score": 0.92
                }
            ],
            "categories": {
                "Work": {
                    "count": 5,
                    "avg_score": 0.85,
                    "summary": "Work memories"
                }
            },
            "total": 5
        }

        result = OrganizedRecallResult.from_dict(data)

        assert len(result.memories) == 1
        assert result.memories[0]["id"] == "mem1"
        assert "Work" in result.categories
        assert result.categories["Work"]["count"] == 5
        assert result.total == 5

    def test_from_dict_minimal_response(self):
        """Test OrganizedRecallResult.from_dict with minimal response"""
        data = {}

        result = OrganizedRecallResult.from_dict(data)

        assert result.memories == []
        assert result.categories == {}
        assert result.total == 0

    def test_from_dict_with_count_fallback(self):
        """Test OrganizedRecallResult.from_dict falls back to count field"""
        data = {
            "memories": [],
            "categories": {},
            "count": 10  # backward compatibility field
        }

        result = OrganizedRecallResult.from_dict(data)

        assert result.total == 10


class TestRecallBackwardCompatibility:
    """Test backward compatibility of recall() method"""

    def setup_method(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_dev_test123")

    def test_recall_without_organized_returns_basic_format(self):
        """Test that recall() without organized flag returns basic format"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "memories": [
                    {"id": "mem1", "text": "Test memory"}
                ],
                "count": 1
            }

            result = self.client.recall("query")

            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert "organized" not in params

            # Basic format should still work
            assert "memories" in result
            assert "count" in result

    def test_recall_handles_old_response_format(self):
        """Test that recall() handles old API response format"""
        with patch.object(self.client, '_request') as mock_request:
            # Old format without categories
            mock_request.return_value = {
                "memories": [{"id": "mem1", "text": "Test"}],
                "count": 1
            }

            result = self.client.recall("query")

            assert "memories" in result
            assert result["count"] == 1
            # Should not raise error even without categories

    def test_recall_handles_new_response_format(self):
        """Test that recall() handles new API response format"""
        with patch.object(self.client, '_request') as mock_request:
            # New format with categories and total
            mock_request.return_value = {
                "memories": [{"id": "mem1", "text": "Test"}],
                "categories": {"Work": {"count": 1, "avg_score": 0.9, "summary": "Work"}},
                "total": 1
            }

            result = self.client.recall("query", organized=True)

            assert "memories" in result
            assert "categories" in result
            assert "total" in result


class TestCategorySummaryType:
    """Test CategorySummary TypedDict"""

    def test_category_summary_fields(self):
        """Test CategorySummary has expected fields"""
        summary: CategorySummary = {
            "count": 5,
            "avg_score": 0.85,
            "summary": "Test summary"
        }

        assert summary["count"] == 5
        assert summary["avg_score"] == 0.85
        assert summary["summary"] == "Test summary"


class TestRecallMemoryType:
    """Test RecallMemory TypedDict"""

    def test_recall_memory_fields(self):
        """Test RecallMemory has expected fields"""
        memory: RecallMemory = {
            "id": "test-uuid",
            "text": "Test memory",
            "metadata": {
                "tags": ["tag1"],
                "category": "Work",
                "entities": [],
                "importance": 0.8,
                "summary": "Test"
            },
            "score": 0.92,
            "created_at": "2024-01-01T00:00:00Z",
            "source": "python-sdk",
            "project_id": "default"
        }

        assert memory["id"] == "test-uuid"
        assert memory["score"] == 0.92
        assert memory["metadata"]["category"] == "Work"


if __name__ == "__main__":
    print("Running RecallBricks Recall Tests\n")
    print("=" * 60)

    # Run tests manually without pytest
    test_classes = [
        TestRecallMethod,
        TestRecallWithServiceToken,
        TestOrganizedRecallResultType,
        TestRecallBackwardCompatibility,
        TestCategorySummaryType,
        TestRecallMemoryType
    ]

    passed = 0
    failed = 0

    for test_class in test_classes:
        print(f"\n{test_class.__name__}")
        print("-" * 40)
        test_instance = test_class()

        for method_name in dir(test_instance):
            if method_name.startswith("test_"):
                try:
                    if hasattr(test_instance, 'setup_method'):
                        test_instance.setup_method()
                    getattr(test_instance, method_name)()
                    print(f"  [PASS] {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"  [FAIL] {method_name}: {str(e)}")
                    failed += 1

    print("\n" + "=" * 60)
    print(f"\nResults: {passed} passed, {failed} failed")

    if failed == 0:
        print("All recall tests passed!")
    else:
        print(f"{failed} test(s) failed")
        exit(1)
