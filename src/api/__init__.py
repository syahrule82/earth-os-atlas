"""ATLAS REST API — FastAPI server."""
from .app import create_app, app
from .routes import proof_router, ledger_router, governance_router, analytics_router

__all__ = ["create_app", "app", "proof_router", "ledger_router", 
           "governance_router", "analytics_router"]
