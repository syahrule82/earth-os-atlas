// Package atlas provides a Go SDK for the ATLAS Earth OS
package atlas

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// ValueCategory represents one of the 12 ATLAS value categories
type ValueCategory string

const (
	CategorySolvedProblem       ValueCategory = "SOLVED_PROBLEM"
	CategoryCreatedKnowledge    ValueCategory = "CREATED_KNOWLEDGE"
	CategoryBuiltInfrastructure ValueCategory = "BUILT_INFRASTRUCTURE"
	CategoryHealedBiological    ValueCategory = "HEALED_BIOLOGICAL"
	CategoryProtectedSystems    ValueCategory = "PROTECTED_SYSTEMS"
	CategoryOptimizedProcess    ValueCategory = "OPTIMIZED_PROCESS"
	CategoryConnectedPeople     ValueCategory = "CONNECTED_PEOPLE"
	CategoryRestoredEcological  ValueCategory = "RESTORED_ECOLOGICAL"
	CategoryAdvancedArt         ValueCategory = "ADVANCED_ART"
	CategoryDistributedFairly   ValueCategory = "DISTRIBUTED_FAIRLY"
	CategoryPreventedHarm       ValueCategory = "PREVENTED_HARM"
	CategoryCreatedBeauty       ValueCategory = "CREATED_BEAUTY"
)

// ComplexityTier represents the scale of a contribution
type ComplexityTier string

const (
	TierMicro     ComplexityTier = "micro"
	TierSmall     ComplexityTier = "small"
	TierMedium    ComplexityTier = "medium"
	TierLarge     ComplexityTier = "large"
	TierMassive   ComplexityTier = "massive"
	TierPlanetary ComplexityTier = "planetary"
)

// Client is the ATLAS API client
type Client struct {
	rpcURL     string
	apiKey     string
	httpClient *http.Client
}

// ContributionProof represents a proof of value creation
type ContributionProof struct {
	ProofID    string        `json:"proof_id"`
	CreatorID  string        `json:"creator_id"`
	Category   ValueCategory `json:"category"`
	Tier       ComplexityTier `json:"tier"`
	Hours      float64       `json:"hours"`
	BaseValue  string        `json:"base_value"`
	CanMint    bool          `json:"can_mint"`
}

// MintResult represents the result of minting ATLAS
type MintResult struct {
	Amount     string  `json:"amount"`
	ProofID    string  `json:"proof_id"`
	Confidence float64 `json:"confidence"`
}

// NetworkStats represents network-level statistics
type NetworkStats struct {
	Peers               uint32  `json:"peers"`
	MeshHealth          float64 `json:"mesh_health"`
	ValueEventsLastHour uint64  `json:"value_events_last_hour"`
	AtlasMintedToday    string  `json:"atlas_minted_today"`
}

// NewClient creates a new ATLAS client
func NewClient(rpcURL string) *Client {
	return &Client{
		rpcURL:     rpcURL,
		httpClient: &http.Client{Timeout: 30 * time.Second},
	}
}

// WithAPIKey sets the API key for authentication
func (c *Client) WithAPIKey(key string) *Client {
	c.apiKey = key
	return c
}

// CreateProof creates a contribution proof
func (c *Client) CreateProof(ctx context.Context, creatorID string, category ValueCategory, tier ComplexityTier, hours float64, description string) (*ContributionProof, error) {
	body := map[string]interface{}{
		"creator_id":  creatorID,
		"category":    string(category),
		"tier":        string(tier),
		"hours":       hours,
		"description": description,
	}
	jsonBody, _ := json.Marshal(body)

	req, err := http.NewRequestWithContext(ctx, "POST", c.rpcURL+"/v1/proof/create", bytes.NewReader(jsonBody))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("X-Atlas-Key", c.apiKey)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("API error: %d - %s", resp.StatusCode, string(body))
	}

	var proof ContributionProof
	if err := json.NewDecoder(resp.Body).Decode(&proof); err != nil {
		return nil, err
	}
	return &proof, nil
}

// Mint mints ATLAS from a verified proof
func (c *Client) Mint(ctx context.Context, proofID string, confidence float64) (*MintResult, error) {
	body := map[string]interface{}{
		"proof_id":   proofID,
		"confidence": confidence,
	}
	jsonBody, _ := json.Marshal(body)

	req, err := http.NewRequestWithContext(ctx, "POST", c.rpcURL+"/v1/ledger/mint", bytes.NewReader(jsonBody))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.apiKey != "" {
		req.Header.Set("X-Atlas-Key", c.apiKey)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result MintResult
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}
	return &result, nil
}

// Balance retrieves the balance of an address
func (c *Client) Balance(ctx context.Context, address string) (string, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.rpcURL+"/v1/ledger/balance/"+address, nil)
	if err != nil {
		return "", err
	}
	if c.apiKey != "" {
		req.Header.Set("X-Atlas-Key", c.apiKey)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var data map[string]string
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return "", err
	}
	return data["balance"], nil
}

// NetworkStats retrieves current network statistics
func (c *Client) NetworkStats(ctx context.Context) (*NetworkStats, error) {
	req, err := http.NewRequestWithContext(ctx, "GET", c.rpcURL+"/v1/analytics/network", nil)
	if err != nil {
		return nil, err
	}
	if c.apiKey != "" {
		req.Header.Set("X-Atlas-Key", c.apiKey)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var stats NetworkStats
	if err := json.NewDecoder(resp.Body).Decode(&stats); err != nil {
		return nil, err
	}
	return &stats, nil
}
