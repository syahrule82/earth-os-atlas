// ATLAS TypeScript SDK
import type { ContributionProof, ATLASConfig, MintResult, NetworkStats, ValueCategory, ComplexityTier } from './types';

export class AtlasClient {
  private config: ATLASConfig;
  private baseUrl: string;

  constructor(config: ATLASConfig) {
    this.config = config;
    this.baseUrl = config.rpcUrl;
  }

  async createProof(
    creatorId: string,
    category: ValueCategory,
    tier: ComplexityTier,
    hours: number,
    description?: string
  ): Promise<ContributionProof> {
    const response = await fetch(`${this.baseUrl}/v1/proof/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
      body: JSON.stringify({ creator_id: creatorId, category, tier, hours, description }),
    });
    if (!response.ok) throw new Error(`ATLAS API error: ${response.status}`);
    return response.json();
  }

  async mint(proofId: string, confidence = 0.9): Promise<MintResult> {
    const response = await fetch(`${this.baseUrl}/v1/ledger/mint`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...this.authHeaders() },
      body: JSON.stringify({ proof_id: proofId, confidence }),
    });
    return response.json();
  }

  async balance(address: string): Promise<string> {
    const resp = await fetch(`${this.baseUrl}/v1/ledger/balance/${address}`, { headers: this.authHeaders() });
    const data = await resp.json();
    return data.balance;
  }

  async networkStats(): Promise<NetworkStats> {
    const resp = await fetch(`${this.baseUrl}/v1/analytics/network`, { headers: this.authHeaders() });
    return resp.json();
  }

  watchValueEvents(callback: (event: any) => void): WebSocket {
    const ws = new WebSocket(`${this.baseUrl.replace('http', 'ws')}/ws/events`);
    ws.onmessage = (e) => callback(JSON.parse(e.data));
    return ws;
  }

  private authHeaders(): HeadersInit {
    return this.config.apiKey ? { 'X-Atlas-Key': this.config.apiKey } : {};
  }
}

// Factory function
export function createAtlasClient(config: ATLASConfig): AtlasClient {
  return new AtlasClient(config);
}

export * from './types';
