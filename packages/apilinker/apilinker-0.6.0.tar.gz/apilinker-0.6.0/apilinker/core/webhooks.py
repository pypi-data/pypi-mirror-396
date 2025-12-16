"""
Webhook Connectors module for APILinker.

Provides first-class support for receiving webhooks and triggering syncs.
Features include:
- HTTP webhook server/listener (FastAPI-based)
- Webhook endpoint registration and management
- Event filtering and routing
- Signature verification (HMAC, JWT)
- Webhook replay and retry mechanisms
- Webhook-to-API mapping
- Configurable webhook endpoints
"""

import hashlib
import hmac
import json
import logging
import threading
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import re

from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

# Check for optional FastAPI dependency
try:
    from fastapi import FastAPI, Request, Response, HTTPException
    from fastapi.responses import JSONResponse
    import uvicorn

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None  # type: ignore
    Request = None  # type: ignore
    Response = None  # type: ignore
    HTTPException = None  # type: ignore
    JSONResponse = None  # type: ignore
    uvicorn = None  # type: ignore

# Check for optional JWT dependency
try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None  # type: ignore


class SignatureType(str, Enum):
    """Supported signature verification types."""

    NONE = "none"
    HMAC_SHA256 = "hmac_sha256"
    HMAC_SHA1 = "hmac_sha1"
    JWT = "jwt"


class WebhookStatus(str, Enum):
    """Status of a webhook event processing."""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookEndpoint(BaseModel):
    """Configuration for a webhook endpoint."""

    path: str = Field(..., description="URL path for the webhook endpoint")
    name: Optional[str] = Field(
        default=None, description="Human-readable name for the endpoint"
    )
    secret: Optional[str] = Field(
        default=None, description="Secret key for signature verification"
    )
    signature_type: SignatureType = Field(
        default=SignatureType.NONE, description="Type of signature verification"
    )
    signature_header: str = Field(
        default="X-Hub-Signature-256",
        description="Header containing the signature",
    )
    methods: List[str] = Field(
        default_factory=lambda: ["POST"], description="Allowed HTTP methods"
    )
    enabled: bool = Field(default=True, description="Whether the endpoint is enabled")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional endpoint metadata"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if self.name is None:
            # Generate name from path
            object.__setattr__(
                self, "name", self.path.strip("/").replace("/", "_") or "root"
            )


class WebhookEvent(BaseModel):
    """Represents a received webhook event."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_path: str = Field(..., description="Path of the endpoint that received it")
    endpoint_name: Optional[str] = Field(
        default=None, description="Name of the endpoint"
    )
    method: str = Field(default="POST", description="HTTP method used")
    headers: Dict[str, str] = Field(default_factory=dict, description="Request headers")
    payload: Any = Field(default=None, description="Request payload")
    raw_body: Optional[bytes] = Field(
        default=None, description="Raw request body for signature verification"
    )
    query_params: Dict[str, str] = Field(
        default_factory=dict, description="Query parameters"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: WebhookStatus = Field(default=WebhookStatus.PENDING)
    processing_attempts: int = Field(default=0)
    last_error: Optional[str] = Field(default=None)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WebhookDeliveryResult(BaseModel):
    """Result of processing a webhook delivery."""

    event_id: str
    success: bool
    message: str = ""
    handler_results: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(arbitrary_types_allowed=True)


class WebhookConfig(BaseModel):
    """Global webhook server configuration."""

    host: str = Field(default="0.0.0.0", description="Host to bind the server to")
    port: int = Field(default=8000, description="Port to listen on")
    endpoints: List[WebhookEndpoint] = Field(
        default_factory=list, description="Registered webhook endpoints"
    )
    max_retry_attempts: int = Field(
        default=3, description="Maximum retry attempts for failed events"
    )
    retry_delay_seconds: float = Field(
        default=1.0, description="Initial retry delay in seconds"
    )
    retry_backoff_multiplier: float = Field(
        default=2.0, description="Backoff multiplier for retry delays"
    )
    event_history_size: int = Field(
        default=1000, description="Maximum number of events to keep in history"
    )
    request_timeout_seconds: float = Field(
        default=30.0, description="Timeout for processing webhook requests"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


# =============================================================================
# Signature Verification
# =============================================================================


class SignatureVerifier(ABC):
    """Base class for webhook signature verification."""

    @abstractmethod
    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verify the signature of a webhook payload.

        Args:
            payload: Raw request body
            signature: Signature from the request header
            secret: Secret key for verification

        Returns:
            True if signature is valid, False otherwise
        """
        pass


class HMACVerifier(SignatureVerifier):
    """HMAC signature verifier supporting SHA-256 and SHA-1."""

    def __init__(self, algorithm: str = "sha256"):
        """
        Initialize HMAC verifier.

        Args:
            algorithm: Hash algorithm to use (sha256 or sha1)
        """
        if algorithm not in ("sha256", "sha1"):
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        self.algorithm = algorithm
        self._hash_func = hashlib.sha256 if algorithm == "sha256" else hashlib.sha1

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify HMAC signature."""
        if not signature or not secret:
            return False

        # Handle different signature formats
        # GitHub: sha256=<signature> or sha1=<signature>
        # Stripe: similar format
        sig_parts = signature.split("=", 1)
        if len(sig_parts) == 2:
            prefix, sig_value = sig_parts
            # Verify algorithm matches if specified
            if prefix in ("sha256", "sha1") and prefix != self.algorithm:
                logger.warning(
                    f"Signature algorithm mismatch: expected {self.algorithm}, "
                    f"got {prefix}"
                )
                return False
            signature = sig_value
        else:
            signature = sig_parts[0]

        # Compute expected signature
        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            self._hash_func,
        ).hexdigest()

        # Constant-time comparison to prevent timing attacks
        return hmac.compare_digest(expected.lower(), signature.lower())


class JWTVerifier(SignatureVerifier):
    """JWT token verifier."""

    def __init__(
        self,
        algorithms: Optional[List[str]] = None,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
    ):
        """
        Initialize JWT verifier.

        Args:
            algorithms: Allowed JWT algorithms (default: HS256)
            issuer: Expected token issuer
            audience: Expected token audience
        """
        if not JWT_AVAILABLE:
            raise ImportError(
                "PyJWT is required for JWT verification. "
                "Install with: pip install pyjwt"
            )
        self.algorithms = algorithms or ["HS256"]
        self.issuer = issuer
        self.audience = audience

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify JWT token."""
        if not signature or not secret:
            return False

        # Handle Bearer prefix
        if signature.startswith("Bearer "):
            signature = signature[7:]

        try:
            options: Dict[str, Any] = {}
            if self.issuer:
                options["iss"] = self.issuer
            if self.audience:
                options["aud"] = self.audience

            jwt.decode(  # type: ignore
                signature,
                secret,
                algorithms=self.algorithms,
                options={"verify_signature": True},
            )
            return True
        except Exception as e:
            logger.debug(f"JWT verification failed: {e}")
            return False


def get_verifier(signature_type: SignatureType) -> Optional[SignatureVerifier]:
    """
    Get the appropriate signature verifier for the given type.

    Args:
        signature_type: Type of signature verification

    Returns:
        SignatureVerifier instance or None if no verification needed
    """
    if signature_type == SignatureType.NONE:
        return None
    elif signature_type == SignatureType.HMAC_SHA256:
        return HMACVerifier("sha256")
    elif signature_type == SignatureType.HMAC_SHA1:
        return HMACVerifier("sha1")
    elif signature_type == SignatureType.JWT:
        return JWTVerifier()
    else:
        raise ValueError(f"Unsupported signature type: {signature_type}")


# =============================================================================
# Event Filtering
# =============================================================================


class WebhookEventFilter:
    """Filter webhook events based on patterns."""

    def __init__(
        self,
        endpoint_paths: Optional[List[str]] = None,
        methods: Optional[List[str]] = None,
        header_patterns: Optional[Dict[str, str]] = None,
        payload_patterns: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize event filter.

        Args:
            endpoint_paths: List of endpoint paths to match (supports wildcards)
            methods: List of HTTP methods to match
            header_patterns: Header patterns to match (regex supported)
            payload_patterns: JSON path patterns to match in payload
        """
        self.endpoint_paths = endpoint_paths
        self.methods = [m.upper() for m in methods] if methods else None
        self.header_patterns = header_patterns or {}
        self.payload_patterns = payload_patterns or {}

        # Compile header patterns
        self._compiled_headers: Dict[str, "re.Pattern[str]"] = {}
        for key, pattern in self.header_patterns.items():
            self._compiled_headers[key.lower()] = re.compile(pattern)

    def matches(self, event: WebhookEvent) -> bool:
        """
        Check if an event matches this filter.

        Args:
            event: Webhook event to check

        Returns:
            True if event matches all filter criteria
        """
        # Check endpoint path
        if self.endpoint_paths:
            path_matched = False
            for path_pattern in self.endpoint_paths:
                if self._match_path(event.endpoint_path, path_pattern):
                    path_matched = True
                    break
            if not path_matched:
                return False

        # Check method
        if self.methods and event.method.upper() not in self.methods:
            return False

        # Check headers
        lower_headers = {k.lower(): v for k, v in event.headers.items()}
        for header_key, pattern in self._compiled_headers.items():
            header_value = lower_headers.get(header_key, "")
            if not pattern.match(header_value):
                return False

        # Check payload patterns
        if self.payload_patterns and event.payload:
            for json_path, expected_value in self.payload_patterns.items():
                actual_value = self._get_json_path(event.payload, json_path)
                if not self._match_value(actual_value, expected_value):
                    return False

        return True

    def _match_path(self, path: str, pattern: str) -> bool:
        """Match path against pattern with wildcard support."""
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace("*", ".*").replace("?", ".")
        if not regex_pattern.startswith("^"):
            regex_pattern = "^" + regex_pattern
        if not regex_pattern.endswith("$"):
            regex_pattern = regex_pattern + "$"
        return bool(re.match(regex_pattern, path))

    def _get_json_path(self, data: Any, path: str) -> Any:
        """Get value from nested dictionary using dot notation."""
        keys = path.split(".")
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                idx = int(key)
                current = current[idx] if 0 <= idx < len(current) else None
            else:
                return None
            if current is None:
                return None
        return current

    def _match_value(self, actual: Any, expected: Any) -> bool:
        """Match actual value against expected (supports regex for strings)."""
        if actual is None:
            return expected is None
        if isinstance(expected, str) and isinstance(actual, str):
            # Try regex match
            try:
                return bool(re.match(expected, actual))
            except re.error:
                return actual == expected
        return actual == expected


# =============================================================================
# Event Routing
# =============================================================================


WebhookHandler = Callable[[WebhookEvent], Optional[Dict[str, Any]]]


class WebhookRouter:
    """Route webhook events to appropriate handlers."""

    def __init__(self) -> None:
        """Initialize the webhook router."""
        self._routes: List[tuple[WebhookEventFilter, str, WebhookHandler]] = []

    def add_route(
        self,
        filter_: WebhookEventFilter,
        handler: WebhookHandler,
        name: Optional[str] = None,
    ) -> None:
        """
        Add a route for webhook events.

        Args:
            filter_: Filter to match events
            handler: Handler function for matched events
            name: Optional name for the route
        """
        route_name = name or f"route_{len(self._routes)}"
        self._routes.append((filter_, route_name, handler))
        logger.debug(f"Added webhook route: {route_name}")

    def route(self, event: WebhookEvent) -> List[tuple[str, WebhookHandler]]:
        """
        Find all matching handlers for an event.

        Args:
            event: Webhook event to route

        Returns:
            List of (route_name, handler) tuples
        """
        matching_handlers = []
        for filter_, name, handler in self._routes:
            if filter_.matches(event):
                matching_handlers.append((name, handler))
        return matching_handlers

    def remove_route(self, name: str) -> bool:
        """
        Remove a route by name.

        Args:
            name: Name of the route to remove

        Returns:
            True if route was removed, False if not found
        """
        for i, (_, route_name, _) in enumerate(self._routes):
            if route_name == name:
                self._routes.pop(i)
                logger.debug(f"Removed webhook route: {name}")
                return True
        return False


# =============================================================================
# Retry Manager
# =============================================================================


class WebhookRetryManager:
    """Manage retry logic for failed webhook processing."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_delay: float = 60.0,
    ):
        """
        Initialize retry manager.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            backoff_multiplier: Multiplier for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.backoff_multiplier = backoff_multiplier
        self.max_delay = max_delay
        self._retry_queue: List[tuple[WebhookEvent, float]] = []
        self._lock = threading.Lock()

    def should_retry(self, event: WebhookEvent) -> bool:
        """Check if an event should be retried."""
        return event.processing_attempts < self.max_attempts

    def get_retry_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt."""
        delay = self.initial_delay * (self.backoff_multiplier ** (attempt - 1))
        return min(delay, self.max_delay)

    def schedule_retry(self, event: WebhookEvent) -> bool:
        """
        Schedule an event for retry.

        Args:
            event: Event to retry

        Returns:
            True if scheduled, False if max attempts reached
        """
        if not self.should_retry(event):
            logger.warning(
                f"Event {event.id} exceeded max retry attempts "
                f"({self.max_attempts})"
            )
            return False

        delay = self.get_retry_delay(event.processing_attempts)
        retry_time = time.time() + delay

        with self._lock:
            event.status = WebhookStatus.RETRYING
            self._retry_queue.append((event, retry_time))
            self._retry_queue.sort(key=lambda x: x[1])

        logger.info(
            f"Scheduled event {event.id} for retry in {delay:.1f}s "
            f"(attempt {event.processing_attempts + 1}/{self.max_attempts})"
        )
        return True

    def get_due_events(self) -> List[WebhookEvent]:
        """Get all events that are due for retry."""
        current_time = time.time()
        due_events = []

        with self._lock:
            while self._retry_queue and self._retry_queue[0][1] <= current_time:
                event, _ = self._retry_queue.pop(0)
                due_events.append(event)

        return due_events

    def pending_count(self) -> int:
        """Get the number of pending retries."""
        with self._lock:
            return len(self._retry_queue)


# =============================================================================
# Replay Manager
# =============================================================================


class WebhookReplayManager:
    """Store and replay historical webhook events."""

    def __init__(self, max_history_size: int = 1000):
        """
        Initialize replay manager.

        Args:
            max_history_size: Maximum number of events to store
        """
        self.max_history_size = max_history_size
        self._history: List[WebhookEvent] = []
        self._lock = threading.Lock()

    def store(self, event: WebhookEvent) -> None:
        """Store an event in history."""
        with self._lock:
            self._history.append(event)
            # Trim history if needed
            if len(self._history) > self.max_history_size:
                self._history = self._history[-self.max_history_size :]

    def get_event(self, event_id: str) -> Optional[WebhookEvent]:
        """Get an event by ID."""
        with self._lock:
            for event in self._history:
                if event.id == event_id:
                    return event
        return None

    def get_history(
        self,
        endpoint_path: Optional[str] = None,
        status: Optional[WebhookStatus] = None,
        limit: int = 100,
    ) -> List[WebhookEvent]:
        """
        Get event history with optional filtering.

        Args:
            endpoint_path: Filter by endpoint path
            status: Filter by event status
            limit: Maximum number of events to return

        Returns:
            List of matching events (most recent first)
        """
        with self._lock:
            result = list(reversed(self._history))

        if endpoint_path:
            result = [e for e in result if e.endpoint_path == endpoint_path]
        if status:
            result = [e for e in result if e.status == status]

        return result[:limit]

    def replay(self, event_id: str) -> Optional[WebhookEvent]:
        """
        Create a copy of an event for replay.

        Args:
            event_id: ID of the event to replay

        Returns:
            New event instance with reset status, or None if not found
        """
        original = self.get_event(event_id)
        if not original:
            return None

        # Create a new event with the same payload but new ID and reset status
        replay_event = WebhookEvent(
            endpoint_path=original.endpoint_path,
            endpoint_name=original.endpoint_name,
            method=original.method,
            headers=original.headers.copy(),
            payload=original.payload,
            raw_body=original.raw_body,
            query_params=original.query_params.copy(),
            status=WebhookStatus.PENDING,
            processing_attempts=0,
        )
        return replay_event

    def clear_history(self) -> int:
        """Clear all event history."""
        with self._lock:
            count = len(self._history)
            self._history.clear()
        return count


# =============================================================================
# Webhook Server
# =============================================================================


class WebhookServer:
    """FastAPI-based webhook server."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8000,
        title: str = "APILinker Webhook Server",
    ):
        """
        Initialize webhook server.

        Args:
            host: Host to bind to
            port: Port to listen on
            title: Server title for OpenAPI docs
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI and uvicorn are required for the webhook server. "
                "Install with: pip install apilinker[webhooks]"
            )

        self.host = host
        self.port = port
        self._app = FastAPI(title=title)
        self._endpoints: Dict[str, WebhookEndpoint] = {}
        self._event_handlers: List[Callable[[WebhookEvent], None]] = []
        self._server: Optional[Any] = None
        self._server_thread: Optional[threading.Thread] = None

        # Setup default routes
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup default server routes."""

        @self._app.get("/health")
        async def health_check() -> Dict[str, str]:
            return {"status": "healthy", "service": "webhook-server"}

        @self._app.get("/endpoints")
        async def list_endpoints() -> Dict[str, Any]:
            return {
                "endpoints": [
                    {
                        "path": ep.path,
                        "name": ep.name,
                        "methods": ep.methods,
                        "enabled": ep.enabled,
                        "signature_type": ep.signature_type.value,
                    }
                    for ep in self._endpoints.values()
                ]
            }

    def register_endpoint(self, endpoint: WebhookEndpoint) -> None:
        """
        Register a webhook endpoint.

        Args:
            endpoint: Endpoint configuration
        """
        if endpoint.path in self._endpoints:
            logger.warning(f"Replacing existing endpoint: {endpoint.path}")

        self._endpoints[endpoint.path] = endpoint

        # Create route handler
        async def handle_webhook(
            request: Request,
            path: str = endpoint.path,
        ) -> Response:
            return await self._handle_request(request, path)

        # Register route for all configured methods
        for method in endpoint.methods:
            route_path = endpoint.path
            self._app.add_api_route(
                route_path,
                handle_webhook,
                methods=[method],
                name=f"webhook_{endpoint.name}",
            )

        logger.info(
            f"Registered webhook endpoint: {endpoint.path} "
            f"(methods: {endpoint.methods})"
        )

    async def _handle_request(self, request: Request, endpoint_path: str) -> Response:
        """Handle incoming webhook request."""
        endpoint = self._endpoints.get(endpoint_path)
        if not endpoint:
            raise HTTPException(status_code=404, detail="Endpoint not found")

        if not endpoint.enabled:
            raise HTTPException(status_code=503, detail="Endpoint disabled")

        # Read raw body
        raw_body = await request.body()

        # Get headers
        headers = dict(request.headers)

        # Verify signature if required
        if endpoint.signature_type != SignatureType.NONE:
            signature = headers.get(endpoint.signature_header.lower(), "")
            if not signature:
                raise HTTPException(
                    status_code=401,
                    detail=f"Missing signature header: {endpoint.signature_header}",
                )

            verifier = get_verifier(endpoint.signature_type)
            if verifier and endpoint.secret:
                if not verifier.verify(raw_body, signature, endpoint.secret):
                    raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse payload
        try:
            if raw_body:
                content_type = headers.get("content-type", "")
                if "application/json" in content_type:
                    payload = json.loads(raw_body)
                else:
                    payload = raw_body.decode("utf-8")
            else:
                payload = None
        except Exception as e:
            logger.warning(f"Failed to parse payload: {e}")
            payload = raw_body.decode("utf-8", errors="replace")

        # Create event
        event = WebhookEvent(
            endpoint_path=endpoint_path,
            endpoint_name=endpoint.name,
            method=request.method,
            headers=headers,
            payload=payload,
            raw_body=raw_body,
            query_params=dict(request.query_params),
        )

        # Notify handlers
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

        return JSONResponse(
            content={
                "status": "received",
                "event_id": event.id,
                "timestamp": event.timestamp.isoformat(),
            },
            status_code=200,
        )

    def add_event_handler(self, handler: Callable[[WebhookEvent], None]) -> None:
        """Add a handler to be called for all incoming events."""
        self._event_handlers.append(handler)

    def start(self, blocking: bool = False) -> None:
        """
        Start the webhook server.

        Args:
            blocking: If True, block until server stops. If False, run in background.
        """
        config = uvicorn.Config(
            app=self._app,
            host=self.host,
            port=self.port,
            log_level="info",
        )
        self._server = uvicorn.Server(config)

        if blocking:
            self._server.run()
        else:
            self._server_thread = threading.Thread(
                target=self._server.run,
                daemon=True,
            )
            self._server_thread.start()
            logger.info(f"Webhook server started on {self.host}:{self.port}")

    def stop(self) -> None:
        """Stop the webhook server."""
        if self._server:
            self._server.should_exit = True
            if self._server_thread:
                self._server_thread.join(timeout=5.0)
            logger.info("Webhook server stopped")

    @property
    def app(self) -> Any:
        """Get the underlying FastAPI app for advanced customization."""
        return self._app


# =============================================================================
# Webhook Manager
# =============================================================================


class WebhookManager:
    """
    Main manager class for webhook connectors.

    Orchestrates the webhook server, event routing, retry management,
    and event replay functionality.
    """

    def __init__(self, config: Optional[WebhookConfig] = None):
        """
        Initialize webhook manager.

        Args:
            config: Webhook configuration (uses defaults if not provided)
        """
        self.config = config or WebhookConfig()
        self._server: Optional[WebhookServer] = None
        self.router = WebhookRouter()
        self.retry_manager = WebhookRetryManager(
            max_attempts=self.config.max_retry_attempts,
            initial_delay=self.config.retry_delay_seconds,
            backoff_multiplier=self.config.retry_backoff_multiplier,
        )
        self.replay_manager = WebhookReplayManager(
            max_history_size=self.config.event_history_size
        )
        self._processing = False
        self._process_thread: Optional[threading.Thread] = None

    def register_endpoint(self, endpoint: WebhookEndpoint) -> None:
        """Register a webhook endpoint."""
        self.config.endpoints.append(endpoint)
        if self._server:
            self._server.register_endpoint(endpoint)

    def add_handler(
        self,
        handler: WebhookHandler,
        filter_: Optional[WebhookEventFilter] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Add an event handler.

        Args:
            handler: Handler function
            filter_: Optional filter (matches all events if not provided)
            name: Optional handler name
        """
        if filter_ is None:
            filter_ = WebhookEventFilter()
        self.router.add_route(filter_, handler, name)

    def start(self, blocking: bool = False) -> None:
        """
        Start the webhook manager and server.

        Args:
            blocking: If True, block until stopped
        """
        # Create and configure server
        self._server = WebhookServer(
            host=self.config.host,
            port=self.config.port,
        )

        # Register configured endpoints
        for endpoint in self.config.endpoints:
            self._server.register_endpoint(endpoint)

        # Add event processing handler
        self._server.add_event_handler(self._on_event_received)

        # Start processing thread
        self._processing = True
        self._process_thread = threading.Thread(
            target=self._process_loop,
            daemon=True,
        )
        self._process_thread.start()

        # Start server
        self._server.start(blocking=blocking)

    def stop(self) -> None:
        """Stop the webhook manager and server."""
        self._processing = False
        if self._process_thread:
            self._process_thread.join(timeout=5.0)
        if self._server:
            self._server.stop()

    def _on_event_received(self, event: WebhookEvent) -> None:
        """Handle incoming webhook event."""
        # Store in history
        self.replay_manager.store(event)

        # Process event
        self._process_event(event)

    def _process_event(self, event: WebhookEvent) -> WebhookDeliveryResult:
        """Process a webhook event through all matching handlers."""
        start_time = time.time()
        event.status = WebhookStatus.PROCESSING
        event.processing_attempts += 1

        handlers = self.router.route(event)
        if not handlers:
            logger.debug(f"No handlers matched event {event.id}")
            event.status = WebhookStatus.SUCCESS
            return WebhookDeliveryResult(
                event_id=event.id,
                success=True,
                message="No handlers matched",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        handler_results: Dict[str, Any] = {}
        all_success = True
        last_error: Optional[str] = None

        for route_name, handler in handlers:
            try:
                result = handler(event)
                handler_results[route_name] = {
                    "success": True,
                    "result": result,
                }
            except Exception as e:
                logger.error(f"Handler {route_name} failed for event {event.id}: {e}")
                handler_results[route_name] = {
                    "success": False,
                    "error": str(e),
                }
                all_success = False
                last_error = str(e)

        processing_time = (time.time() - start_time) * 1000

        if all_success:
            event.status = WebhookStatus.SUCCESS
            return WebhookDeliveryResult(
                event_id=event.id,
                success=True,
                message=f"Processed by {len(handlers)} handler(s)",
                handler_results=handler_results,
                processing_time_ms=processing_time,
            )
        else:
            event.last_error = last_error
            # Schedule retry if possible
            if self.retry_manager.should_retry(event):
                self.retry_manager.schedule_retry(event)
                return WebhookDeliveryResult(
                    event_id=event.id,
                    success=False,
                    message="Processing failed, scheduled for retry",
                    handler_results=handler_results,
                    processing_time_ms=processing_time,
                )
            else:
                event.status = WebhookStatus.FAILED
                return WebhookDeliveryResult(
                    event_id=event.id,
                    success=False,
                    message="Processing failed, max retries exceeded",
                    handler_results=handler_results,
                    processing_time_ms=processing_time,
                )

    def _process_loop(self) -> None:
        """Background loop for processing retries."""
        while self._processing:
            # Process due retries
            due_events = self.retry_manager.get_due_events()
            for event in due_events:
                self._process_event(event)

            # Short sleep to prevent busy waiting
            time.sleep(0.1)

    def replay_event(self, event_id: str) -> Optional[WebhookDeliveryResult]:
        """
        Replay a historical event.

        Args:
            event_id: ID of the event to replay

        Returns:
            Delivery result or None if event not found
        """
        event = self.replay_manager.replay(event_id)
        if not event:
            logger.warning(f"Event not found for replay: {event_id}")
            return None

        # Store the replay event in history
        self.replay_manager.store(event)

        # Process the replayed event
        return self._process_event(event)

    def get_event_history(
        self,
        endpoint_path: Optional[str] = None,
        status: Optional[WebhookStatus] = None,
        limit: int = 100,
    ) -> List[WebhookEvent]:
        """Get event history with optional filtering."""
        return self.replay_manager.get_history(
            endpoint_path=endpoint_path,
            status=status,
            limit=limit,
        )

    @property
    def pending_retries(self) -> int:
        """Get the number of events pending retry."""
        return self.retry_manager.pending_count()
