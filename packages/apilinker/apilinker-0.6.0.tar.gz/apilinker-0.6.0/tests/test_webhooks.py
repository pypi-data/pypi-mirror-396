"""
Tests for the Webhook Connectors module.
"""

import hashlib
import hmac
import json
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import pytest

from apilinker.core.webhooks import (
    SignatureType,
    WebhookStatus,
    WebhookEndpoint,
    WebhookEvent,
    WebhookConfig,
    WebhookDeliveryResult,
    HMACVerifier,
    WebhookEventFilter,
    WebhookRouter,
    WebhookRetryManager,
    WebhookReplayManager,
    get_verifier,
)


class TestWebhookModels:
    """Tests for webhook Pydantic models."""

    def test_webhook_endpoint_creation(self) -> None:
        """Test WebhookEndpoint creation with defaults."""
        endpoint = WebhookEndpoint(path="/hooks/github")

        assert endpoint.path == "/hooks/github"
        assert endpoint.name == "hooks_github"
        assert endpoint.signature_type == SignatureType.NONE
        assert endpoint.methods == ["POST"]
        assert endpoint.enabled is True

    def test_webhook_endpoint_with_signature(self) -> None:
        """Test WebhookEndpoint with signature verification."""
        endpoint = WebhookEndpoint(
            path="/webhooks/stripe",
            name="stripe_webhook",
            secret="whsec_test123",
            signature_type=SignatureType.HMAC_SHA256,
            signature_header="Stripe-Signature",
            methods=["POST"],
        )

        assert endpoint.name == "stripe_webhook"
        assert endpoint.secret == "whsec_test123"
        assert endpoint.signature_type == SignatureType.HMAC_SHA256
        assert endpoint.signature_header == "Stripe-Signature"

    def test_webhook_event_creation(self) -> None:
        """Test WebhookEvent creation."""
        event = WebhookEvent(
            endpoint_path="/hooks/test",
            endpoint_name="test_hook",
            method="POST",
            headers={"content-type": "application/json"},
            payload={"action": "test"},
        )

        assert event.endpoint_path == "/hooks/test"
        assert event.method == "POST"
        assert event.status == WebhookStatus.PENDING
        assert event.processing_attempts == 0
        assert event.id is not None

    def test_webhook_config_defaults(self) -> None:
        """Test WebhookConfig default values."""
        config = WebhookConfig()

        assert config.host == "0.0.0.0"
        assert config.port == 8000
        assert config.max_retry_attempts == 3
        assert config.retry_delay_seconds == 1.0
        assert config.event_history_size == 1000

    def test_webhook_delivery_result(self) -> None:
        """Test WebhookDeliveryResult creation."""
        result = WebhookDeliveryResult(
            event_id="test-123",
            success=True,
            message="Processed successfully",
            processing_time_ms=50.5,
        )

        assert result.event_id == "test-123"
        assert result.success is True
        assert result.processing_time_ms == 50.5


class TestSignatureVerification:
    """Tests for webhook signature verification."""

    def test_hmac_sha256_verification(self) -> None:
        """Test HMAC-SHA256 signature verification."""
        verifier = HMACVerifier("sha256")
        secret = "my_secret_key"
        payload = b'{"test": "data"}'

        # Generate valid signature
        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()

        # Test with sha256= prefix (GitHub style)
        assert verifier.verify(payload, f"sha256={expected}", secret) is True

        # Test without prefix
        assert verifier.verify(payload, expected, secret) is True

        # Test invalid signature
        assert verifier.verify(payload, "invalid_signature", secret) is False

    def test_hmac_sha1_verification(self) -> None:
        """Test HMAC-SHA1 signature verification."""
        verifier = HMACVerifier("sha1")
        secret = "secret123"
        payload = b"test payload"

        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha1,
        ).hexdigest()

        assert verifier.verify(payload, f"sha1={expected}", secret) is True
        assert verifier.verify(payload, expected, secret) is True

    def test_hmac_algorithm_mismatch(self) -> None:
        """Test that algorithm mismatch is handled."""
        verifier = HMACVerifier("sha256")
        secret = "secret"
        payload = b"test"

        # Generate SHA-1 signature but try to verify with SHA-256 verifier
        sha1_sig = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha1,
        ).hexdigest()

        # Should fail because algorithm prefix doesn't match
        assert verifier.verify(payload, f"sha1={sha1_sig}", secret) is False

    def test_empty_signature_or_secret(self) -> None:
        """Test that empty signature or secret returns False."""
        verifier = HMACVerifier("sha256")

        assert verifier.verify(b"test", "", "secret") is False
        assert verifier.verify(b"test", "signature", "") is False

    def test_get_verifier_factory(self) -> None:
        """Test get_verifier factory function."""
        assert get_verifier(SignatureType.NONE) is None
        assert isinstance(get_verifier(SignatureType.HMAC_SHA256), HMACVerifier)
        assert isinstance(get_verifier(SignatureType.HMAC_SHA1), HMACVerifier)


class TestWebhookEventFilter:
    """Tests for webhook event filtering."""

    def test_filter_by_endpoint_path(self) -> None:
        """Test filtering by endpoint path."""
        filter_ = WebhookEventFilter(endpoint_paths=["/hooks/github"])

        event_match = WebhookEvent(
            endpoint_path="/hooks/github",
            payload={},
        )
        event_no_match = WebhookEvent(
            endpoint_path="/hooks/stripe",
            payload={},
        )

        assert filter_.matches(event_match) is True
        assert filter_.matches(event_no_match) is False

    def test_filter_by_endpoint_wildcard(self) -> None:
        """Test filtering with wildcard patterns."""
        filter_ = WebhookEventFilter(endpoint_paths=["/hooks/*"])

        event1 = WebhookEvent(endpoint_path="/hooks/github", payload={})
        event2 = WebhookEvent(endpoint_path="/hooks/stripe", payload={})
        event3 = WebhookEvent(endpoint_path="/api/webhooks", payload={})

        assert filter_.matches(event1) is True
        assert filter_.matches(event2) is True
        assert filter_.matches(event3) is False

    def test_filter_by_method(self) -> None:
        """Test filtering by HTTP method."""
        filter_ = WebhookEventFilter(methods=["POST", "PUT"])

        event_post = WebhookEvent(
            endpoint_path="/hooks/test",
            method="POST",
            payload={},
        )
        event_get = WebhookEvent(
            endpoint_path="/hooks/test",
            method="GET",
            payload={},
        )

        assert filter_.matches(event_post) is True
        assert filter_.matches(event_get) is False

    def test_filter_by_header_pattern(self) -> None:
        """Test filtering by header patterns."""
        filter_ = WebhookEventFilter(
            header_patterns={"x-github-event": "push|pull_request"}
        )

        event_push = WebhookEvent(
            endpoint_path="/hooks/test",
            headers={"X-GitHub-Event": "push"},
            payload={},
        )
        event_issue = WebhookEvent(
            endpoint_path="/hooks/test",
            headers={"X-GitHub-Event": "issues"},
            payload={},
        )

        assert filter_.matches(event_push) is True
        assert filter_.matches(event_issue) is False

    def test_filter_by_payload_pattern(self) -> None:
        """Test filtering by payload patterns."""
        filter_ = WebhookEventFilter(
            payload_patterns={"action": "opened", "repository.name": ".*"}
        )

        event_match = WebhookEvent(
            endpoint_path="/hooks/test",
            payload={
                "action": "opened",
                "repository": {"name": "test-repo"},
            },
        )
        event_no_match = WebhookEvent(
            endpoint_path="/hooks/test",
            payload={"action": "closed"},
        )

        assert filter_.matches(event_match) is True
        assert filter_.matches(event_no_match) is False

    def test_filter_matches_all(self) -> None:
        """Test that empty filter matches all events."""
        filter_ = WebhookEventFilter()

        event = WebhookEvent(
            endpoint_path="/any/path",
            method="DELETE",
            payload={"anything": "here"},
        )

        assert filter_.matches(event) is True


class TestWebhookRouter:
    """Tests for webhook event routing."""

    def test_add_and_route(self) -> None:
        """Test adding routes and routing events."""
        router = WebhookRouter()

        handler1 = Mock(return_value={"result": 1})
        handler2 = Mock(return_value={"result": 2})

        # Add routes
        router.add_route(
            WebhookEventFilter(endpoint_paths=["/hooks/github"]),
            handler1,
            name="github_handler",
        )
        router.add_route(
            WebhookEventFilter(endpoint_paths=["/hooks/stripe"]),
            handler2,
            name="stripe_handler",
        )

        # Route event
        event = WebhookEvent(endpoint_path="/hooks/github", payload={})
        handlers = router.route(event)

        assert len(handlers) == 1
        assert handlers[0][0] == "github_handler"

    def test_route_multiple_handlers(self) -> None:
        """Test routing to multiple matching handlers."""
        router = WebhookRouter()

        handler1 = Mock()
        handler2 = Mock()

        # Both handlers match all events
        router.add_route(WebhookEventFilter(), handler1, name="handler1")
        router.add_route(WebhookEventFilter(), handler2, name="handler2")

        event = WebhookEvent(endpoint_path="/any", payload={})
        handlers = router.route(event)

        assert len(handlers) == 2

    def test_remove_route(self) -> None:
        """Test removing a route."""
        router = WebhookRouter()

        handler = Mock()
        router.add_route(WebhookEventFilter(), handler, name="to_remove")

        assert router.remove_route("to_remove") is True
        assert router.remove_route("nonexistent") is False

        # Verify no handlers match after removal
        event = WebhookEvent(endpoint_path="/test", payload={})
        handlers = router.route(event)
        assert len(handlers) == 0


class TestWebhookRetryManager:
    """Tests for webhook retry management."""

    def test_should_retry(self) -> None:
        """Test retry eligibility check."""
        manager = WebhookRetryManager(max_attempts=3)

        event = WebhookEvent(endpoint_path="/test", payload={})

        assert manager.should_retry(event) is True

        event.processing_attempts = 3
        assert manager.should_retry(event) is False

    def test_get_retry_delay(self) -> None:
        """Test exponential backoff calculation."""
        manager = WebhookRetryManager(
            initial_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=60.0,
        )

        assert manager.get_retry_delay(1) == 1.0
        assert manager.get_retry_delay(2) == 2.0
        assert manager.get_retry_delay(3) == 4.0
        assert manager.get_retry_delay(4) == 8.0

        # Test max delay cap
        assert manager.get_retry_delay(10) == 60.0  # Capped at max_delay

    def test_schedule_retry(self) -> None:
        """Test scheduling an event for retry."""
        manager = WebhookRetryManager(max_attempts=3, initial_delay=0.1)

        event = WebhookEvent(endpoint_path="/test", payload={})

        assert manager.schedule_retry(event) is True
        assert event.status == WebhookStatus.RETRYING
        assert manager.pending_count() == 1

    def test_schedule_retry_max_exceeded(self) -> None:
        """Test that retry is rejected when max attempts exceeded."""
        manager = WebhookRetryManager(max_attempts=2)

        event = WebhookEvent(endpoint_path="/test", payload={})
        event.processing_attempts = 2

        assert manager.schedule_retry(event) is False
        assert manager.pending_count() == 0

    def test_get_due_events(self) -> None:
        """Test retrieving events that are due for retry."""
        manager = WebhookRetryManager(initial_delay=0.01)

        event = WebhookEvent(endpoint_path="/test", payload={})
        manager.schedule_retry(event)

        # Wait for the event to become due
        time.sleep(0.05)

        due = manager.get_due_events()
        assert len(due) == 1
        assert due[0].id == event.id
        assert manager.pending_count() == 0


class TestWebhookReplayManager:
    """Tests for webhook replay management."""

    def test_store_and_get(self) -> None:
        """Test storing and retrieving events."""
        manager = WebhookReplayManager()

        event = WebhookEvent(
            endpoint_path="/test",
            payload={"data": "test"},
        )
        manager.store(event)

        retrieved = manager.get_event(event.id)
        assert retrieved is not None
        assert retrieved.id == event.id
        assert retrieved.payload == {"data": "test"}

    def test_get_history(self) -> None:
        """Test getting event history with filters."""
        manager = WebhookReplayManager()

        # Store multiple events
        for i in range(5):
            event = WebhookEvent(
                endpoint_path="/test" if i < 3 else "/other",
                payload={"index": i},
            )
            if i % 2 == 0:
                event.status = WebhookStatus.SUCCESS
            else:
                event.status = WebhookStatus.FAILED
            manager.store(event)

        # Test filtering by endpoint
        history = manager.get_history(endpoint_path="/test")
        assert len(history) == 3

        # Test filtering by status
        history = manager.get_history(status=WebhookStatus.SUCCESS)
        assert len(history) == 3

        # Test limit
        history = manager.get_history(limit=2)
        assert len(history) == 2

    def test_replay(self) -> None:
        """Test replaying an event."""
        manager = WebhookReplayManager()

        original = WebhookEvent(
            endpoint_path="/test",
            payload={"original": True},
        )
        original.status = WebhookStatus.FAILED
        original.processing_attempts = 3
        manager.store(original)

        # Replay the event
        replayed = manager.replay(original.id)

        assert replayed is not None
        assert replayed.id != original.id  # New ID
        assert replayed.payload == original.payload
        assert replayed.status == WebhookStatus.PENDING
        assert replayed.processing_attempts == 0

    def test_replay_nonexistent(self) -> None:
        """Test replaying a nonexistent event."""
        manager = WebhookReplayManager()

        result = manager.replay("nonexistent-id")
        assert result is None

    def test_history_size_limit(self) -> None:
        """Test that history is trimmed when limit exceeded."""
        manager = WebhookReplayManager(max_history_size=5)

        for i in range(10):
            event = WebhookEvent(
                endpoint_path="/test",
                payload={"index": i},
            )
            manager.store(event)

        history = manager.get_history(limit=100)
        assert len(history) == 5
        # Should have the most recent events
        assert history[0].payload["index"] == 9
        assert history[4].payload["index"] == 5

    def test_clear_history(self) -> None:
        """Test clearing event history."""
        manager = WebhookReplayManager()

        for i in range(5):
            manager.store(WebhookEvent(endpoint_path="/test", payload={}))

        count = manager.clear_history()
        assert count == 5
        assert len(manager.get_history()) == 0


class TestWebhookServerMocked:
    """Tests for WebhookServer with mocked FastAPI."""

    @patch("apilinker.core.webhooks.FASTAPI_AVAILABLE", True)
    @patch("apilinker.core.webhooks.FastAPI")
    @patch("apilinker.core.webhooks.uvicorn")
    def test_server_initialization(
        self, mock_uvicorn: MagicMock, mock_fastapi: MagicMock
    ) -> None:
        """Test server initialization."""
        from apilinker.core.webhooks import WebhookServer

        mock_app = MagicMock()
        mock_fastapi.return_value = mock_app

        server = WebhookServer(host="127.0.0.1", port=9000)

        assert server.host == "127.0.0.1"
        assert server.port == 9000
        mock_fastapi.assert_called_once()

    @patch("apilinker.core.webhooks.FASTAPI_AVAILABLE", True)
    @patch("apilinker.core.webhooks.FastAPI")
    @patch("apilinker.core.webhooks.uvicorn")
    def test_register_endpoint(
        self, mock_uvicorn: MagicMock, mock_fastapi: MagicMock
    ) -> None:
        """Test endpoint registration."""
        from apilinker.core.webhooks import WebhookServer

        mock_app = MagicMock()
        mock_fastapi.return_value = mock_app

        server = WebhookServer()

        endpoint = WebhookEndpoint(
            path="/hooks/test",
            methods=["POST", "PUT"],
        )
        server.register_endpoint(endpoint)

        # Verify route was added for each method
        assert mock_app.add_api_route.call_count == 2


class TestWebhookManagerMocked:
    """Tests for WebhookManager with mocked server."""

    @patch("apilinker.core.webhooks.FASTAPI_AVAILABLE", True)
    @patch("apilinker.core.webhooks.WebhookServer")
    def test_manager_initialization(self, mock_server_class: MagicMock) -> None:
        """Test manager initialization."""
        from apilinker.core.webhooks import WebhookManager, WebhookConfig

        config = WebhookConfig(
            host="127.0.0.1",
            port=9000,
            max_retry_attempts=5,
        )
        manager = WebhookManager(config)

        assert manager.config.host == "127.0.0.1"
        assert manager.config.port == 9000
        assert manager.retry_manager.max_attempts == 5

    def test_add_handler(self) -> None:
        """Test adding event handlers."""
        from apilinker.core.webhooks import WebhookManager

        manager = WebhookManager()

        handler = Mock()
        manager.add_handler(handler, name="test_handler")

        # Verify handler was added to router
        event = WebhookEvent(endpoint_path="/test", payload={})
        handlers = manager.router.route(event)
        assert len(handlers) == 1

    @patch("apilinker.core.webhooks.FASTAPI_AVAILABLE", True)
    @patch("apilinker.core.webhooks.WebhookServer")
    def test_start_and_stop(self, mock_server_class: MagicMock) -> None:
        """Test starting and stopping the manager."""
        from apilinker.core.webhooks import WebhookManager

        mock_server = MagicMock()
        mock_server_class.return_value = mock_server

        manager = WebhookManager()
        manager.start(blocking=False)

        mock_server.start.assert_called_once_with(blocking=False)

        manager.stop()
        mock_server.stop.assert_called_once()

    def test_event_history(self) -> None:
        """Test getting event history."""
        from apilinker.core.webhooks import WebhookManager

        manager = WebhookManager()

        # Manually add events to replay manager for testing
        for i in range(3):
            event = WebhookEvent(
                endpoint_path="/test",
                payload={"i": i},
            )
            manager.replay_manager.store(event)

        history = manager.get_event_history(limit=10)
        assert len(history) == 3
