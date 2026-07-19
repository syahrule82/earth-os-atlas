"""Protocol adapters — Bridge legacy and non-standard systems."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time

@dataclass
class ProtocolAdapter:
    """Base protocol adapter for translating between ATLAS and external protocols."""
    protocol_name: str
    version: str
    direction: str  # inbound, outbound, bidirectional
    
    def adapt_inbound(self, external_data: dict) -> dict:
        """Transform external protocol data to ATLAS format."""
        raise NotImplementedError
    
    def adapt_outbound(self, atlas_data: dict) -> dict:
        """Transform ATLAS data to external protocol format."""
        raise NotImplementedError

@dataclass
class LegacyAdapter(ProtocolAdapter):
    """Adapter for legacy systems (SOAP, XML-RPC, EDI, FTP)."""
    protocol_name: str = "legacy"
    version: str = "1.0"
    direction: str = "bidirectional"
    supported_legacy: list = field(default_factory=lambda: ["SOAP", "XML-RPC", "EDI", "FTP", "SMTP"])
    
    def adapt_inbound(self, external_data: dict) -> dict:
        """Convert legacy format to ATLAS event."""
        # Legacy systems often send flat key-value data
        return {
            "atlas_event": True,
            "source": "legacy",
            "original_format": external_data.get("format", "unknown"),
            "data": external_data,
            "timestamp": time.time(),
        }
    
    def adapt_outbound(self, atlas_data: dict) -> dict:
        """Convert ATLAS data to legacy format."""
        return {
            "format": "legacy",
            "payload": atlas_data,
            "timestamp": time.time(),
        }

@dataclass
class RESTAdapter(ProtocolAdapter):
    """Adapter for RESTful APIs."""
    protocol_name: str = "REST"
    version: str = "1.0"
    direction: str = "bidirectional"
    base_url: str = ""
    
    def adapt_inbound(self, external_data: dict) -> dict:
        return {
            "atlas_event": True,
            "source": "rest",
            "data": external_data,
            "timestamp": time.time(),
        }
    
    def adapt_outbound(self, atlas_data: dict) -> dict:
        return {
            "method": "POST",
            "url": self.base_url,
            "body": atlas_data,
            "headers": {"Content-Type": "application/json"},
        }

@dataclass
class GraphQLAdapter(ProtocolAdapter):
    """Adapter for GraphQL APIs."""
    protocol_name: str = "GraphQL"
    version: str = "1.0"
    direction: str = "bidirectional"
    endpoint: str = ""
    
    def adapt_inbound(self, external_data: dict) -> dict:
        query = external_data.get("query", "")
        variables = external_data.get("variables", {})
        return {
            "atlas_event": True,
            "source": "graphql",
            "query": query,
            "variables": variables,
            "timestamp": time.time(),
        }
    
    def adapt_outbound(self, atlas_data: dict) -> dict:
        # Convert to GraphQL mutation
        return {
            "query": f"mutation {{ createEvent(data: {atlas_data}) {{ id }} }}",
            "variables": {},
        }
