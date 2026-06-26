// ProofRegistry.sol
// On-chain contribution proof storage
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ProofRegistry
 * @dev Stores and validates Proof-of-Value contribution records on-chain
 */
contract ProofRegistry {
    enum ValueCategory {
        SOLVED_PROBLEM,
        CREATED_KNOWLEDGE,
        BUILT_INFRASTRUCTURE,
        HEALED_BIOLOGICAL,
        PROTECTED_SYSTEMS,
        OPTIMIZED_PROCESS,
        CONNECTED_PEOPLE,
        RESTORED_ECOLOGICAL,
        ADVANCED_ART,
        DISTRIBUTED_FAIRLY,
        PREVENTED_HARM,
        CREATED_BEAUTY
    }

    struct Proof {
        bytes32 proof_id;
        address creator;
        ValueCategory category;
        string tier;           // micro/small/medium/large/massive/planetary
        uint256 hours;         // scaled by 100 (e.g. 800 = 8 hours)
        uint256 base_value;    // ATLAS tokens * 1e18
        uint256 attestations;
        uint256 timestamp;
        string artifact_cid;   // IPFS CID
        bool minted;
    }

    mapping(bytes32 => Proof) public proofs;
    mapping(bytes32 => mapping(address => bool)) public attestors;
    uint256 public proof_count;
    uint256 public constant MIN_ATTESTATIONS = 2;

    event ProofCreated(bytes32 indexed proof_id, address indexed creator, ValueCategory category);
    event ProofAttested(bytes32 indexed proof_id, address indexed attestor);
    event ProofReadyForMint(bytes32 indexed proof_id);

    function createProof(
        ValueCategory category,
        string calldata tier,
        uint256 hours,
        uint256 base_value,
        string calldata artifact_cid
    ) external returns (bytes32) {
        bytes32 proof_id = keccak256(abi.encodePacked(msg.sender, category, block.timestamp, proof_count));
        proofs[proof_id] = Proof({
            proof_id:     proof_id,
            creator:      msg.sender,
            category:     category,
            tier:         tier,
            hours:        hours,
            base_value:   base_value,
            attestations: 0,
            timestamp:    block.timestamp,
            artifact_cid: artifact_cid,
            minted:       false
        });
        proof_count++;
        emit ProofCreated(proof_id, msg.sender, category);
        return proof_id;
    }

    function attest(bytes32 proof_id) external {
        require(proofs[proof_id].creator != address(0), "Proof not found");
        require(!attestors[proof_id][msg.sender], "Already attested");
        require(msg.sender != proofs[proof_id].creator, "Cannot self-attest");
        attestors[proof_id][msg.sender] = true;
        proofs[proof_id].attestations++;
        emit ProofAttested(proof_id, msg.sender);
        if (proofs[proof_id].attestations >= MIN_ATTESTATIONS) {
            emit ProofReadyForMint(proof_id);
        }
    }

    function canMint(bytes32 proof_id) external view returns (bool) {
        Proof storage p = proofs[proof_id];
        return p.attestations >= MIN_ATTESTATIONS && !p.minted;
    }

    function markMinted(bytes32 proof_id) external {
        proofs[proof_id].minted = true;
    }
}
