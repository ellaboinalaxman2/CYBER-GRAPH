// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title CyberGraphAudit
 * @dev Smart contract for registering and verifying immutable cybersecurity audit records.
 * Designed for the Cyber Graph security-event integrity verification system.
 */
contract CyberGraphAudit {
    // Structure to hold an individual audit record
    struct AuditRecord {
        string auditId;
        string eventId;
        string eventHash;
        uint256 timestamp;
        address submitter;
    }

    // Mapping from audit ID to its corresponding AuditRecord
    mapping(string => AuditRecord) private auditRecords;

    // Event emitted when a new audit record is registered on-chain
    event AuditRegistered(
        string indexed auditId,
        string eventId,
        string eventHash,
        uint256 timestamp,
        address indexed submitter
    );

    /**
     * @notice Registers a new cybersecurity audit record on-chain.
     * @param auditId Unique identifier for the audit record.
     * @param eventId Identifier of the security event being audited.
     * @param eventHash Cryptographic SHA-256 hash of the canonicalized security event.
     */
    function registerAudit(
        string memory auditId,
        string memory eventId,
        string memory eventHash
    ) external {
        require(bytes(auditId).length > 0, "Audit ID cannot be empty");
        require(bytes(eventId).length > 0, "Event ID cannot be empty");
        require(bytes(eventHash).length > 0, "Event hash cannot be empty");
        require(bytes(auditRecords[auditId].auditId).length == 0, "Audit ID already registered");

        auditRecords[auditId] = AuditRecord({
            auditId: auditId,
            eventId: eventId,
            eventHash: eventHash,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        emit AuditRegistered(
            auditId,
            eventId,
            eventHash,
            block.timestamp,
            msg.sender
        );
    }

    /**
     * @notice Retrieves the stored audit record details for a given audit ID.
     * @param auditId The unique identifier of the audit record.
     * @return auditId The unique audit identifier.
     * @return eventId The associated event identifier.
     * @return eventHash The cryptographic hash stored on-chain.
     * @return timestamp The block timestamp when the audit was registered.
     * @return submitter The address that submitted the audit record.
     */
    function getAudit(string memory auditId)
        external
        view
        returns (
            string memory,
            string memory,
            string memory,
            uint256,
            address
        )
    {
        require(bytes(auditRecords[auditId].auditId).length > 0, "Audit record not found");
        AuditRecord memory record = auditRecords[auditId];
        return (
            record.auditId,
            record.eventId,
            record.eventHash,
            record.timestamp,
            record.submitter
        );
    }

    /**
     * @notice Verifies whether a supplied event hash matches the stored hash for an audit ID.
     * @param auditId The unique identifier of the audit record to verify.
     * @param eventHash The event hash to compare against the on-chain record.
     * @return bool True if the record exists and the hashes match, False otherwise.
     */
    function verifyAudit(string memory auditId, string memory eventHash)
        external
        view
        returns (bool)
    {
        // If the record does not exist or input hash is empty, return false
        if (bytes(auditRecords[auditId].auditId).length == 0 || bytes(eventHash).length == 0) {
            return false;
        }

        // Compare string hashes in Solidity using keccak256
        return keccak256(bytes(auditRecords[auditId].eventHash)) == keccak256(bytes(eventHash));
    }
}
