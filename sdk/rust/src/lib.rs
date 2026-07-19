// ATLAS Rust SDK
// Type-safe async client for Earth OS

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// ATLAS client for interacting with Earth OS nodes
pub struct AtlasClient {
    rpc_url: String,
    api_key: Option<String>,
    http_client: reqwest::Client,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ContributionProof {
    pub proof_id: String,
    pub creator_id: String,
    pub category: ValueCategory,
    pub tier: ComplexityTier,
    pub hours: f64,
    pub base_value: String,
    pub can_mint: bool,
    pub timestamp: f64,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum ValueCategory {
    SolvedProblem,
    CreatedKnowledge,
    BuiltInfrastructure,
    HealedBiological,
    ProtectedSystems,
    OptimizedProcess,
    ConnectedPeople,
    RestoredEcological,
    AdvancedArt,
    DistributedFairly,
    PreventedHarm,
    CreatedBeauty,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum ComplexityTier {
    Micro,
    Small,
    Medium,
    Large,
    Massive,
    Planetary,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MintResult {
    pub amount: String,
    pub proof_id: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct NetworkStats {
    pub peers: u32,
    pub mesh_health: f64,
    pub value_events_last_hour: u64,
    pub atlas_minted_today: String,
}

#[derive(Debug, thiserror::Error)]
pub enum AtlasError {
    #[error("HTTP error: {0}")]
    Http(#[from] reqwest::Error),
    #[error("API error: {status} - {message}")]
    Api { status: u16, message: String },
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

impl AtlasClient {
    /// Create a new ATLAS client
    pub fn new(rpc_url: &str) -> Self {
        Self {
            rpc_url: rpc_url.to_string(),
            api_key: None,
            http_client: reqwest::Client::new(),
        }
    }

    /// Set API key for authentication
    pub fn with_api_key(mut self, key: &str) -> Self {
        self.api_key = Some(key.to_string());
        self
    }

    fn url(&self, path: &str) -> String {
        format!("{}{}", self.rpc_url, path)
    }

    fn add_auth(&self, req: reqwest::RequestBuilder) -> reqwest::RequestBuilder {
        match &self.api_key {
            Some(key) => req.header("X-Atlas-Key", key),
            None => req,
        }
    }

    /// Create a contribution proof
    pub async fn create_proof(
        &self,
        creator_id: &str,
        category: ValueCategory,
        tier: ComplexityTier,
        hours: f64,
        description: &str,
    ) -> Result<ContributionProof, AtlasError> {
        let body = serde_json::json!({
            "creator_id": creator_id,
            "category": category,
            "tier": tier,
            "hours": hours,
            "description": description,
        });
        let resp = self.add_auth(
            self.http_client.post(self.url("/v1/proof/create"))
                .header("Content-Type", "application/json")
                .json(&body)
        ).send().await?;

        if !resp.status().is_success() {
            return Err(AtlasError::Api {
                status: resp.status().as_u16(),
                message: resp.text().await.unwrap_or_default(),
            });
        }

        Ok(resp.json().await?)
    }

    /// Mint ATLAS from a verified proof
    pub async fn mint(
        &self,
        proof_id: &str,
        confidence: f64,
    ) -> Result<MintResult, AtlasError> {
        let body = serde_json::json!({
            "proof_id": proof_id,
            "confidence": confidence,
        });
        let resp = self.add_auth(
            self.http_client.post(self.url("/v1/ledger/mint"))
                .header("Content-Type", "application/json")
                .json(&body)
        ).send().await?;

        Ok(resp.json().await?)
    }

    /// Check balance of an address
    pub async fn balance(&self, address: &str) -> Result<String, AtlasError> {
        let resp = self.add_auth(
            self.http_client.get(self.url(&format!("/v1/ledger/balance/{}", address)))
        ).send().await?;

        let data: HashMap<String, String> = resp.json().await?;
        Ok(data.get("balance").cloned().unwrap_or_default())
    }

    /// Get network statistics
    pub async fn network_stats(&self) -> Result<NetworkStats, AtlasError> {
        let resp = self.add_auth(
            self.http_client.get(self.url("/v1/analytics/network"))
        ).send().await?;

        Ok(resp.json().await?)
    }

    /// Transfer ATLAS to another address
    pub async fn transfer(
        &self,
        sender: &str,
        recipient: &str,
        amount: f64,
    ) -> Result<bool, AtlasError> {
        let body = serde_json::json!({
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        });
        let resp = self.add_auth(
            self.http_client.post(self.url("/v1/ledger/transfer"))
                .header("Content-Type", "application/json")
                .json(&body)
        ).send().await?;

        Ok(resp.status().is_success())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_creation() {
        let client = AtlasClient::new("http://localhost:8000");
        assert_eq!(client.rpc_url, "http://localhost:8000");
    }

    #[test]
    fn test_with_api_key() {
        let client = AtlasClient::new("http://localhost:8000")
            .with_api_key("test-key");
        assert!(client.api_key.is_some());
    }
}
