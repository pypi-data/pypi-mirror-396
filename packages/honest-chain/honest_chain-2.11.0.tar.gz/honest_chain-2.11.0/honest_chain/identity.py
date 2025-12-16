"""
HONEST CHAIN - Quantum-Ready Agent Identity
============================================

Cryptographic identity system for AI agents.

Features:
- SHA3-256 hashing (quantum-resistant)
- Hash-based identity commitments
- DID-style identifiers (did:hc:...)
- Deterministic key derivation
- Signature chains for decision signing
- Ready for post-quantum algorithms (CRYSTALS-Dilithium)

Security Model:
    L0: SHA3-256 hash commitments (quantum-safe)
    L1: HMAC-SHA3 signatures (current)
    L2: Post-quantum signatures (future: Dilithium/SPHINCS+)

Copyright (c) 2025 Stellanium Ltd. All rights reserved.
Licensed under Business Source License 1.1 (BSL). See LICENSE file.
"""

import hashlib
import hmac
import json
import secrets
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from enum import Enum


class SignatureAlgorithm(Enum):
    """Supported signature algorithms"""
    HMAC_SHA3_256 = "hmac-sha3-256"      # Current: quantum-safe HMAC
    HASH_CHAIN = "hash-chain-v1"          # Hash-based commitments
    # Future post-quantum:
    # DILITHIUM3 = "dilithium3"           # NIST PQ standard
    # SPHINCS_SHA3 = "sphincs-sha3-256f"  # Hash-based signatures


@dataclass
class KeyMaterial:
    """Cryptographic key material for an agent"""
    seed: bytes                    # 32-byte master seed
    identity_key: bytes            # Derived identity key
    signing_key: bytes             # Derived signing key
    commitment: str                # Public commitment (hash of public data)
    created_at: str
    algorithm: SignatureAlgorithm = SignatureAlgorithm.HMAC_SHA3_256

    @classmethod
    def generate(cls) -> 'KeyMaterial':
        """Generate new cryptographic key material"""
        seed = secrets.token_bytes(32)
        return cls.from_seed(seed)

    @classmethod
    def from_seed(cls, seed: bytes) -> 'KeyMaterial':
        """Derive all keys from master seed"""
        # Use SHA3-256 for quantum resistance
        identity_key = hashlib.sha3_256(seed + b"identity").digest()
        signing_key = hashlib.sha3_256(seed + b"signing").digest()

        # Public commitment - can be shared without revealing keys
        commitment = hashlib.sha3_256(identity_key + signing_key).hexdigest()

        return cls(
            seed=seed,
            identity_key=identity_key,
            signing_key=signing_key,
            commitment=commitment,
            created_at=datetime.utcnow().isoformat() + "Z"
        )

    def to_public(self) -> Dict[str, Any]:
        """Export only public data (safe to share)"""
        return {
            "commitment": self.commitment,
            "algorithm": self.algorithm.value,
            "created_at": self.created_at
        }


@dataclass
class AgentIdentity:
    """
    Quantum-ready cryptographic identity for AI agents.

    Usage:
        # Create new identity
        identity = AgentIdentity.create("my-agent")

        # Sign data
        signature = identity.sign(b"decision data")

        # Verify signature
        assert identity.verify(b"decision data", signature)

        # Get DID
        did = identity.did  # "did:hc:abc123..."
    """

    agent_id: str
    keys: KeyMaterial
    _did: str = field(default="", init=False)

    def __post_init__(self):
        # Generate DID from commitment
        self._did = f"did:hc:{self.keys.commitment[:32]}"

    @property
    def did(self) -> str:
        """Decentralized Identifier (DID) for this agent"""
        return self._did

    @property
    def public_key_hash(self) -> str:
        """Public key hash (quantum-safe commitment)"""
        return self.keys.commitment

    @classmethod
    def create(cls, agent_id: str, storage_path: Optional[Path] = None) -> 'AgentIdentity':
        """
        Create a new agent identity.

        Args:
            agent_id: Unique identifier for the agent
            storage_path: Where to store keys (default: ~/.honest_chain/identities/)

        Returns:
            New AgentIdentity with generated keys
        """
        storage = storage_path or Path.home() / ".honest_chain" / "identities"
        storage.mkdir(parents=True, exist_ok=True)

        key_file = storage / f"{agent_id}.key"

        # Check if identity already exists
        if key_file.exists():
            return cls.load(agent_id, storage_path)

        # Generate new keys
        keys = KeyMaterial.generate()
        identity = cls(agent_id=agent_id, keys=keys)

        # Save keys securely
        identity._save(key_file)

        return identity

    @classmethod
    def load(cls, agent_id: str, storage_path: Optional[Path] = None) -> 'AgentIdentity':
        """Load existing identity from storage"""
        storage = storage_path or Path.home() / ".honest_chain" / "identities"
        key_file = storage / f"{agent_id}.key"

        if not key_file.exists():
            raise FileNotFoundError(f"No identity found for agent: {agent_id}")

        with open(key_file, "rb") as f:
            data = json.loads(f.read().decode())

        seed = bytes.fromhex(data["seed"])
        keys = KeyMaterial.from_seed(seed)

        return cls(agent_id=agent_id, keys=keys)

    def _save(self, key_file: Path) -> None:
        """Save identity to file (with restrictive permissions)"""
        data = {
            "agent_id": self.agent_id,
            "seed": self.keys.seed.hex(),
            "created_at": self.keys.created_at,
            "algorithm": self.keys.algorithm.value,
            "did": self.did
        }

        # Write with restrictive permissions (owner only)
        with open(key_file, "wb") as f:
            f.write(json.dumps(data, indent=2).encode())

        # Set file permissions to owner-only (Unix)
        try:
            os.chmod(key_file, 0o600)
        except (OSError, AttributeError):
            pass  # Windows or permission error

    def sign(self, data: bytes) -> 'Signature':
        """
        Sign data with quantum-safe HMAC-SHA3-256.

        Args:
            data: Bytes to sign

        Returns:
            Signature object
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Include timestamp in signed data to prevent replay
        message = data + timestamp.encode()

        # HMAC-SHA3-256 signature
        sig_bytes = hmac.new(
            self.keys.signing_key,
            message,
            hashlib.sha3_256
        ).digest()

        return Signature(
            value=sig_bytes.hex(),
            algorithm=SignatureAlgorithm.HMAC_SHA3_256,
            timestamp=timestamp,
            signer_did=self.did,
            signer_commitment=self.keys.commitment
        )

    def sign_decision(self, decision_data: Dict[str, Any]) -> 'Signature':
        """
        Sign a decision record.

        Args:
            decision_data: Decision dictionary to sign

        Returns:
            Signature for the decision
        """
        # Canonical JSON encoding
        canonical = json.dumps(decision_data, sort_keys=True, separators=(',', ':'))
        return self.sign(canonical.encode())

    def verify(self, data: bytes, signature: 'Signature') -> bool:
        """
        Verify a signature.

        Args:
            data: Original data that was signed
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        if signature.signer_did != self.did:
            return False

        # Reconstruct message with timestamp
        message = data + signature.timestamp.encode()

        # Compute expected signature
        expected = hmac.new(
            self.keys.signing_key,
            message,
            hashlib.sha3_256
        ).digest()

        # Constant-time comparison
        return hmac.compare_digest(expected.hex(), signature.value)

    def create_commitment(self, data: bytes) -> 'HashCommitment':
        """
        Create a hash commitment (quantum-safe).

        This can be published before revealing data,
        proving you knew the data at commitment time.

        Args:
            data: Data to commit to

        Returns:
            HashCommitment that can be verified later
        """
        nonce = secrets.token_bytes(16)
        commitment_hash = hashlib.sha3_256(data + nonce + self.keys.identity_key).hexdigest()

        return HashCommitment(
            commitment=commitment_hash,
            nonce=nonce.hex(),
            timestamp=datetime.utcnow().isoformat() + "Z",
            signer_did=self.did
        )

    def export_public(self) -> Dict[str, Any]:
        """Export public identity info (safe to share)"""
        return {
            "did": self.did,
            "agent_id": self.agent_id,
            "commitment": self.keys.commitment,
            "algorithm": self.keys.algorithm.value,
            "created_at": self.keys.created_at,
            "quantum_safe": True
        }


@dataclass
class Signature:
    """Digital signature with metadata"""
    value: str                      # Hex-encoded signature
    algorithm: SignatureAlgorithm
    timestamp: str                  # ISO8601 timestamp
    signer_did: str                 # DID of signer
    signer_commitment: str          # Public key commitment

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "algorithm": self.algorithm.value,
            "timestamp": self.timestamp,
            "signer_did": self.signer_did,
            "signer_commitment": self.signer_commitment,
            "quantum_safe": True
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signature':
        return cls(
            value=data["value"],
            algorithm=SignatureAlgorithm(data["algorithm"]),
            timestamp=data["timestamp"],
            signer_did=data["signer_did"],
            signer_commitment=data["signer_commitment"]
        )


@dataclass
class HashCommitment:
    """
    Hash-based commitment (quantum-safe).

    Allows proving knowledge of data without revealing it.
    Reveal nonce later to prove commitment.
    """
    commitment: str    # SHA3-256 hash
    nonce: str         # Random nonce (reveal to verify)
    timestamp: str
    signer_did: str

    def verify(self, data: bytes, identity_key: bytes) -> bool:
        """Verify this commitment matches the data"""
        nonce_bytes = bytes.fromhex(self.nonce)
        expected = hashlib.sha3_256(data + nonce_bytes + identity_key).hexdigest()
        return hmac.compare_digest(expected, self.commitment)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commitment": self.commitment,
            "timestamp": self.timestamp,
            "signer_did": self.signer_did,
            "type": "hash-commitment-sha3-256",
            "quantum_safe": True
        }


def verify_signature_standalone(
    data: bytes,
    signature: Signature,
    public_commitment: str
) -> bool:
    """
    Verify signature without full identity (for auditors).

    Note: This requires the signing key to be known, which
    is not possible with HMAC. For full standalone verification,
    use post-quantum signatures when available.

    Returns:
        False (standalone HMAC verification not possible)
    """
    # HMAC requires shared secret - use for self-verification only
    # For third-party verification, need asymmetric post-quantum signatures
    return False


# === DEMO ===
if __name__ == "__main__":
    print("HONEST CHAIN - Quantum-Ready Identity")
    print("=" * 50)

    # Create identity
    identity = AgentIdentity.create("demo-agent-quantum")

    print(f"\nAgent ID: {identity.agent_id}")
    print(f"DID: {identity.did}")
    print(f"Public commitment: {identity.public_key_hash[:32]}...")
    print(f"Algorithm: {identity.keys.algorithm.value}")
    print(f"Quantum-safe: Yes (SHA3-256)")

    # Sign some data
    test_data = b"This is a test decision"
    signature = identity.sign(test_data)

    print(f"\nSignature: {signature.value[:32]}...")
    print(f"Timestamp: {signature.timestamp}")

    # Verify
    is_valid = identity.verify(test_data, signature)
    print(f"Verified: {is_valid}")

    # Create commitment
    commitment = identity.create_commitment(b"secret data")
    print(f"\nCommitment: {commitment.commitment[:32]}...")

    print("\nQuantum-ready identity system operational!")
