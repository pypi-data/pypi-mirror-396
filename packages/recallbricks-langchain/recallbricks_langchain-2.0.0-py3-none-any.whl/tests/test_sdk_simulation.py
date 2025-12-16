"""
Comprehensive SDK Simulation Tests

This module simulates real user workflows to ensure the entire SDK works as designed.
Tests all major components: RecallBricksMemory, RecallBricksChatMessageHistory,
RecallBricksRetriever, and RecallBricksClient.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import os
import uuid
import time

# Import all SDK components
from recallbricks_langchain import (
    # LangChain Integrations
    RecallBricksMemory,
    RecallBricksChatMessageHistory,
    RecallBricksRetriever,
    # Base Client
    RecallBricksClient,
    # Exceptions
    RecallBricksError,
    ValidationError,
    RateLimitError,
    CircuitBreakerError,
    APIError,
    AuthenticationError,
    NotFoundError,
    # Utilities
    CircuitBreaker,
    RateLimiter,
    MetricsCollector,
)
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document


class MockResponse:
    """Mock HTTP response object."""

    def __init__(self, json_data, status_code=200, headers=None):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers or {}
        self.ok = 200 <= status_code < 300
        self.text = json.dumps(json_data) if json_data else ""
        self.content = self.text.encode() if self.text else b""

    def json(self):
        return self.json_data

    def raise_for_status(self):
        if not self.ok:
            from requests import HTTPError
            raise HTTPError(f"HTTP Error: {self.status_code}")


class TestRecallBricksMemorySimulation(unittest.TestCase):
    """Simulate real user workflow with RecallBricksMemory."""

    def setUp(self):
        """Set up test fixtures with valid parameters."""
        self.api_key = "test-api-key-12345"
        self.agent_id = "agent-simulation-test"
        self.user_id = str(uuid.uuid4())  # Valid UUID format

    @patch('recallbricks_langchain.memory.get_session')
    def test_full_memory_workflow(self, mock_get_session):
        """Test complete memory workflow: learn -> recall -> save_context -> load."""
        # Set up mock session
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Mock responses
        learn_response = MockResponse({
            "id": "mem-123",
            "text": "User prefers dark mode",
            "metadata": {
                "tags": ["preferences", "ui"],
                "category": "Preferences",
                "importance": 0.8
            }
        })

        recall_response = MockResponse({
            "memories": [
                {
                    "id": "mem-123",
                    "text": "User prefers dark mode",
                    "score": 0.95,
                    "metadata": {
                        "tags": ["preferences", "ui"],
                        "category": "Preferences",
                        "importance": 0.8
                    }
                }
            ],
            "categories": {
                "Preferences": {
                    "summary": "User UI preferences",
                    "count": 1,
                    "avg_score": 0.95
                }
            }
        })

        mock_session.post.return_value = learn_response

        # Initialize memory
        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            enable_logging=False
        )

        # Test learn()
        result = memory.learn("User prefers dark mode")
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "mem-123")

        # Test recall()
        mock_session.post.return_value = recall_response
        result = memory.recall("user preferences")
        self.assertIn("memories", result)
        self.assertEqual(len(result["memories"]), 1)
        self.assertIn("categories", result)

        # Test save_context()
        mock_session.post.return_value = learn_response
        memory.save_context(
            {"input": "What is my preferred theme?"},
            {"output": "You prefer dark mode for your applications."}
        )

        # Test load_memory_variables()
        mock_session.post.return_value = recall_response
        result = memory.load_memory_variables({"input": "preferences"})
        self.assertIn("history", result)

        print("RecallBricksMemory full workflow: PASSED")

    @patch('recallbricks_langchain.memory.get_session')
    def test_organized_recall_formatting(self, mock_get_session):
        """Test that organized recall formats context correctly."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        recall_response = MockResponse({
            "memories": [
                {
                    "id": "mem-1",
                    "text": "User prefers dark mode",
                    "score": 0.95,
                    "metadata": {"category": "Preferences"}
                },
                {
                    "id": "mem-2",
                    "text": "User works in Python",
                    "score": 0.90,
                    "metadata": {"category": "Skills"}
                }
            ],
            "categories": {
                "Preferences": {
                    "summary": "User UI preferences",
                    "count": 1,
                    "avg_score": 0.95
                },
                "Skills": {
                    "summary": "Programming skills",
                    "count": 1,
                    "avg_score": 0.90
                }
            }
        })

        mock_session.post.return_value = recall_response

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            organized=True,
            enable_logging=False
        )

        result = memory.load_memory_variables({"input": "tell me about the user"})

        # Check that history contains organized context
        history = result.get("history", [])
        self.assertTrue(len(history) > 0)

        # The formatted context should contain category information
        context = history[0] if history else ""
        self.assertIn("Relevant Context", context)

        print("Organized recall formatting: PASSED")

    @patch('recallbricks_langchain.memory.get_session')
    def test_return_messages_mode(self, mock_get_session):
        """Test that return_messages=True returns BaseMessage objects."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        recall_response = MockResponse({
            "memories": [
                {"id": "mem-1", "text": "User said hello", "score": 0.9, "metadata": {}},
            ],
            "categories": {}
        })

        mock_session.post.return_value = recall_response

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            return_messages=True,
            enable_logging=False
        )

        result = memory.load_memory_variables({"input": "test"})

        # Should return list of HumanMessage objects
        history = result.get("history", [])
        self.assertIsInstance(history, list)
        if history:
            self.assertIsInstance(history[0], HumanMessage)

        print("Return messages mode: PASSED")

    def test_validation_errors(self):
        """Test that validation errors are raised correctly."""
        # Test missing agent_id
        with self.assertRaises(ValueError):
            RecallBricksMemory(
                agent_id="",
                api_key=self.api_key
            )

        # Test invalid user_id format (not UUID)
        with self.assertRaises(ValueError):
            RecallBricksMemory(
                agent_id=self.agent_id,
                user_id="invalid-not-uuid",
                api_key=self.api_key
            )

        # Test HTTP URL (must be HTTPS)
        with self.assertRaises(ValueError):
            RecallBricksMemory(
                agent_id=self.agent_id,
                api_key=self.api_key,
                api_url="http://insecure.com"
            )

        # Test missing API key
        with self.assertRaises(ValueError):
            # Clear env var if set
            original = os.environ.pop("RECALLBRICKS_API_KEY", None)
            try:
                RecallBricksMemory(agent_id=self.agent_id)
            finally:
                if original:
                    os.environ["RECALLBRICKS_API_KEY"] = original

        print("Validation errors: PASSED")

    @patch('recallbricks_langchain.memory.get_session')
    def test_metrics_collection(self, mock_get_session):
        """Test that metrics are collected correctly."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.post.return_value = MockResponse({"id": "mem-1"})

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            enable_metrics=True,
            enable_logging=False
        )

        # Perform some operations
        memory.learn("Test memory")

        # Check legacy metrics
        metrics = memory.get_metrics()
        self.assertIn("save_count", metrics)

        # Check detailed metrics
        detailed = memory.get_detailed_metrics()
        self.assertIn("requests_total", detailed)
        self.assertIn("requests_success", detailed)

        # Check Prometheus export
        prometheus = memory.get_prometheus_metrics()
        self.assertIn("recallbricks_", prometheus)

        print("Metrics collection: PASSED")

    @patch('recallbricks_langchain.memory.get_session')
    def test_health_check(self, mock_get_session):
        """Test health check functionality."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.get.return_value = MockResponse({"status": "healthy"})

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            enable_logging=False
        )

        health = memory.health_check()

        self.assertIn("status", health)
        self.assertIn("checks", health)
        self.assertIn("circuit_breaker", health["checks"])
        self.assertIn("rate_limiter", health["checks"])

        print("Health check: PASSED")


class TestRecallBricksChatMessageHistorySimulation(unittest.TestCase):
    """Simulate real user workflow with RecallBricksChatMessageHistory."""

    def setUp(self):
        self.api_key = "test-api-key-12345"
        self.session_id = "session-" + str(uuid.uuid4())[:8]

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_full_chat_history_workflow(self, mock_get_session):
        """Test complete chat history workflow: add messages -> retrieve."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Mock learn response
        learn_response = MockResponse({"id": "msg-123"})
        mock_session.post.return_value = learn_response

        # Initialize chat history
        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id,
            enable_logging=False
        )

        # Add messages
        history.add_user_message("Hello, how are you?")
        history.add_ai_message("I'm doing well, thank you!")

        # Verify messages were added
        self.assertEqual(mock_session.post.call_count, 2)

        # Check the payloads
        calls = mock_session.post.call_args_list
        first_call = calls[0]
        self.assertIn("human:", first_call[1]["json"]["text"])

        second_call = calls[1]
        self.assertIn("ai:", second_call[1]["json"]["text"])

        print("RecallBricksChatMessageHistory add messages: PASSED")

    @patch('recallbricks_langchain.chat_history.get_session')
    def test_load_messages(self, mock_get_session):
        """Test loading messages from RecallBricks."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Mock recall response with existing messages
        recall_response = MockResponse({
            "memories": [
                {
                    "text": "human: Hello there",
                    "metadata": {"message_type": "human", "session_id": self.session_id}
                },
                {
                    "text": "ai: Hi! How can I help?",
                    "metadata": {"message_type": "ai", "session_id": self.session_id}
                }
            ]
        })
        mock_session.post.return_value = recall_response

        history = RecallBricksChatMessageHistory(
            api_key=self.api_key,
            session_id=self.session_id,
            enable_logging=False
        )

        # Access messages property triggers load
        messages = history.messages

        self.assertEqual(len(messages), 2)
        self.assertIsInstance(messages[0], HumanMessage)
        self.assertIsInstance(messages[1], AIMessage)

        print("RecallBricksChatMessageHistory load messages: PASSED")

    def test_validation(self):
        """Test chat history validation."""
        # Missing API key
        with self.assertRaises(ValidationError):
            RecallBricksChatMessageHistory(
                api_key="",
                session_id=self.session_id
            )

        # Missing session_id
        with self.assertRaises(ValidationError):
            RecallBricksChatMessageHistory(
                api_key=self.api_key,
                session_id=""
            )

        # HTTP URL
        with self.assertRaises(ValidationError):
            RecallBricksChatMessageHistory(
                api_key=self.api_key,
                session_id=self.session_id,
                api_url="http://insecure.com"
            )

        print("RecallBricksChatMessageHistory validation: PASSED")


class TestRecallBricksRetrieverSimulation(unittest.TestCase):
    """Simulate real user workflow with RecallBricksRetriever."""

    def setUp(self):
        self.api_key = "test-api-key-12345"

    @patch('recallbricks_langchain.retriever.get_session')
    def test_retrieve_documents(self, mock_get_session):
        """Test document retrieval for RAG workflow."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        recall_response = MockResponse({
            "memories": [
                {
                    "id": "doc-1",
                    "text": "RecallBricks is a cognitive memory infrastructure.",
                    "score": 0.95,
                    "metadata": {
                        "tags": ["product", "overview"],
                        "category": "Documentation",
                        "importance": 0.9,
                        "entities": ["RecallBricks"]
                    },
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": "doc-2",
                    "text": "It provides persistent memory for AI agents.",
                    "score": 0.88,
                    "metadata": {
                        "tags": ["features"],
                        "category": "Features",
                        "importance": 0.8,
                        "entities": ["AI agents"]
                    },
                    "created_at": "2024-01-02T00:00:00Z"
                }
            ],
            "categories": {
                "Documentation": {"summary": "Product docs", "count": 1, "avg_score": 0.95},
                "Features": {"summary": "Feature descriptions", "count": 1, "avg_score": 0.88}
            }
        })
        mock_session.post.return_value = recall_response

        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            k=5,
            organized=True,
            enable_logging=False
        )

        # Test _get_relevant_documents
        documents = retriever._get_relevant_documents("What is RecallBricks?")

        self.assertEqual(len(documents), 2)
        self.assertIsInstance(documents[0], Document)
        self.assertEqual(documents[0].page_content, "RecallBricks is a cognitive memory infrastructure.")
        self.assertIn("score", documents[0].metadata)
        self.assertEqual(documents[0].metadata["score"], 0.95)

        print("RecallBricksRetriever retrieve documents: PASSED")

    @patch('recallbricks_langchain.retriever.get_session')
    def test_retrieve_with_categories(self, mock_get_session):
        """Test document retrieval with category summaries."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        recall_response = MockResponse({
            "memories": [
                {"id": "doc-1", "text": "Test doc", "score": 0.9, "metadata": {"category": "Test"}}
            ],
            "categories": {
                "Test": {"summary": "Test category", "count": 1, "avg_score": 0.9}
            }
        })
        mock_session.post.return_value = recall_response

        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            enable_logging=False
        )

        result = retriever.get_relevant_documents_with_categories("test query")

        self.assertIn("documents", result)
        self.assertIn("categories", result)
        self.assertEqual(len(result["documents"]), 1)
        self.assertIn("Test", result["categories"])

        print("RecallBricksRetriever with categories: PASSED")

    def test_validation(self):
        """Test retriever validation."""
        # Missing API key
        with self.assertRaises(ValidationError):
            RecallBricksRetriever(api_key="")

        # Invalid k value
        with self.assertRaises(ValidationError):
            RecallBricksRetriever(api_key=self.api_key, k=0)

        with self.assertRaises(ValidationError):
            RecallBricksRetriever(api_key=self.api_key, k=101)

        # HTTP URL
        with self.assertRaises(ValidationError):
            RecallBricksRetriever(
                api_key=self.api_key,
                api_url="http://insecure.com"
            )

        print("RecallBricksRetriever validation: PASSED")


class TestRecallBricksClientSimulation(unittest.TestCase):
    """Simulate real user workflow with RecallBricksClient."""

    def setUp(self):
        self.api_key = "test-api-key-12345"

    @patch('recallbricks_langchain.client.get_session')
    def test_client_initialization(self, mock_get_session):
        """Test client initialization."""
        client = RecallBricksClient(
            api_key=self.api_key,
            enable_logging=False
        )

        self.assertEqual(client.api_key, self.api_key)
        self.assertIsNotNone(client.circuit_breaker)
        self.assertIsNotNone(client.rate_limiter)

        print("RecallBricksClient initialization: PASSED")

    @patch('recallbricks_langchain.client.get_session')
    def test_client_get_request(self, mock_get_session):
        """Test GET request through client."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.request.return_value = MockResponse({"status": "healthy"})

        client = RecallBricksClient(
            api_key=self.api_key,
            enable_logging=False
        )

        result = client.get("/health")

        self.assertEqual(result["status"], "healthy")
        mock_session.request.assert_called_once()

        print("RecallBricksClient GET request: PASSED")

    @patch('recallbricks_langchain.client.get_session')
    def test_client_post_request(self, mock_get_session):
        """Test POST request through client."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.request.return_value = MockResponse({"id": "new-123"})

        client = RecallBricksClient(
            api_key=self.api_key,
            enable_deduplication=False,  # Disable for this test
            enable_logging=False
        )

        result = client.post("/memories/learn", {"text": "test"})

        self.assertEqual(result["id"], "new-123")

        print("RecallBricksClient POST request: PASSED")

    def test_authentication_validation(self):
        """Test client authentication validation."""
        # Clear env vars
        original_key = os.environ.pop("RECALLBRICKS_API_KEY", None)
        original_token = os.environ.pop("RECALLBRICKS_SERVICE_TOKEN", None)

        try:
            with self.assertRaises(AuthenticationError):
                RecallBricksClient()
        finally:
            if original_key:
                os.environ["RECALLBRICKS_API_KEY"] = original_key
            if original_token:
                os.environ["RECALLBRICKS_SERVICE_TOKEN"] = original_token

        print("RecallBricksClient authentication validation: PASSED")

    @patch('recallbricks_langchain.client.get_session')
    def test_client_health_check(self, mock_get_session):
        """Test client health check."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.request.return_value = MockResponse({"status": "healthy"})

        client = RecallBricksClient(
            api_key=self.api_key,
            enable_logging=False
        )

        health = client.health_check()

        self.assertIn("status", health)
        self.assertIn("checks", health)

        print("RecallBricksClient health check: PASSED")


class TestUtilitiesSimulation(unittest.TestCase):
    """Test utility classes: CircuitBreaker, RateLimiter, MetricsCollector."""

    def test_circuit_breaker_normal_operation(self):
        """Test circuit breaker in normal closed state."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

        # Normal successful calls
        result = cb.call(lambda: "success")
        self.assertEqual(result, "success")
        self.assertEqual(cb.state, "closed")

        print("CircuitBreaker normal operation: PASSED")

    def test_circuit_breaker_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        def failing_func():
            raise ValueError("Simulated failure")

        # First failure
        with self.assertRaises(ValueError):
            cb.call(failing_func)
        self.assertEqual(cb.failure_count, 1)

        # Second failure - should open circuit
        with self.assertRaises(ValueError):
            cb.call(failing_func)
        self.assertEqual(cb.state, "open")

        # Next call should raise CircuitBreakerError
        with self.assertRaises(CircuitBreakerError):
            cb.call(failing_func)

        print("CircuitBreaker opens on failures: PASSED")

    def test_rate_limiter(self):
        """Test rate limiter allows/denies requests correctly."""
        rl = RateLimiter(rate=2, per=1)  # 2 requests per second

        # First two should be allowed
        self.assertTrue(rl.allow())
        self.assertTrue(rl.allow())

        # Third should be denied
        self.assertFalse(rl.allow())

        # Wait for token refill
        time.sleep(1.1)
        self.assertTrue(rl.allow())

        print("RateLimiter: PASSED")

    def test_metrics_collector(self):
        """Test metrics collection and export."""
        mc = MetricsCollector()

        # Increment counters
        mc.increment("requests_total", 10)
        mc.increment("requests_success", 8)
        mc.increment("requests_failed", 2)

        # Record response times
        mc.record_response_time(0.1)
        mc.record_response_time(0.2)
        mc.record_response_time(0.15)

        # Get metrics
        metrics = mc.get_metrics()

        self.assertEqual(metrics["requests_total"], 10)
        self.assertEqual(metrics["requests_success"], 8)
        self.assertEqual(metrics["success_rate"], 0.8)
        self.assertIn("response_time_avg", metrics)

        # Test Prometheus export
        prometheus = mc.export_prometheus()
        self.assertIn("recallbricks_requests_total", prometheus)

        print("MetricsCollector: PASSED")


class TestErrorHandlingSimulation(unittest.TestCase):
    """Test error handling across the SDK."""

    def setUp(self):
        self.api_key = "test-api-key-12345"
        self.agent_id = "agent-test"
        self.user_id = str(uuid.uuid4())

    @patch('recallbricks_langchain.memory.get_session')
    def test_graceful_degradation_on_api_error(self, mock_get_session):
        """Test that SDK handles API errors gracefully."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Simulate API error
        error_response = MockResponse(
            {"error": {"message": "Internal server error"}},
            status_code=500
        )
        mock_session.post.return_value = error_response

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            max_retries=0,  # No retries for faster test
            enable_logging=False
        )

        # load_memory_variables should return empty history on error
        result = memory.load_memory_variables({"input": "test"})
        self.assertEqual(result, {"history": []})

        print("Graceful degradation on API error: PASSED")

    @patch('recallbricks_langchain.memory.get_session')
    def test_empty_input_handling(self, mock_get_session):
        """Test handling of empty inputs."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.post.return_value = MockResponse({"id": "mem-1"})

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            enable_logging=False
        )

        # Empty input should be handled gracefully
        memory.save_context({"input": ""}, {"output": "response"})

        # Whitespace-only should also be handled
        memory.save_context({"input": "   "}, {"output": "response"})

        # Neither should have made API calls (skipped)
        self.assertEqual(mock_session.post.call_count, 0)

        print("Empty input handling: PASSED")

    @patch('recallbricks_langchain.memory.get_session')
    def test_deduplication(self, mock_get_session):
        """Test request deduplication prevents duplicate saves."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session
        mock_session.post.return_value = MockResponse({"id": "mem-1"})

        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            enable_deduplication=True,
            enable_logging=False
        )

        # First save should go through
        memory.save_context({"input": "hello"}, {"output": "world"})
        first_call_count = mock_session.post.call_count

        # Second identical save should be deduplicated
        memory.save_context({"input": "hello"}, {"output": "world"})

        # Call count should be same (duplicate was skipped)
        self.assertEqual(mock_session.post.call_count, first_call_count)

        print("Deduplication: PASSED")


class TestEndToEndSimulation(unittest.TestCase):
    """End-to-end simulation of typical user workflows."""

    def setUp(self):
        self.api_key = "test-api-key-12345"
        self.agent_id = "chatbot-agent"
        self.user_id = str(uuid.uuid4())

    @patch('recallbricks_langchain.memory.get_session')
    def test_chatbot_conversation_flow(self, mock_get_session):
        """Simulate a full chatbot conversation using RecallBricksMemory."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Set up responses
        learn_response = MockResponse({"id": "mem-123"})
        recall_response = MockResponse({
            "memories": [
                {
                    "id": "mem-1",
                    "text": "User: My name is Alice",
                    "score": 0.95,
                    "metadata": {"category": "Personal Info"}
                }
            ],
            "categories": {
                "Personal Info": {"summary": "User identity", "count": 1, "avg_score": 0.95}
            }
        })

        # Initialize memory for chatbot
        memory = RecallBricksMemory(
            agent_id=self.agent_id,
            user_id=self.user_id,
            api_key=self.api_key,
            organized=True,
            enable_logging=False
        )

        # Simulate conversation turn 1: User introduces themselves
        mock_session.post.return_value = learn_response
        memory.save_context(
            {"input": "Hi! My name is Alice."},
            {"output": "Nice to meet you, Alice! How can I help you today?"}
        )

        # Simulate conversation turn 2: User asks about something
        mock_session.post.return_value = recall_response
        context = memory.load_memory_variables({"input": "What's my name again?"})

        # Verify context was retrieved
        self.assertIn("history", context)

        # Simulate conversation turn 3: Bot uses context to respond
        mock_session.post.return_value = learn_response
        memory.save_context(
            {"input": "What's my name again?"},
            {"output": "Your name is Alice, as you mentioned earlier!"}
        )

        print("Chatbot conversation flow: PASSED")

    @patch('recallbricks_langchain.retriever.get_session')
    def test_rag_workflow(self, mock_get_session):
        """Simulate a RAG (Retrieval Augmented Generation) workflow."""
        mock_session = Mock()
        mock_get_session.return_value = mock_session

        # Mock knowledge base recall
        recall_response = MockResponse({
            "memories": [
                {
                    "id": "kb-1",
                    "text": "RecallBricks provides persistent memory for AI agents using a cognitive graph architecture.",
                    "score": 0.98,
                    "metadata": {
                        "tags": ["product", "architecture"],
                        "category": "Technical Documentation",
                        "importance": 1.0,
                        "entities": ["RecallBricks", "AI agents", "cognitive graph"]
                    }
                },
                {
                    "id": "kb-2",
                    "text": "The learn() endpoint automatically extracts metadata including tags, categories, and entities.",
                    "score": 0.92,
                    "metadata": {
                        "tags": ["api", "features"],
                        "category": "API Reference",
                        "importance": 0.9,
                        "entities": ["learn endpoint", "metadata"]
                    }
                }
            ],
            "categories": {
                "Technical Documentation": {"summary": "Core architecture docs", "count": 1, "avg_score": 0.98},
                "API Reference": {"summary": "API endpoint documentation", "count": 1, "avg_score": 0.92}
            }
        })
        mock_session.post.return_value = recall_response

        # Initialize retriever for RAG
        retriever = RecallBricksRetriever(
            api_key=self.api_key,
            k=5,
            organized=True,
            enable_logging=False
        )

        # User question
        question = "How does RecallBricks store memories?"

        # Retrieve relevant documents
        docs = retriever._get_relevant_documents(question)

        # Verify documents were retrieved
        self.assertEqual(len(docs), 2)
        self.assertIn("cognitive graph", docs[0].page_content)

        # Get documents with categories for enhanced prompting
        result = retriever.get_relevant_documents_with_categories(question)

        self.assertIn("categories", result)
        self.assertIn("Technical Documentation", result["categories"])

        print("RAG workflow: PASSED")


def run_all_tests():
    """Run all simulation tests and report results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestRecallBricksMemorySimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestRecallBricksChatMessageHistorySimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestRecallBricksRetrieverSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestRecallBricksClientSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilitiesSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandlingSimulation))
    suite.addTests(loader.loadTestsFromTestCase(TestEndToEndSimulation))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print("SDK SIMULATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\nALL TESTS PASSED - SDK is working as designed!")
    else:
        print("\nSOME TESTS FAILED - Please review the output above.")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split(chr(10))[0]}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split(chr(10))[0]}")

    return result.wasSuccessful()


if __name__ == '__main__':
    run_all_tests()
