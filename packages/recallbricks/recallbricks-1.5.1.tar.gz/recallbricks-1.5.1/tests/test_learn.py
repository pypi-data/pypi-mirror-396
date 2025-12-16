"""
Test learn() functionality for RecallBricks Python SDK
Tests automatic metadata extraction via /api/v1/memories/learn endpoint
"""

try:
    import pytest
    HAS_PYTEST = True
except ImportError:
    HAS_PYTEST = False

import warnings
from unittest.mock import Mock, patch, MagicMock
from recallbricks import RecallBricks, AuthenticationError
from recallbricks.types import LearnedMemory, MemoryMetadata


class TestLearnMethod:
    """Test the learn() method for automatic metadata extraction"""

    def setup_method(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_dev_test123")

    def test_learn_calls_correct_endpoint(self):
        """Test that learn() calls /api/v1/memories/learn endpoint"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "id": "test-uuid",
                "text": "Test memory",
                "metadata": {
                    "tags": ["auto", "test"],
                    "category": "Work",
                    "entities": ["Python"],
                    "importance": 0.85,
                    "summary": "Auto summary"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }

            result = self.client.learn("Test memory content")

            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/memories/learn"

    def test_learn_returns_auto_metadata(self):
        """Test that learn() returns auto-generated metadata"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "id": "test-uuid",
                "text": "User prefers dark mode",
                "metadata": {
                    "tags": ["preference", "ui", "dark-mode"],
                    "category": "Preferences",
                    "entities": ["dark mode"],
                    "importance": 0.75,
                    "summary": "User UI preference for dark mode"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }

            result = self.client.learn("User prefers dark mode")

            assert "id" in result
            assert "metadata" in result
            assert "tags" in result["metadata"]
            assert "category" in result["metadata"]
            assert "entities" in result["metadata"]
            assert "importance" in result["metadata"]
            assert "summary" in result["metadata"]

    def test_learn_with_metadata_overrides(self):
        """Test that user can override auto-generated metadata"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {
                "id": "test-uuid",
                "text": "Test content",
                "metadata": {
                    "tags": ["custom-tag"],
                    "category": "Custom",
                    "entities": [],
                    "importance": 0.5,
                    "summary": "Custom"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }

            custom_metadata = {"tags": ["custom-tag"], "category": "Custom"}
            result = self.client.learn("Test content", metadata=custom_metadata)

            call_args = mock_request.call_args
            payload = call_args[1]["json"]
            assert "metadata" in payload
            assert payload["metadata"] == custom_metadata

    def test_learn_with_project_id(self):
        """Test learn() with project_id parameter"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid", "text": "Test"}

            self.client.learn("Test content", project_id="my-project")

            call_args = mock_request.call_args
            payload = call_args[1]["json"]
            assert payload["project_id"] == "my-project"

    def test_learn_with_custom_source(self):
        """Test learn() with custom source parameter"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid", "text": "Test"}

            self.client.learn("Test content", source="custom-source")

            call_args = mock_request.call_args
            payload = call_args[1]["json"]
            assert payload["source"] == "custom-source"

    def test_learn_default_source_is_python_sdk(self):
        """Test that default source is 'python-sdk'"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid", "text": "Test"}

            self.client.learn("Test content")

            call_args = mock_request.call_args
            payload = call_args[1]["json"]
            assert payload["source"] == "python-sdk"

    def test_learn_empty_text_raises_error(self):
        """Test that empty text raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.learn("")
            assert "text cannot be empty" in str(exc_info.value)
        else:
            try:
                self.client.learn("")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "text cannot be empty" in str(e)

    def test_learn_whitespace_text_raises_error(self):
        """Test that whitespace-only text raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.learn("   ")
            assert "text cannot be empty" in str(exc_info.value)
        else:
            try:
                self.client.learn("   ")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "text cannot be empty" in str(e)

    def test_learn_non_string_text_raises_error(self):
        """Test that non-string text raises TypeError"""
        if HAS_PYTEST:
            with pytest.raises(TypeError) as exc_info:
                self.client.learn(123)
            assert "text must be a string" in str(exc_info.value)
        else:
            try:
                self.client.learn(123)
                raise AssertionError("Expected TypeError")
            except TypeError as e:
                assert "text must be a string" in str(e)

    def test_learn_sanitizes_input(self):
        """Test that learn() sanitizes text input"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid", "text": "Test"}

            # Text with control characters
            self.client.learn("Test\x00content\x08here")

            call_args = mock_request.call_args
            payload = call_args[1]["json"]
            # Control characters should be removed
            assert "\x00" not in payload["text"]
            assert "\x08" not in payload["text"]


class TestLearnWithServiceToken:
    """Test learn() with service token authentication"""

    def setup_method(self):
        """Set up test client with service token"""
        self.client = RecallBricks(service_token="rbk_service_test123")

    def test_learn_requires_user_id_with_service_token(self):
        """Test that user_id is required when using service token"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.learn("Test content")
            assert "user_id is required" in str(exc_info.value)
        else:
            try:
                self.client.learn("Test content")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                assert "user_id is required" in str(e)

    def test_learn_with_user_id_succeeds(self):
        """Test that learn() succeeds with user_id when using service token"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid", "text": "Test"}

            self.client.learn("Test content", user_id="user_123")

            call_args = mock_request.call_args
            payload = call_args[1]["json"]
            assert payload["user_id"] == "user_123"

    def test_learn_empty_user_id_raises_error(self):
        """Test that empty user_id raises ValueError"""
        if HAS_PYTEST:
            with pytest.raises(ValueError) as exc_info:
                self.client.learn("Test content", user_id="")
            # Empty string is treated as missing user_id with service token
            assert "user_id is required" in str(exc_info.value)
        else:
            try:
                self.client.learn("Test content", user_id="")
                raise AssertionError("Expected ValueError")
            except ValueError as e:
                # Empty string is treated as missing user_id with service token
                assert "user_id is required" in str(e)

    def test_learn_non_string_user_id_raises_error(self):
        """Test that non-string user_id raises TypeError"""
        if HAS_PYTEST:
            with pytest.raises(TypeError) as exc_info:
                self.client.learn("Test content", user_id=123)
            assert "user_id must be a string" in str(exc_info.value)
        else:
            try:
                self.client.learn("Test content", user_id=123)
                raise AssertionError("Expected TypeError")
            except TypeError as e:
                assert "user_id must be a string" in str(e)


class TestSaveMemoryDeprecation:
    """Test save_memory() deprecation warning"""

    def setup_method(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_dev_test123")

    def test_save_memory_raises_deprecation_warning(self):
        """Test that save_memory() raises DeprecationWarning"""
        with patch.object(self.client, 'save') as mock_save:
            mock_save.return_value = {"id": "test-uuid"}

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                self.client.save_memory("Test content")

                assert len(w) == 1
                assert issubclass(w[0].category, DeprecationWarning)
                assert "save_memory() is deprecated" in str(w[0].message)
                assert "learn()" in str(w[0].message)

    def test_save_memory_still_works(self):
        """Test that save_memory() still functions correctly"""
        with patch.object(self.client, 'save') as mock_save:
            mock_save.return_value = {"id": "test-uuid", "text": "Test"}

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result = self.client.save_memory(
                    "Test content",
                    tags=["tag1"],
                    metadata={"key": "value"}
                )

            mock_save.assert_called_once_with(
                text="Test content",
                user_id=None,
                source="api",
                project_id="default",
                tags=["tag1"],
                metadata={"key": "value"},
                max_retries=3
            )


class TestLearnedMemoryType:
    """Test LearnedMemory dataclass"""

    def test_from_dict_full_response(self):
        """Test LearnedMemory.from_dict with full response"""
        data = {
            "id": "test-uuid",
            "text": "Test memory content",
            "metadata": {
                "tags": ["tag1", "tag2"],
                "category": "Work",
                "entities": ["Python", "SDK"],
                "importance": 0.85,
                "summary": "Test summary"
            },
            "created_at": "2024-01-01T00:00:00Z",
            "source": "python-sdk",
            "project_id": "my-project"
        }

        learned = LearnedMemory.from_dict(data)

        assert learned.id == "test-uuid"
        assert learned.text == "Test memory content"
        assert learned.metadata["tags"] == ["tag1", "tag2"]
        assert learned.metadata["category"] == "Work"
        assert learned.metadata["entities"] == ["Python", "SDK"]
        assert learned.metadata["importance"] == 0.85
        assert learned.metadata["summary"] == "Test summary"
        assert learned.created_at == "2024-01-01T00:00:00Z"
        assert learned.source == "python-sdk"
        assert learned.project_id == "my-project"

    def test_from_dict_minimal_response(self):
        """Test LearnedMemory.from_dict with minimal response"""
        data = {
            "id": "test-uuid",
            "text": "Test"
        }

        learned = LearnedMemory.from_dict(data)

        assert learned.id == "test-uuid"
        assert learned.text == "Test"
        assert learned.metadata["tags"] == []
        assert learned.metadata["category"] == ""
        assert learned.source == "python-sdk"  # default


class TestLearnRetries:
    """Test learn() retry behavior"""

    def setup_method(self):
        """Set up test client"""
        self.client = RecallBricks(api_key="rb_dev_test123")

    def test_learn_passes_max_retries(self):
        """Test that learn() passes max_retries to _request"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid"}

            self.client.learn("Test content", max_retries=5)

            call_args = mock_request.call_args
            assert call_args[1]["max_retries"] == 5

    def test_learn_default_max_retries(self):
        """Test that learn() uses default max_retries of 3"""
        with patch.object(self.client, '_request') as mock_request:
            mock_request.return_value = {"id": "test-uuid"}

            self.client.learn("Test content")

            call_args = mock_request.call_args
            assert call_args[1]["max_retries"] == 3


if __name__ == "__main__":
    print("Running RecallBricks Learn Tests\n")
    print("=" * 60)

    # Run tests manually without pytest
    test_classes = [
        TestLearnMethod,
        TestLearnWithServiceToken,
        TestSaveMemoryDeprecation,
        TestLearnedMemoryType,
        TestLearnRetries
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
        print("All learn tests passed!")
    else:
        print(f"{failed} test(s) failed")
        exit(1)
