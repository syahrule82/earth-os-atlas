"""Universal Gateway — Single API gateway for all external connections."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from decimal import Decimal
import hashlib, time, secrets

@dataclass
class APIKey:
    """Scoped API key for external consumers."""
    key_id: str
    key_hash: str  # SHA-256 hash of the actual key
    consumer_did: str
    scopes: List[str]  # e.g., ["proof:create", "ledger:mint", "ledger:balance"]
    rate_limit_per_min: int = 100
    created_at: float = field(default_factory=time.time)
    last_used: Optional[float] = None
    active: bool = True
    expires_at: Optional[float] = None

@dataclass
class GatewayRoute:
    """A route definition in the gateway."""
    route_id: str
    path: str  # e.g., "/v1/proof/create"
    method: str  # GET, POST, PUT, DELETE
    connector: str  # Which connector handles this
    handler: str  # Handler function name
    required_scopes: List[str]
    rate_limit_per_min: int = 60
    cache_ttl: int = 0  # 0 = no cache
    transform_request: Optional[str] = None  # Transform function name
    transform_response: Optional[str] = None

class UniversalGateway:
    """
    Universal API gateway for ATLAS.
    
    - Routes requests to appropriate connectors
    - Enforces authentication via API keys
    - Rate limiting per consumer and per route
    - Request/response transformation
    - Caching for read operations
    """

    def __init__(self):
        self.routes: Dict[str, GatewayRoute] = {}
        self.api_keys: Dict[str, APIKey] = {}  # key_id -> APIKey
        self.connector_registry: Dict[str, object] = {}
        self.request_log: List[dict] = []
        self.rate_limiter: Dict[str, List[float]] = {}  # key_id -> timestamps
        self.cache: Dict[str, tuple] = {}  # cache_key -> (data, expiry)

    def register_route(self, route: GatewayRoute) -> None:
        key = f"{route.method}:{route.path}"
        self.routes[key] = route

    def register_connector(self, name: str, connector: object) -> None:
        self.connector_registry[name] = connector

    def create_api_key(self, consumer_did: str, scopes: List[str],
                      rate_limit: int = 100) -> tuple:
        """Create a new API key. Returns (key_id, raw_key)."""
        raw_key = secrets.token_urlsafe(32)
        key_id = hashlib.sha256(f"{consumer_did}:{time.time()}".encode()).hexdigest()[:16]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = APIKey(
            key_id=key_id, key_hash=key_hash,
            consumer_did=consumer_did, scopes=scopes,
            rate_limit_per_min=rate_limit,
        )
        self.api_keys[key_id] = api_key
        return key_id, raw_key

    def authenticate(self, raw_key: str) -> Optional[APIKey]:
        """Authenticate an API key."""
 key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        for api_key in self.api_keys.values():
            if api_key.key_hash == key_hash and api_key.active:
                if api_key.expires_at and time.time() > api_key.expires_at:
                    return None
                api_key.last_used = time.time()
                return api_key
        return None

    def check_rate_limit(self, key_id: str) -> bool:
        """Check if request is within rate limit."""
        api_key = self.api_keys.get(key_id)
        if not api_key:
            return False
        now = time.time()
        window_start = now - 60  # 1 minute window
        timestamps = [t for t in self.rate_limiter.get(key_id, []) if t > window_start]
        if len(timestamps) >= api_key.rate_limit_per_min:
            return False
        timestamps.append(now)
        self.rate_limiter[key_id] = timestamps
        return True

    def route_request(self, method: str, path: str, api_key: APIKey,
                      body: dict = None, params: dict = None) -> dict:
        """Route a request to the appropriate connector."""
        key = f"{method}:{path}"
        route = self.routes.get(key)
        if not route:
            return {"status": 404, "error": "Route not found"}
        # Check scopes
        for scope in route.required_scopes:
            if scope not in api_key.scopes:
                return {"status": 403, "error": f"Missing scope: {scope}"}
        # Check rate limit
        if not self.check_rate_limit(api_key.key_id):
            return {"status": 429, "error": "Rate limit exceeded"}
        # Check cache
        if route.cache_ttl > 0:
            cache_key = f"{key}:{str(params)}"
            cached = self.cache.get(cache_key)
            if cached and time.time() < cached[1]:
                return {"status": 200, "data": cached[0], "cached": True}
        # Get connector
        connector = self.connector_registry.get(route.connector)
        if not connector:
            return {"status": 503, "error": f"Connector {route.connector} unavailable"}
        # Call handler
        handler = getattr(connector, route.handler, None)
        if not handler:
            return {"status": 500, "error": f"Handler {route.handler} not found"}
        try:
            result = handler(body or {}, params or {})
            # Cache if applicable
            if route.cache_ttl > 0 and method == "GET":
                cache_key = f"{key}:{str(params)}"
                self.cache[cache_key] = (result, time.time() + route.cache_ttl)
            # Log request
            self.request_log.append({
                "key_id": api_key.key_id, "method": method,
                "path": path, "status": 200, "timestamp": time.time(),
            })
            return {"status": 200, "data": result}
        except Exception as e:
            self.request_log.append({
                "key_id": api_key.key_id, "method": method,
                "path": path, "status": 500, "error": str(e),
                "timestamp": time.time(),
            })
            return {"status": 500, "error": str(e)}

    def revoke_api_key(self, key_id: str) -> bool:
        api_key = self.api_keys.get(key_id)
        if api_key:
            api_key.active = False
            return True
        return False

    def stats(self) -> dict:
        return {
            "total_routes": len(self.routes),
            "total_api_keys": len(self.api_keys),
            "active_keys": sum(1 for k in self.api_keys.values() if k.active),
            "total_connectors": len(self.connector_registry),
            "total_requests": len(self.request_log),
            "cache_entries": len(self.cache),
        }
