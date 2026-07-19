"""libp2p node for ATLAS interplanetary mesh."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib, time

@dataclass
class PeerInfo:
    peer_id:      str
    addresses:    List[str]
    protocols:    List[str]
    latency_ms:   float = 0
    bandwidth:    float = 0  # bytes/sec
    connected:    bool = False
    last_seen:    float = field(default_factory=time.time)

@dataclass
class Libp2pNode:
    """
    libp2p node for decentralized peer discovery and communication.
    Supports pubsub, DHT, and stream multiplexing.
    """
    node_id:        str
    listen_addrs:   List[str]
    protocols:      List[str] = field(default_factory=lambda: [
        "/atlas/mesh/1.0.0",
        "/atlas/dht/1.0.0",
        "/atlas/pubsub/1.0.0",
        "/atlas/identify/1.0.0",
    ])
    peers:          Dict[str, PeerInfo] = field(default_factory=dict)
    dht_store:      Dict[str, str] = field(default_factory=dict)
    pubsub_topics:  Dict[str, List[str]] = field(default_factory=dict)
    bootstrapped:   bool = False

    def add_peer(self, peer: PeerInfo) -> None:
        self.peers[peer.peer_id] = peer

    def remove_peer(self, peer_id: str) -> None:
        self.peers.pop(peer_id, None)

    def discover_peers(self, bootstrap_nodes: List[str]) -> List[PeerInfo]:
        """Discover peers via DHT bootstrap."""
        discovered = []
        for addr in bootstrap_nodes:
            pid = hashlib.sha256(addr.encode()).hexdigest()[:16]
            peer = PeerInfo(
                peer_id=pid, addresses=[addr],
                protocols=self.protocols, connected=False,
                latency_ms=50 + len(addr) % 200,
            )
            discovered.append(peer)
            self.add_peer(peer)
        self.bootstrapped = True
        return discovered

    def publish(self, topic: str, message: bytes) -> int:
        """Publish to a pubsub topic. Returns subscriber count."""
        subs = self.pubsub_topics.get(topic, [])
        # In production: flood/gossip to peers subscribed to topic
        return len(subs)

    def subscribe(self, topic: str, handler_id: str) -> None:
        if topic not in self.pubsub_topics:
            self.pubsub_topics[topic] = []
        self.pubsub_topics[topic].append(handler_id)

    def dht_put(self, key: str, value: str) -> None:
        self.dht_store[key] = value

    def dht_get(self, key: str) -> Optional[str]:
        return self.dht_store.get(key)

    def connected_peers(self) -> List[PeerInfo]:
        return [p for p in self.peers.values() if p.connected]
