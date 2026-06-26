// TypeScript SDK type definitions
export interface ContributionProof {
  proof_id: string;
  creator_id: string;
  category: ValueCategory;
  tier: ComplexityTier;
  hours: number;
  base_value: string;  // Decimal as string
  attestation_count: number;
  can_mint: boolean;
  timestamp: number;
}

export type ValueCategory =
  | 'SOLVED_PROBLEM'
  | 'CREATED_KNOWLEDGE'
  | 'BUILT_INFRASTRUCTURE'
  | 'HEALED_BIOLOGICAL'
  | 'PROTECTED_SYSTEMS'
  | 'OPTIMIZED_PROCESS'
  | 'CONNECTED_PEOPLE'
  | 'RESTORED_ECOLOGICAL'
  | 'ADVANCED_ART'
  | 'DISTRIBUTED_FAIRLY'
  | 'PREVENTED_HARM'
  | 'CREATED_BEAUTY';

export type ComplexityTier = 'micro' | 'small' | 'medium' | 'large' | 'massive' | 'planetary';

export interface ATLASConfig {
  rpcUrl: string;
  network: 'mainnet' | 'testnet' | 'local';
  apiKey?: string;
}

export interface MintResult {
  amount: string;
  proof_id: string;
  confidence: number;
  tx_hash?: string;
}

export interface NetworkStats {
  peers: number;
  mesh_health: number;
  value_events_last_hour: number;
  atlas_minted_today: string;
  top_categories: ValueCategory[];
}
