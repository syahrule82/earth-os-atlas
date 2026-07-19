# Security Policy

## 🔒 Supported Versions

| Version | Supported |
|---------|----------|
| 3.2.x   | ✅ |
| 3.0.x   | ✅ |
| < 3.0   | ❌ |

## 🛡️ Security Features

ATLAS implements multiple layers of security:

- **Post-Quantum Cryptography**: Kyber-768 KEM, Dilithium signatures
- **BLS12-381**: Signature aggregation for validator consensus
- **Zero-Knowledge Proofs**: zk-SNARKs for anonymous attestation
- **Circuit Breakers**: Automatic fault isolation
- **Rate Limiting**: Token bucket per endpoint
- **Audit Logging**: 7-year immutable audit trail
- **Anti-Coercion**: Neural voting coercion detection
- **Slashing**: Validator misbehavior punishment (1-10%)

## 🐛 Reporting a Vulnerability

**Do NOT open a public issue for security vulnerabilities.**

Email: `security@kosasih.org`

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

### Response Timeline

- **Acknowledgement**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Fix Timeline**: Critical (7 days), High (30 days), Medium (90 days)

## 🏆 Bug Bounty Program

| Severity | Reward (ATLAS) |
|----------|----------------|
| Critical | 10,000 |
| High | 5,000 |
| Medium | 1,000 |
| Low | 100 |

Bounties are paid in ATLAS tokens once mainnet launches.

**Forged by TITAN FORGE** 🔥
