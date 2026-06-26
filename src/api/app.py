"""FastAPI application factory."""
try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    FastAPI = None

def create_app() -> object:
    if not FastAPI:
        raise ImportError("pip install fastapi uvicorn")
    
    app = FastAPI(
        title="ATLAS — Earth OS",
        description="The Living Economic Operating System. Proof-of-Value > Proof-of-Work.",
        version="3.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    from .routes import proof_router, ledger_router, governance_router, analytics_router
    app.include_router(proof_router, prefix="/v1/proof",      tags=["Proofs"])
    app.include_router(ledger_router, prefix="/v1/ledger",    tags=["Ledger"])
    app.include_router(governance_router, prefix="/v1/dao",   tags=["Governance"])
    app.include_router(analytics_router, prefix="/v1/analytics", tags=["Analytics"])
    
    @app.get("/health")
    def health():
        return {"status": "ok", "version": "3.0.0", "network": "atlas-testnet"}
    
    return app

app = create_app() if FastAPI else None
