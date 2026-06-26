# CHANGELOG

All notable changes to ATLAS — Earth OS.

## [3.0.0] — 2026-06-26 (Phase 4 Complete)

### Added: Phase 4 — API, Contracts & SDKs
- **REST API** (FastAPI): `/v1/proof`, `/v1/ledger`, `/v1/dao`, `/v1/analytics`
- **Solidity Contracts**: ATLASToken, ProofRegistry, GovernanceDAO, Bridge, Treasury
- **TypeScript SDK**: Full type definitions, WebSocket events, ESM bundle
- **Kubernetes Helm chart** for one-command deployment
- **Grafana alerting rules** for production monitoring
- **Comprehensive API documentation**

### Added: Phase 3 — Economic Engine & Governance
- **Bonding curves**: Linear, Exponential, Logarithmic price discovery
- **AMM pools**: Constant product with fee tiers and liquidity positions
- **TWAP Oracle**: Time-weighted average price with multi-source aggregation
- **DAO Treasury**: Programmable allocation with proportional/quadratic strategies
- **GovernanceDAO**: Quadratic voting, conviction voting, 7-day proposal periods
- **Reputation System**: Soulbound tokens, contribution records, recency decay
- **DID:atlas Identity**: Verifiable credentials, zk-SNARK proofs
- **Cross-chain Bridges**: Ethereum, Solana, Cosmos IBC
- **PNI Bridge**: OpenBCI, g.tec, Emotiv EEG adapters
- **Economic Simulator**: Agent-based modeling, Gini coefficient, stress testing
- **Kubernetes manifests**: 3-replica testnet deployment
- **Grafana dashboard**: 6-panel production monitoring

### Added: Phase 2 — Distributed Infrastructure
- **Mesh Protocol**: Full PNI/BCI-IPv6 stack, thought packets, neural addressing
- **HERMES Network**: Global sensor mesh, multi-modal fusion, category detection
- **ATLAS Ledger**: Proof-of-Value blockchain, account state, consensus
- **Titan Forge**: Orchestrator, workflow engine, system metrics
- **Quantum Layer**: Kyber-768, Dilithium, QRNG, quantum consensus
- **Docker/Compose**: Containerized node deployment
- **CI/CD Release**: Automated PyPI publishing

### Added: Phase 1 — Foundation
- **4 Titans**: HERMES, PROMETHEUS, GAEA, CHRONOS agents
- **ATLAS Core**: ValueRecognizer (12 categories), PROMETHEUSValidator, ATLASMinter
- **Cognitive State**: FSM, memory graph, attention engine, valence tracker
- **Synaptic Mesh**: Thought packets, neural addresses, Dijkstra routing
- **Quantum**: Post-quantum crypto, lattice keys, quantum consensus
- **Nanite Mesh**: Nano-computation substrate simulation
- **Test Suite**: 40+ tests across all modules

## [2.0.0] — 2026-05-18 (protocol-zero)

- Initial protocol-zero repository
- BCI-IPv6 protocol specification
- Basic thought packet structure

## [1.0.0] — 2026-05-01 (genesis)

- Project inception: The Living Economic Operating System
- TITAN FORGE design philosophy
- Earth OS thesis: Proof-of-Value > Proof-of-Work
