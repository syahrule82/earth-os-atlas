// ATLASToken.sol
// ERC20 token with Proof-of-Value minting
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title ATLASToken
 * @dev Value-Creation Currency backed by proof of contribution
 * Proof-of-Value > Proof-of-Work
 */
contract ATLASToken is ERC20, Ownable {
    uint256 public constant GENESIS_SUPPLY = 1_000_000_000 * 1e18;
    uint256 public constant HALVING_PERIOD = 4 * 365 days;
    uint256 public immutable genesis_timestamp;
    uint256 public total_minted;

    // Authorized minters (PROMETHEUS validators)
    mapping(address => bool) public validators;

    // Contribution proof registry
    mapping(bytes32 => bool) public minted_proofs;

    event ValueMinted(address indexed recipient, bytes32 proof_id, uint256 amount);
    event ValidatorAdded(address indexed validator);

    modifier onlyValidator() {
        require(validators[msg.sender], "Not a validator");
        _;
    }

    constructor() ERC20("ATLAS", "ATLAS") Ownable(msg.sender) {
        genesis_timestamp = block.timestamp;
    }

    function addValidator(address validator) external onlyOwner {
        validators[validator] = true;
        emit ValidatorAdded(validator);
    }

    /**
     * @dev Mint ATLAS from a validated contribution proof
     * @param recipient The creator of value
     * @param proof_id  Unique ID of the ContributionProof
     * @param confidence Validation confidence score (0-10000 = 0-100%)
     */
    function mintFromProof(
        address recipient,
        bytes32 proof_id,
        uint256 confidence
    ) external onlyValidator {
        require(!minted_proofs[proof_id], "Proof already minted");
        require(total_minted < GENESIS_SUPPLY, "Genesis supply exhausted");

        uint256 base_reward = currentReward();
        uint256 amount = (base_reward * confidence) / 10_000;

        minted_proofs[proof_id] = true;
        total_minted += amount;
        _mint(recipient, amount);

        emit ValueMinted(recipient, proof_id, amount);
    }

    /**
     * @dev Current reward rate with 4-year halving
     */
    function currentReward() public view returns (uint256) {
        uint256 halvings = (block.timestamp - genesis_timestamp) / HALVING_PERIOD;
        return (100 * 1e18) >> halvings; // 100 ATLAS base, halving via right shift
    }

    /**
     * @dev Years until next halving
     */
    function yearsToNextHalving() external view returns (uint256) {
        uint256 elapsed = block.timestamp - genesis_timestamp;
        uint256 next = ((elapsed / HALVING_PERIOD) + 1) * HALVING_PERIOD;
        return (next - elapsed) / 365 days;
    }
}
