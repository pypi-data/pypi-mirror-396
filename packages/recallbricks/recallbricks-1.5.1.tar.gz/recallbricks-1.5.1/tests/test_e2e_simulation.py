"""
End-to-End User Simulation Tests for RecallBricks Python SDK
Simulates real user workflows to ensure the SDK works as designed.
"""

import sys
import os
from unittest.mock import patch, Mock
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recallbricks import RecallBricks, AuthenticationError, ValidationError


class UserSimulation:
    """Simulates a user interacting with RecallBricks SDK"""

    def __init__(self):
        self.results = []
        self.errors = []

    def log(self, message, success=True):
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {message}")
        self.results.append((message, success))
        if not success:
            self.errors.append(message)

    def run_all_scenarios(self):
        """Run all user simulation scenarios"""
        print("\n" + "=" * 70)
        print("RECALLBRICKS SDK END-TO-END USER SIMULATION")
        print("=" * 70)

        self.scenario_1_basic_api_key_auth()
        self.scenario_2_service_token_auth()
        self.scenario_3_learn_and_recall_workflow()
        self.scenario_4_save_search_delete_workflow()
        self.scenario_5_error_handling()
        self.scenario_6_input_validation()
        self.scenario_7_deprecation_warnings()
        self.scenario_8_relationship_queries()
        self.scenario_9_advanced_features()

        self.print_summary()
        return len(self.errors) == 0

    def scenario_1_basic_api_key_auth(self):
        """Scenario 1: User authenticates with API key"""
        print("\n--- Scenario 1: Basic API Key Authentication ---")

        # Test valid API key
        try:
            client = RecallBricks(api_key="rb_dev_test_key_12345")
            assert client.api_key == "rb_dev_test_key_12345"
            assert client.service_token is None
            assert 'X-API-Key' in client.session.headers
            self.log("Create client with API key")
        except Exception as e:
            self.log(f"Create client with API key: {e}", False)

        # Test no auth raises error
        try:
            RecallBricks()
            self.log("Reject client without auth", False)
        except AuthenticationError:
            self.log("Reject client without auth (raises AuthenticationError)")

        # Test both auth methods raises error
        try:
            RecallBricks(api_key="test", service_token="test")
            self.log("Reject client with both auth methods", False)
        except AuthenticationError:
            self.log("Reject client with both auth methods")

    def scenario_2_service_token_auth(self):
        """Scenario 2: User authenticates with service token"""
        print("\n--- Scenario 2: Service Token Authentication ---")

        # Test valid service token
        try:
            client = RecallBricks(service_token="rbk_service_test_token")
            assert client.service_token == "rbk_service_test_token"
            assert client.api_key is None
            assert 'X-Service-Token' in client.session.headers
            self.log("Create client with service token")
        except Exception as e:
            self.log(f"Create client with service token: {e}", False)

        # Test service token requires user_id for operations
        client = RecallBricks(service_token="rbk_service_test")
        try:
            with patch.object(client, '_request') as mock:
                mock.return_value = {"id": "test"}
                client.learn("Test memory")  # Should fail without user_id
            self.log("Require user_id with service token", False)
        except ValueError as e:
            if "user_id is required" in str(e):
                self.log("Require user_id with service token")
            else:
                self.log(f"Wrong error: {e}", False)

    def scenario_3_learn_and_recall_workflow(self):
        """Scenario 3: User learns memories and recalls them"""
        print("\n--- Scenario 3: Learn and Recall Workflow ---")

        client = RecallBricks(api_key="rb_dev_test")

        # Mock the API responses
        with patch.object(client, '_request') as mock_request:
            # Learn a memory
            mock_request.return_value = {
                "id": "mem-uuid-123",
                "text": "User prefers dark mode and Python",
                "metadata": {
                    "tags": ["preference", "ui", "programming"],
                    "category": "Preferences",
                    "entities": ["dark mode", "Python"],
                    "importance": 0.85,
                    "summary": "User UI and language preferences"
                },
                "created_at": "2024-01-01T00:00:00Z"
            }

            try:
                result = client.learn("User prefers dark mode and Python")
                assert result["id"] == "mem-uuid-123"
                assert "metadata" in result
                assert "tags" in result["metadata"]
                self.log("Learn memory with auto-metadata")
            except Exception as e:
                self.log(f"Learn memory: {e}", False)

            # Recall memories
            mock_request.return_value = {
                "memories": [
                    {
                        "id": "mem-uuid-123",
                        "text": "User prefers dark mode",
                        "score": 0.95,
                        "metadata": {"category": "Preferences"}
                    }
                ],
                "count": 1
            }

            try:
                results = client.recall("user preferences")
                assert "memories" in results
                assert len(results["memories"]) == 1
                self.log("Recall memories by query")
            except Exception as e:
                self.log(f"Recall memories: {e}", False)

            # Recall with organized results
            mock_request.return_value = {
                "memories": [
                    {"id": "m1", "text": "Work task", "metadata": {"category": "Work"}},
                    {"id": "m2", "text": "Personal note", "metadata": {"category": "Personal"}}
                ],
                "categories": {
                    "Work": {"count": 5, "avg_score": 0.85, "summary": "Work items"},
                    "Personal": {"count": 3, "avg_score": 0.72, "summary": "Personal notes"}
                },
                "total": 8
            }

            try:
                results = client.recall("tasks", organized=True)
                assert "categories" in results
                assert "Work" in results["categories"]
                self.log("Recall with organized categories")
            except Exception as e:
                self.log(f"Organized recall: {e}", False)

    def scenario_4_save_search_delete_workflow(self):
        """Scenario 4: User saves, searches, and deletes memories"""
        print("\n--- Scenario 4: Save, Search, Delete Workflow ---")

        client = RecallBricks(api_key="rb_dev_test")

        with patch.object(client, '_request') as mock_request:
            # Save a memory
            mock_request.return_value = {
                "id": "saved-mem-456",
                "text": "Important project deadline",
                "created_at": "2024-01-01T00:00:00Z"
            }

            try:
                result = client.save("Important project deadline", tags=["urgent", "work"])
                assert result["id"] == "saved-mem-456"
                self.log("Save memory with tags")
            except Exception as e:
                self.log(f"Save memory: {e}", False)

            # Search memories
            mock_request.return_value = {
                "memories": [
                    {"id": "saved-mem-456", "text": "Important project deadline", "score": 0.92}
                ],
                "count": 1
            }

            try:
                results = client.search("deadline")
                assert "memories" in results
                self.log("Search memories")
            except Exception as e:
                self.log(f"Search memories: {e}", False)

            # Get specific memory
            mock_request.return_value = {
                "id": "saved-mem-456",
                "text": "Important project deadline"
            }

            try:
                memory = client.get("saved-mem-456")
                assert memory["id"] == "saved-mem-456"
                self.log("Get specific memory by ID")
            except Exception as e:
                self.log(f"Get memory: {e}", False)

            # Update memory
            mock_request.return_value = {
                "id": "saved-mem-456",
                "text": "Updated: Important project deadline next week"
            }

            try:
                result = client.update("saved-mem-456", text="Updated: Important project deadline next week")
                assert "Updated" in result["text"]
                self.log("Update memory text")
            except Exception as e:
                self.log(f"Update memory: {e}", False)

            # Delete memory
            mock_request.return_value = {"success": True}

            try:
                result = client.delete("saved-mem-456")
                self.log("Delete memory")
            except Exception as e:
                self.log(f"Delete memory: {e}", False)

            # Get all memories
            mock_request.return_value = {
                "memories": [
                    {"id": "m1", "text": "Memory 1"},
                    {"id": "m2", "text": "Memory 2"}
                ],
                "count": 2
            }

            try:
                all_memories = client.get_all()
                assert "memories" in all_memories
                self.log("Get all memories")
            except Exception as e:
                self.log(f"Get all: {e}", False)

    def scenario_5_error_handling(self):
        """Scenario 5: SDK handles errors gracefully"""
        print("\n--- Scenario 5: Error Handling ---")

        client = RecallBricks(api_key="rb_dev_test")

        with patch.object(client, 'session') as mock_session:
            # Test 401 authentication error
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.content = json.dumps({
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API key",
                    "hint": "Check your API key"
                }
            }).encode()
            mock_response.json.return_value = {
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API key",
                    "hint": "Check your API key"
                }
            }
            mock_session.request.return_value = mock_response

            try:
                client.learn("test")
                self.log("Handle 401 auth error", False)
            except AuthenticationError as e:
                assert "Invalid API key" in str(e)
                self.log("Handle 401 auth error (raises AuthenticationError)")
            except Exception as e:
                self.log(f"Wrong error type: {type(e)}", False)

    def scenario_6_input_validation(self):
        """Scenario 6: SDK validates user inputs"""
        print("\n--- Scenario 6: Input Validation ---")

        client = RecallBricks(api_key="rb_dev_test")

        # Empty text
        try:
            client.learn("")
            self.log("Reject empty text", False)
        except ValueError as e:
            if "empty" in str(e).lower():
                self.log("Reject empty text (raises ValueError)")
            else:
                self.log(f"Wrong error: {e}", False)

        # Whitespace only text
        try:
            client.learn("   ")
            self.log("Reject whitespace-only text", False)
        except ValueError:
            self.log("Reject whitespace-only text")

        # Non-string text
        try:
            client.learn(12345)
            self.log("Reject non-string text", False)
        except TypeError:
            self.log("Reject non-string text (raises TypeError)")

        # Invalid helpfulness score
        try:
            client.recall("query", min_helpfulness_score=1.5)
            self.log("Reject invalid helpfulness score", False)
        except ValueError:
            self.log("Reject invalid helpfulness score (out of range)")

        # Empty query
        try:
            client.recall("")
            self.log("Reject empty query", False)
        except ValueError:
            self.log("Reject empty query")

        # Empty memory_id for update
        try:
            client.update("", text="new text")
            self.log("Reject empty memory_id for update", False)
        except ValueError:
            self.log("Reject empty memory_id for update")

        # Update with no changes
        try:
            client.update("mem-123")
            self.log("Reject update with no fields", False)
        except ValueError:
            self.log("Reject update with no fields")

    def scenario_7_deprecation_warnings(self):
        """Scenario 7: Deprecated methods show warnings"""
        print("\n--- Scenario 7: Deprecation Warnings ---")

        import warnings
        client = RecallBricks(api_key="rb_dev_test")

        with patch.object(client, 'save') as mock_save:
            mock_save.return_value = {"id": "test"}

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                client.save_memory("Test content")

                if len(w) == 1 and issubclass(w[0].category, DeprecationWarning):
                    self.log("save_memory() shows DeprecationWarning")
                else:
                    self.log("save_memory() deprecation warning missing", False)

    def scenario_8_relationship_queries(self):
        """Scenario 8: User queries memory relationships"""
        print("\n--- Scenario 8: Relationship Queries ---")

        client = RecallBricks(api_key="rb_dev_test")

        with patch.object(client, '_request') as mock_request:
            # Get relationships
            mock_request.return_value = {
                "memory_id": "mem-123",
                "count": 3,
                "relationships": [
                    {"id": "r1", "type": "related_to", "target_id": "mem-456"},
                    {"id": "r2", "type": "depends_on", "target_id": "mem-789"}
                ]
            }

            try:
                result = client.get_relationships("mem-123")
                assert result["count"] == 3
                self.log("Get memory relationships")
            except Exception as e:
                self.log(f"Get relationships: {e}", False)

            # Get graph context
            mock_request.return_value = {
                "root_id": "mem-123",
                "depth": 2,
                "nodes": [
                    {"id": "mem-123", "text": "Root memory"},
                    {"id": "mem-456", "text": "Related memory"}
                ],
                "edges": [
                    {"from": "mem-123", "to": "mem-456", "type": "related_to"}
                ]
            }

            try:
                result = client.get_graph_context("mem-123", depth=2)
                assert result["depth"] == 2
                assert len(result["nodes"]) == 2
                self.log("Get graph context")
            except Exception as e:
                self.log(f"Get graph context: {e}", False)

        # Validate relationship inputs
        try:
            client.get_relationships("")
            self.log("Reject empty memory_id for relationships", False)
        except ValueError:
            self.log("Reject empty memory_id for relationships")

        try:
            client.get_graph_context("mem-123", depth=-1)
            self.log("Reject negative depth", False)
        except ValueError:
            self.log("Reject negative depth")

    def scenario_9_advanced_features(self):
        """Scenario 9: User uses advanced SDK features"""
        print("\n--- Scenario 9: Advanced Features ---")

        client = RecallBricks(api_key="rb_dev_test")

        with patch.object(client, '_request') as mock_request:
            # Health check
            mock_request.return_value = {
                "status": "healthy",
                "version": "1.0.0"
            }

            try:
                result = client.health()
                assert result["status"] == "healthy"
                self.log("Check API health")
            except Exception as e:
                self.log(f"Health check: {e}", False)

            # Rate limit check
            mock_request.return_value = {
                "limit": 1000,
                "remaining": 950,
                "reset": 3600
            }

            try:
                result = client.get_rate_limit()
                assert result["remaining"] == 950
                self.log("Get rate limit status")
            except Exception as e:
                self.log(f"Rate limit: {e}", False)

        # Custom base URL
        try:
            custom_client = RecallBricks(
                api_key="test",
                base_url="https://custom.api.com/api/v2"
            )
            assert custom_client.base_url == "https://custom.api.com/api/v2"
            self.log("Use custom base URL")
        except Exception as e:
            self.log(f"Custom base URL: {e}", False)

        # Custom timeout
        try:
            timeout_client = RecallBricks(api_key="test", timeout=60)
            assert timeout_client.timeout == 60
            self.log("Set custom timeout")
        except Exception as e:
            self.log(f"Custom timeout: {e}", False)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("END-TO-END SIMULATION SUMMARY")
        print("=" * 70)

        total = len(self.results)
        passed = sum(1 for _, success in self.results if success)
        failed = total - passed

        print(f"Total scenarios tested: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success rate: {passed/total*100:.1f}%")

        if self.errors:
            print("\nFailed tests:")
            for error in self.errors:
                print(f"  - {error}")

        print("=" * 70)


def run_e2e_simulation():
    """Run the end-to-end simulation"""
    simulation = UserSimulation()
    success = simulation.run_all_scenarios()
    return success


if __name__ == "__main__":
    success = run_e2e_simulation()
    sys.exit(0 if success else 1)
