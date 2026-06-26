"""Cross-chain bridges for ATLAS interoperability."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Optional
import hashlib, time

@dataclass
class BridgeConfig:
    chain_id: str
    rpc_url: str
    bridge_contract: str
    native_token: str

@dataclass
class BridgeTransfer:
    transfer_id: str
    from_chain: str
    to_chain: str
    sender: str
    recipient: str
    amount: Decimal
    status: str  # pending, confirmed, failed
    tx_hash: Optional[str] = None

class EthereumBridge:
    """Ethereum <-> ATLAS bridge via lock/mint."""
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.pending: Dict[str, BridgeTransfer] = {}

    def lock_and_mint(self, sender: str, recipient: str, 
                      amount: Decimal) -> BridgeTransfer:
        """Lock ETH/ERC20 on Ethereum, mint wATLAS on ATLAS."""
        tid = hashlib.sha256(f"{sender}:{recipient}:{amount}:{time.time()}".encode()).hexdigest()[:16]
        transfer = BridgeTransfer(
            transfer_id=tid,
            from_chain="ethereum",
            to_chain="atlas",
            sender=sender,
            recipient=recipient,
            amount=amount,
            status="pending",
        )
        self.pending[tid] = transfer
        # In production: listen for Ethereum event, then mint on ATLAS
        return transfer

    def burn_and_release(self, sender: str, recipient: str, 
                         amount: Decimal) -> BridgeTransfer:
        """Burn wATLAS on ATLAS, release ETH/ERC20 on Ethereum."""
        tid = hashlib.sha256(f"{sender}:{recipient}:{amount}:{time.time()}".encode()).hexdigest()[:16]
        return BridgeTransfer(
            transfer_id=tid,
            from_chain="atlas",
            to_chain="ethereum",
            sender=sender,
            recipient=recipient,
            amount=amount,
            status="pending",
        )

class SolanaBridge:
    """Solana <-> ATLAS bridge via Wormhole."""
    def __init__(self, config: BridgeConfig):
        self.config = config

class CosmosIBCBridge:
    """Cosmos IBC bridge for ATLAS."""
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.channels: Dict[str, str] = {}
