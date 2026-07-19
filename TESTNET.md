# 🧪 ATLAS Testnet Documentation

> **Network**: `atlas-testnet-v1` 
> **Chain ID**: `1337` 
> **RPC**: `http://testnet.atlas.kosasih.org:8000` 
> **WebSocket**: `ws://testnet.atlas.kosasih.org:8000/ws` 
> **Faucet**: `http://testnet.atlas.kosasih.org:9090/faucet` 
> **Explorer**: `http://testnet.atlas.kosasih.org:3000` 
> **Status**: 🟢 Online

---

## 📋 Prerequisites

- Python 3.11+ (for Python node)
- Docker 24+ (for containerized deployment)
- kubectl 1.28+ (for Kubernetes)
- Helm 3.13+ (for Helm deployment)
- An ATLAS-compatible PNI device (optional, for neural features)

---

## 🚀 Node Setup

### Option A: Docker (Fastest)

```bash
git clone https://github.com/KOSASIH/earth-os-atlas.git
cd earth-os-atlas
docker-compose up -d
```

Verify your node is running:
```bash
curl http://localhost:9090/health
# {"status": "ok", "version": "3.2.0", "network": "atlas-testnet"}
```

Check mesh peers:
```bash
curl http://localhost:9090/v1/analytics/network
# {"peers": 42, "mesh_health": 0.98, ...}
```

### Option B: Kubernetes (Helm)

```bash
# Add the ATLAS Helm chart
helm install atlas ./deploy/helm/atlas \
  --namespace atlas-testnet \
  --create-namespace \
  --set config.network=testnet \
  --set replicaCount=3
```

### Option C: Bare Metal

```bash
git clone https://github.com/KOSASIH/earth-os-atlas.git
cd earth-os-atlas
pip install -e .[dev]

# Start the node
python atlas_cli.py mesh start --region 0 --interface pni-v3

# In another terminal, start the API server
uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

---

## 🪙 Testnet Faucet

Get test ATLAS tokens for development:

```bash
# Request test tokens
curl -X POST http://testnet.atlas.kosasih.org:9090/faucet \
  -H "Content-Type: application/json" \
  -d '{"address": "did:atlas:your-address"}'

# Response: {"amount": "1000", "tx_hash": "0x..."}
```

Rate limit: 1000 ATLAS per address per 24 hours.

---

## 🏛️ Validator Registration

### 1. Generate Validator Keys

```bash
python atlas_cli.py validator init
# Generates:
# ~/.atlas/validator_bls_key.json  (BLS keypair)
# ~/.atlas/validator_ed25519.pem   (Ed25519 identity)
# ~/.atlas/validator_kyber.bin     (Post-quantum KEM)
```

### 2. Register as Validator

```python
from src.validator.staking import StakingManager
from decimal import Decimal

sm = StakingManager()
validator = sm.register_validator(
    operator="did:atlas:your-did",
    stake=Decimal("10000"),  # Min 10,000 ATLAS
)
print(f"Validator ID: {validator.validator_id}")
```

### 3. Start Validating

```bash
python atlas_cli.py validator start --validator-id <your-validator-id>
```

### Validator Requirements

| Requirement | Value |
|-------------|-------|
| Minimum Stake | 10,000 ATLAS |
| Uptime Required | 95% |
| Unbonding Period | 21 days |
| Commission | 0-10% |
| Max Validators | 100 |

### Slashing Conditions

| Violation | Slash Rate |
|-----------|------------|
| Double Sign | 5% of stake |
| Downtime (<95% uptime) | 1% of stake |
| Invalid Proof | 2% of stake |
| Equivocation | 10% of stake |

---

## 🧠 PNI Device Pairing

### Supported Devices

| Device | Channels | Sample Rate | Connection |
|--------|----------|-------------|------------|
| OpenBCI Cyton | 8 | 250 Hz | Serial / BLE |
| OpenBCI Cyton+Daisy | 16 | 250 Hz | Serial / BLE |
| g.tec USBamp | 32 | 600 Hz | USB |
| g.tec g.Nautilus | 32 | 500 Hz | Wireless |
| Emotiv EPOC+ | 14 | 128 Hz | BLE |
| Emotiv Insight | 5 | 128 Hz | BLE |
| Muse 2 | 4 | 256 Hz | BLE |

### Pairing via CLI

```bash
# Scan for nearby PNI devices
python atlas_cli.py pni scan

# Output:
# Found 2 devices:
#   [1] OpenBCI Cyton (RSSI: -45dBm, MAC: 00:06:66:12:34:56)
#   [2] Emotiv EPOC+ (RSSI: -52dBm, MAC: 00:16:53:78:9A:BC)

# Connect to device
python atlas_cli.py pni connect --device 1
```

### Pairing via Python SDK

```python
import asyncio
from src.pni_bridge import OpenBCIAdapter

async def main():
    adapter = OpenBCIAdapter(port="/dev/ttyUSB0")
    await adapter.connect()
    
    reading = await adapter.stream()
    print(f"Channels: {reading.channels}")
    print(f"Sample rate: {reading.sample_rate}Hz")
    
    await adapter.disconnect()

asyncio.run(main())
```

### Pairing via Mobile App

1. Open ATLAS Mobile App
2. Go to Settings → PNI Devices → Scan
3. Select your EEG device
4. Follow calibration prompts (think "approve" / think "reject")
5. Neural wallet is now authenticated via PNI

---

## 📡 API Endpoints

### Base URL
```
http://testnet.atlas.kosasih.org:8000
```

### Interactive Docs
- **Swagger UI**: `http://testnet.atlas.kosasih.org:8000/docs`
- **ReDoc**: `http://testnet.atlas.kosasih.org:8000/redoc`

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/v1/proof/create` | Create contribution proof |
| GET | `/v1/proof/{id}` | Get proof details |
| POST | `/v1/proof/{id}/attest` | Attest to a proof |
| POST | `/v1/ledger/mint` | Mint ATLAS from proof |
| GET | `/v1/ledger/balance/{address}` | Check balance |
| POST | `/v1/ledger/transfer` | Transfer ATLAS |
| POST | `/v1/dao/propose` | Create governance proposal |
| POST | `/v1/dao/vote` | Vote on proposal |
| GET | `/v1/analytics/network` | Network statistics |
| GET | `/v1/analytics/price` | Price feed |
| WS | `/ws/events` | WebSocket event stream |

### Example: Create and Mint

```bash
# 1. Create a proof
curl -X POST http://testnet.atlas.kosasih.org:8000/v1/proof/create \
  -H "Content-Type: application/json" \
  -d '{
    "creator_id": "did:atlas:alice",
    "category": "CREATED_KNOWLEDGE",
    "tier": "medium",
    "hours": 8.0,
    "description": "Wrote ATLAS testnet documentation"
  }'

# 2. Mint ATLAS
curl -X POST http://testnet.atlas.kosasih.org:8000/v1/ledger/mint \
  -H "Content-Type: application/json" \
  -d '{
    "proof_id": "<proof-id-from-step-1>",
    "confidence": 0.9
  }'
```

---

## 📊 Monitoring

### Grafana Dashboard

- **URL**: `http://testnet.atlas.kosasih.org:3001`
- **Credentials**: `admin` / `atlas-testnet`

Dashboards available:
- **ATLAS Overview**: Mesh health, peer count, packet throughput
- **Economic Engine**: Supply, circulation, minting rate, AMM prices
- **Governance**: Active proposals, vote counts, treasury balance
- **Validator Network**: Validator count, uptime, slashing events
- **PNI Metrics**: Connected devices, cognitive state distribution

### Prometheus Metrics

Metrics endpoint: `http://testnet.atlas.kosasih.org:9090/metrics`

Key metrics:
- `atlas_mesh_peers` — Connected peers
- `atlas_thought_packets_rx` — Packets received
- `atlas_value_events_total` — Value creation events
- `atlas_total_supply` — Total ATLAS minted
- `atlas_consensus_duration` — Consensus latency histogram
- `atlas_treasury_balance` — DAO treasury

---

## 🧪 Testing

### Run Full Test Suite

```bash
pytest tests/ -v --tb=short
```

### Run Specific Phase Tests

```bash
# Phase 1-4 (Core + Titans + Mesh + API)
pytest tests/test_atlas_core.py tests/test_titans.py tests/test_synaptic_mesh.py -v

# Phase 5 (Validator + Production)
pytest tests/test_phase5.py -v

# Phase 6 (Interplanetary + AGI + ZK-VM)
pytest tests/test_phase6.py -v

# Phase 7 (Constitution + Congress + Justice)
pytest tests/test_phase7.py -v
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ATLAS_REGION` | `0` | Geographic region ID |
| `ATLAS_INTERFACE` | `pni-v3` | Network interface |
| `ATLAS_LOG_LEVEL` | `INFO` | Log level (DEBUG/INFO/WARN/ERROR) |
| `ATLAS_NETWORK` | `testnet` | Network type |
| `ATLAS_DATA_DIR` | `~/.atlas` | Data directory |
| `ATLAS_METRICS_PORT` | `9090` | Prometheus metrics port |
| `ATLAS_API_PORT` | `8000` | REST API port |
| `ATLAS_MESH_PORT` | `54321` | Mesh UDP port |

---

## 🆘 Troubleshooting

### Node won't start
```bash
# Check logs
docker logs atlas_mesh_node

# Common issues:
# 1. Port already in use → change ports in docker-compose.yml
# 2. Data directory locked → rm -rf ~/.atlas/*.lock
# 3. Python version too old → require 3.11+
```

### Can't connect to mesh
```bash
# Check firewall allows UDP 54321
sudo ufw allow 54321/udp

# Verify peer discovery
python atlas_cli.py mesh peers
```

### PNI device not found
```bash
# Linux: check serial permissions
sudo usermod -a -G dialout $USER
# Log out and back in

# macOS: check Bluetooth is on
# Check device is in pairing mode
```

### Faucet not working
```bash
# Check rate limit (1000 ATLAS / 24h)
curl http://testnet.atlas.kosasih.org:9090/faucet/status
```

---

## 📞 Support

- **GitHub Issues**: [github.com/KOSASIH/earth-os-atlas/issues](https://github.com/KOSASIH/earth-os-atlas/issues)
- **Discussions**: [github.com/KOSASIH/earth-os-atlas/discussions](https://github.com/KOSASIH/earth-os-atlas/discussions)
- **Docs**: [docs.earth-os-atlas.io](https://docs.earth-os-atlas.io)

---

**Forged by TITAN FORGE** 🔥
