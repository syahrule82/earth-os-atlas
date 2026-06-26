// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title ATLASGovernanceDAO
 * @dev Quadratic voting governance for the ATLAS protocol
 */
contract ATLASGovernanceDAO {
    struct Proposal {
        uint256 id;
        address proposer;
        string title;
        string description;
        uint256 start_time;
        uint256 end_time;
        uint256 votes_for_quadratic;
        uint256 votes_against_quadratic;
        uint256 total_participants;
        bool executed;
        bool passed;
    }

    mapping(uint256 => Proposal) public proposals;
    mapping(uint256 => mapping(address => uint256)) public voter_credits;
    mapping(address => uint256) public voice_credits;
    uint256 public proposal_count;
    uint256 public constant VOTING_PERIOD = 7 days;
    uint256 public constant MIN_VOICE_TO_PROPOSE = 100;

    event ProposalCreated(uint256 indexed id, address proposer, string title);
    event Voted(uint256 indexed proposal_id, address voter, uint256 credits, bool approve);
    event ProposalExecuted(uint256 indexed id, bool passed);

    function grantVoice(address voter, uint256 credits) external {
        // In prod: only callable by PROMETHEUS validator contract
        voice_credits[voter] += credits;
    }

    function propose(string calldata title, string calldata description) external returns (uint256) {
        require(voice_credits[msg.sender] >= MIN_VOICE_TO_PROPOSE, "Insufficient voice credits");
        uint256 id = ++proposal_count;
        proposals[id] = Proposal({
            id: id, proposer: msg.sender,
            title: title, description: description,
            start_time: block.timestamp,
            end_time: block.timestamp + VOTING_PERIOD,
            votes_for_quadratic: 0, votes_against_quadratic: 0,
            total_participants: 0, executed: false, passed: false
        });
        emit ProposalCreated(id, msg.sender, title);
        return id;
    }

    function vote(uint256 proposal_id, uint256 credits, bool approve) external {
        Proposal storage p = proposals[proposal_id];
        require(block.timestamp >= p.start_time && block.timestamp <= p.end_time, "Voting closed");
        require(voice_credits[msg.sender] >= credits, "Insufficient voice credits");
        require(voter_credits[proposal_id][msg.sender] == 0, "Already voted");
        
        voice_credits[msg.sender] -= credits;
        voter_credits[proposal_id][msg.sender] = credits;
        
        // Quadratic: voting power = sqrt(credits)
        uint256 qvotes = sqrt(credits);
        if (approve) p.votes_for_quadratic += qvotes;
        else p.votes_against_quadratic += qvotes;
        p.total_participants++;
        
        emit Voted(proposal_id, msg.sender, credits, approve);
    }

    function execute(uint256 proposal_id) external {
        Proposal storage p = proposals[proposal_id];
        require(block.timestamp > p.end_time, "Voting still active");
        require(!p.executed, "Already executed");
        p.executed = true;
        p.passed = p.votes_for_quadratic > p.votes_against_quadratic && p.total_participants >= 3;
        emit ProposalExecuted(proposal_id, p.passed);
    }

    function sqrt(uint256 x) internal pure returns (uint256 y) {
        if (x == 0) return 0;
        uint256 z = (x + 1) / 2;
        y = x;
        while (z < y) { y = z; z = (x / z + z) / 2; }
    }
}
