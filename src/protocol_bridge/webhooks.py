"""Webhook system — Event subscription and delivery."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
import hashlib, time, json, secrets

@dataclass
class WebhookSubscription:
    """A webhook subscription for event delivery."""
    subscription_id: str
    subscriber_did: str
    callback_url: str
    event_types: List[str]  # e.g., ["proof.created", "atlas.minted", "governance.proposal"]
    secret: str  # HMAC signing secret
    active: bool = True
    max_retries: int = 5
    created_at: float = field(default_factory=time.time)
    delivery_count: int = 0
    failure_count: int = 0

@dataclass
class WebhookEvent:
    """An event to be delivered via webhook."""
    event_id: str
    event_type: str
    payload: dict
    timestamp: float = field(default_factory=time.time)
    subscription_id: Optional[str] = None
    delivery_attempts: int = 0
    delivered: bool = False
    next_retry: Optional[float] = None
    response_code: Optional[int] = None

class WebhookSystem:
    """
    Webhook event delivery system.
    
    - Event subscription with type filtering
    - HMAC-SHA256 signed deliveries
    - Exponential backoff retry (1s, 2s, 4s, 8s, 16s)
    - Dead letter queue for permanently failed deliveries
    - Real-time streaming via SSE
    """

    RETRY_DELAYS = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]  # seconds

    def __init__(self):
        self.subscriptions: Dict[str, WebhookSubscription] = {}
        self.pending_events: List[WebhookEvent] = []
        self.delivered_events: List[WebhookEvent] = []
        self.dead_letter_queue: List[WebhookEvent] = []
        self.sse_clients: Dict[str, List[Callable]] = {}  # event_type -> callbacks

    def subscribe(self, subscriber_did: str, callback_url: str,
                  event_types: List[str]) -> WebhookSubscription:
        """Create a new webhook subscription."""
        secret = secrets.token_urlsafe(32)
        sub = WebhookSubscription(
            subscription_id=hashlib.sha256(f"{subscriber_did}:{callback_url}:{time.time()}".encode()).hexdigest()[:16],
            subscriber_did=subscriber_did,
            callback_url=callback_url,
            event_types=event_types,
            secret=secret,
        )
        self.subscriptions[sub.subscription_id] = sub
        return sub

    def unsubscribe(self, subscription_id: str) -> bool:
        sub = self.subscriptions.get(subscription_id)
        if sub:
            sub.active = False
            return True
        return False

    def emit(self, event_type: str, payload: dict) -> List[WebhookEvent]:
        """Emit an event to all matching subscribers."""
        events = []
        for sub in self.subscriptions.values():
            if not sub.active:
                continue
            # Check if subscription matches this event type
            if event_type not in sub.event_types and "*" not in sub.event_types:
                continue
            event = WebhookEvent(
                event_id=hashlib.sha256(f"{event_type}:{time.time()}:{sub.subscription_id}".encode()).hexdigest()[:16],
                event_type=event_type,
                payload=payload,
                subscription_id=sub.subscription_id,
            )
            events.append(event)
            self.pending_events.append(event)
        # Notify SSE clients
        for callback in self.sse_clients.get(event_type, []):
            callback(payload)
        return events

    def deliver(self, event: WebhookEvent) -> bool:
        """Attempt to deliver a webhook event."""
        sub = self.subscriptions.get(event.subscription_id)
        if not sub or not sub.active:
            return False
        event.delivery_attempts += 1
        # Simulate delivery (in production: HTTP POST with HMAC signature)
        success = True  # Simulated success
        if success:
            event.delivered = True
            event.response_code = 200
            sub.delivery_count += 1
            self.delivered_events.append(event)
            self.pending_events = [e for e in self.pending_events if e.event_id != event.event_id]
            return True
        else:
            sub.failure_count += 1
            if event.delivery_attempts >= sub.max_retries:
                self.dead_letter_queue.append(event)
                self.pending_events = [e for e in self.pending_events if e.event_id != event.event_id]
            else:
                delay = self.RETRY_DELAYS[min(event.delivery_attempts - 1, len(self.RETRY_DELAYS) - 1)]
                event.next_retry = time.time() + delay
            return False

    def process_pending(self) -> int:
        """Process all pending events that are ready for delivery."""
        now = time.time()
        ready = [e for e in self.pending_events if e.next_retry is None or e.next_retry <= now]
        delivered = 0
        for event in ready:
            if self.deliver(event):
                delivered += 1
        return delivered

    def sign_payload(self, event: WebhookEvent, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload."""
        import hmac
        payload_bytes = json.dumps(event.payload, sort_keys=True).encode()
        return hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()

    def register_sse_client(self, event_type: str, callback: Callable) -> None:
        """Register a Server-Sent Events client for real-time streaming."""
        if event_type not in self.sse_clients:
            self.sse_clients[event_type] = []
        self.sse_clients[event_type].append(callback)

    def stats(self) -> dict:
        return {
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": sum(1 for s in self.subscriptions.values() if s.active),
            "pending_events": len(self.pending_events),
            "delivered_events": len(self.delivered_events),
            "dead_letter_queue": len(self.dead_letter_queue),
            "total_deliveries": sum(s.delivery_count for s in self.subscriptions.values()),
        }
