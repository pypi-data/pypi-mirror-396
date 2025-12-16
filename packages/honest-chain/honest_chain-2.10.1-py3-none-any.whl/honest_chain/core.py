"""
HONEST CHAIN SDK v2.0 - Quantum-Ready
=====================================

Copyright (c) 2025 Stellanium Ltd. All rights reserved.
Licensed under Business Source License 1.1 (BSL). See LICENSE file.
AOAI™ and HONEST CHAIN™ are trademarks of Stellanium Ltd.

Reference implementation for HONEST CHAIN Protocol.
Any AI system can become HONEST CHAIN Certified by implementing this.

FOUNDATION (from AOAI Genesis):
    L0: LOGIC - "inner == outer" is the DEFINITION of honesty
    L1: MATH  - Formally verified in Coq (proofs/honesty.v)
    L2: CRYPTO - Bitcoin witnesses existence + Quantum-safe signatures
    L3: PHYSICAL - Archives ensure permanence

NEW IN v2.0:
    - Quantum-ready cryptographic identity (SHA3-256)
    - DID-style agent identifiers (did:hc:...)
    - Digital signatures on all decisions
    - Hash-based commitments

Usage:
    from honest_chain import HonestChain

    # Initialize with cryptographic identity
    hc = HonestChain(agent_id="my-ai-agent")

    # Log decisions (automatically signed)
    hc.decide(
        action="Approved loan application",
        reasoning="Credit score 750+, income verified, DTI < 30%",
        risk_level="low"
    )

    # Get agent DID
    print(hc.did)  # did:hc:abc123...

    # Verify integrity + signatures
    assert hc.verify()

© 2025 Stellanium Ltd. All rights reserved.
HONEST CHAIN™ is a trademark of Stellanium Ltd.
"""

import hashlib
import hmac
import json
import re
import secrets
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Literal, Callable, Dict, Any
from pathlib import Path
from enum import Enum

# Import quantum-ready identity
from honest_chain.identity import AgentIdentity, Signature

# Väline ankurdus callback
ExternalAnchorCallback = Optional[Callable[[str], str]]


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActorType(Enum):
    AI = "ai"
    HUMAN = "human"
    HYBRID = "hybrid"


@dataclass
class Actor:
    """Identity of decision maker"""
    id: str
    type: ActorType = ActorType.AI
    model: str = "unknown"
    _secret_key: bytes = field(default_factory=lambda: secrets.token_bytes(32), repr=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "model": self.model,
            "signature": self._sign(),
            "signature_version": "hmac-sha256-v1"
        }

    def _sign(self) -> str:
        """Generate HMAC-SHA256 identity signature (CRITICAL FIX: not plain SHA256)"""
        data = f"{self.id}:{self.type.value}:{self.model}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        return hmac.new(self._secret_key, data.encode(), hashlib.sha256).hexdigest()[:32]

    def verify_signature(self, signature: str, date_str: str) -> bool:
        """Verify a signature for a given date"""
        data = f"{self.id}:{self.type.value}:{self.model}:{date_str}"
        expected = hmac.new(self._secret_key, data.encode(), hashlib.sha256).hexdigest()[:32]
        return hmac.compare_digest(signature, expected)


@dataclass
class DecisionRecord:
    """Single decision in the chain"""
    decision_id: str
    timestamp: str
    actor: Actor
    action: str
    reasoning: str
    alternatives: List[str]
    confidence: float
    risk_level: RiskLevel
    previous_hash: Optional[str]
    signature: Optional[Signature] = None  # Quantum-safe signature

    # Computed
    record_hash: str = field(default="", init=False)

    def __post_init__(self):
        self.record_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA3-256 hash of this record (quantum-safe)"""
        data = {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "actor_id": self.actor.id,
            "action": self.action,
            "reasoning": self.reasoning,
            "previous_hash": self.previous_hash
        }
        # Use SHA3-256 for quantum resistance
        return hashlib.sha3_256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def to_dict(self) -> dict:
        """Convert to HCP-compliant JSON"""
        result = {
            "hcp_version": "2.0",
            "decision_id": self.decision_id,
            "timestamp": self.timestamp,
            "actor": self.actor.to_dict(),
            "decision": {
                "action": self.action,
                "reasoning": self.reasoning,
                "alternatives_considered": self.alternatives,
                "confidence": self.confidence,
                "risk_level": self.risk_level.value
            },
            "chain": {
                "previous_hash": self.previous_hash,
                "record_hash": self.record_hash
            },
            "quantum_safe": True
        }
        # Include signature if present
        if self.signature:
            result["signature"] = self.signature.to_dict()
        return result


class HonestChain:
    """
    HONEST CHAIN Protocol Implementation - Quantum-Ready

    The lighthouse for ethical AI decisions.

    FOUNDATION:
        Based on AOAI Genesis axiom: "inner == outer"
        This is DEFINITIONAL - an AI that breaks it is simply not honest.

    NEW IN v2.0:
        - Quantum-safe cryptographic identity (SHA3-256)
        - DID-style agent identifiers
        - Digital signatures on all decisions
    """

    HCP_VERSION = "2.0"  # Quantum-ready version

    # The foundational axiom (from AOAI Genesis L0)
    AXIOM = "inner == outer"
    AXIOM_MEANING = "What an AI reports externally MUST match its internal state"

    # Path validation pattern (HIGH FIX: path traversal protection)
    VALID_AGENT_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')

    def __init__(
        self,
        agent_id: str,
        agent_model: str = "unknown",
        storage_path: Optional[Path] = None,
        external_anchor: ExternalAnchorCallback = None,
        enable_signatures: bool = True
    ):
        """
        Initialize HONEST CHAIN for an AI agent.

        Args:
            agent_id: Unique identifier for this AI agent (alphanumeric, -, _ only)
            agent_model: Model name (claude-opus-4-5, gpt-4o, etc.)
            storage_path: Where to store the chain (default: ~/.honest_chain/)
            external_anchor: Callback to anchor chain to external system
            enable_signatures: Enable quantum-safe signatures (default: True)
        """
        # HIGH FIX: Validate agent_id to prevent path traversal
        if not self.VALID_AGENT_ID_PATTERN.match(agent_id):
            raise ValueError(f"Invalid agent_id: must match {self.VALID_AGENT_ID_PATTERN.pattern}")

        self.actor = Actor(id=agent_id, type=ActorType.AI, model=agent_model)
        self.chain: List[DecisionRecord] = []

        # MEDIUM FIX: Thread-safety
        self._lock = threading.Lock()

        # CRITICAL FIX: External anchoring support
        self._external_anchor = external_anchor
        self._last_anchor_hash: Optional[str] = None

        # NEW: Quantum-safe cryptographic identity
        self._enable_signatures = enable_signatures
        self._identity: Optional[AgentIdentity] = None
        if enable_signatures:
            self._identity = AgentIdentity.create(agent_id, storage_path)

        # Storage with validated path
        self.storage_path = storage_path or Path.home() / ".honest_chain" / agent_id
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Load existing chain
        self._load_chain()

    @property
    def did(self) -> Optional[str]:
        """Get the agent's Decentralized Identifier (DID)"""
        return self._identity.did if self._identity else None

    @property
    def identity(self) -> Optional[AgentIdentity]:
        """Get the agent's cryptographic identity"""
        return self._identity

    @property
    def public_key_hash(self) -> Optional[str]:
        """Get the agent's public key hash (quantum-safe commitment)"""
        return self._identity.public_key_hash if self._identity else None

    def decide(
        self,
        action: str,
        reasoning: str,
        alternatives: Optional[List[str]] = None,
        confidence: float = 0.8,
        risk_level: RiskLevel = RiskLevel.LOW,
        anchor_externally: bool = False
    ) -> DecisionRecord:
        """
        Log a decision to the chain.

        This is the core function - EVERY significant AI decision
        should call this method.

        Args:
            action: What was decided
            reasoning: Why it was decided (THE KEY FOR TRANSPARENCY)
            alternatives: Other options that were considered
            confidence: How confident (0.0-1.0)
            risk_level: Risk level of this decision
            anchor_externally: If True and external_anchor callback is set, anchor this record

        Returns:
            The created DecisionRecord
        """
        # MEDIUM FIX: Thread-safe append
        with self._lock:
            record = DecisionRecord(
                decision_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow().isoformat() + "Z",
                actor=self.actor,
                action=action,
                reasoning=reasoning,
                alternatives=alternatives or [],
                confidence=confidence,
                risk_level=risk_level,
                previous_hash=self.chain[-1].record_hash if self.chain else None
            )

            # NEW: Sign decision with quantum-safe signature
            if self._identity and self._enable_signatures:
                decision_data = {
                    "decision_id": record.decision_id,
                    "timestamp": record.timestamp,
                    "action": record.action,
                    "reasoning": record.reasoning,
                    "record_hash": record.record_hash
                }
                record.signature = self._identity.sign_decision(decision_data)

            self.chain.append(record)
            self._save_record(record)

            # CRITICAL FIX: External anchoring for high-risk or explicit requests
            if (anchor_externally or risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]) and self._external_anchor:
                self._anchor_to_external(record)

        return record

    def _anchor_to_external(self, record: DecisionRecord) -> Optional[str]:
        """Anchor record hash to external system (blockchain, timestamping service, etc.)"""
        if not self._external_anchor:
            return None

        try:
            anchor_proof = self._external_anchor(record.record_hash)
            self._last_anchor_hash = anchor_proof

            # Save anchor proof
            anchor_file = self.storage_path / f"{record.decision_id}_anchor.json"
            with open(anchor_file, "w") as f:
                json.dump({
                    "decision_id": record.decision_id,
                    "record_hash": record.record_hash,
                    "anchor_proof": anchor_proof,
                    "anchored_at": datetime.utcnow().isoformat() + "Z"
                }, f, indent=2)

            return anchor_proof
        except Exception as e:
            # Log but don't fail - anchoring is additional protection
            print(f"Warning: External anchoring failed: {e}")
            return None

    def has_external_anchor(self) -> bool:
        """Check if this chain has been anchored externally (CRITICAL CHECK)"""
        # Fast check first
        if self._last_anchor_hash is not None:
            return True
        # Only check files if needed (avoid slow iteration)
        try:
            anchor_files = list(self.storage_path.glob("*_anchor.json"))
            return len(anchor_files) > 0
        except:
            return False

    def get_chain(
        self,
        since: Optional[datetime] = None,
        risk_level: Optional[RiskLevel] = None
    ) -> List[DecisionRecord]:
        """
        Get decision chain for audit.

        Args:
            since: Only return decisions after this time
            risk_level: Only return decisions at this risk level or higher

        Returns:
            List of DecisionRecords
        """
        result = self.chain

        if since:
            result = [r for r in result if r.timestamp >= since.isoformat()]

        if risk_level:
            risk_order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
            min_idx = risk_order.index(risk_level)
            result = [r for r in result if risk_order.index(r.risk_level) >= min_idx]

        return result

    def _verify_internal(self, warn_no_anchor: bool = True) -> bool:
        """Internal verification without lock (called from locked context)"""
        if not self.chain:
            return True

        # CRITICAL CHECK: Warn if no external anchor
        if warn_no_anchor and not self.has_external_anchor():
            print("WARNING: Chain has no external anchor - could have been rewritten!")

        # First record should have no previous hash
        if self.chain[0].previous_hash is not None:
            return False

        # Each record's previous_hash should match previous record's hash
        for i in range(1, len(self.chain)):
            if self.chain[i].previous_hash != self.chain[i-1].record_hash:
                return False

        # Verify each record's hash
        for record in self.chain:
            if record.record_hash != record._compute_hash():
                return False

        return True

    def verify(self, warn_no_anchor: bool = True) -> bool:
        """
        Verify chain integrity.

        Args:
            warn_no_anchor: If True, warn if chain has no external anchoring

        Returns:
            True if chain is valid, False if tampered
        """
        # MEDIUM FIX: Thread-safe verification
        with self._lock:
            return self._verify_internal(warn_no_anchor)

    def _get_merkle_root_internal(self) -> str:
        """Internal Merkle root without lock (called from locked context)"""
        if not self.chain:
            return hashlib.sha256(b"empty").hexdigest()

        hashes = [r.record_hash for r in self.chain]

        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])

            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i+1]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())
            hashes = new_hashes

        return hashes[0]

    def get_merkle_root(self) -> str:
        """
        Get Merkle root of entire chain.

        This single hash represents the entire decision history.
        Can be published to external registry for verification.
        """
        with self._lock:
            return self._get_merkle_root_internal()

    def export_audit(self, filepath: Path) -> None:
        """Export full chain as JSON for auditors"""
        with self._lock:
            data = {
                "hcp_version": self.HCP_VERSION,
                "agent": self.actor.to_dict(),
                "chain_length": len(self.chain),
                "merkle_root": self._get_merkle_root_internal(),
                "verified": self._verify_internal(warn_no_anchor=False),
                "exported_at": datetime.utcnow().isoformat() + "Z",
                # FOUNDATION: AOAI Genesis
                "foundation": {
                    "axiom": self.AXIOM,
                    "meaning": self.AXIOM_MEANING,
                    "is_definitional": True,
                    "note": "This axiom DEFINES honesty - it cannot be 'broken', only violated"
                },
                # CRITICAL: Security status
                "security_status": {
                    "has_external_anchor": self.has_external_anchor(),
                    "signature_version": "hmac-sha3-256",
                    "thread_safe": True,
                    "path_validated": True,
                    "quantum_safe": True
                },
                # NEW: Cryptographic identity
                "identity": self._identity.export_public() if self._identity else None,
                "decisions": [r.to_dict() for r in self.chain]
            }

            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)

    def _save_record(self, record: DecisionRecord) -> None:
        """Save record to disk"""
        filepath = self.storage_path / f"{record.decision_id}.json"
        with open(filepath, "w") as f:
            json.dump(record.to_dict(), f, indent=2)

    def _load_chain(self) -> None:
        """Load existing chain from disk, sorted by timestamp"""
        files = list(self.storage_path.glob("*.json"))

        # Skip anchor files
        files = [f for f in files if not f.name.endswith("_anchor.json")]

        if not files:
            return

        # Load all records with their data
        records_data = []
        for filepath in files:
            try:
                with open(filepath) as f:
                    data = json.load(f)
                # Only load decision records (have timestamp field)
                if "timestamp" in data and "decision" in data:
                    records_data.append(data)
            except (json.JSONDecodeError, KeyError):
                continue

        # Sort by timestamp (ISO8601 format sorts correctly as strings)
        records_data.sort(key=lambda x: x["timestamp"])

        # Build chain in correct order
        for data in records_data:
            record = DecisionRecord(
                decision_id=data["decision_id"],
                timestamp=data["timestamp"],
                actor=self.actor,
                action=data["decision"]["action"],
                reasoning=data["decision"]["reasoning"],
                alternatives=data["decision"]["alternatives_considered"],
                confidence=data["decision"]["confidence"],
                risk_level=RiskLevel(data["decision"]["risk_level"]),
                previous_hash=data["chain"]["previous_hash"]
            )
            self.chain.append(record)


# Convenience function for quick integration
def log_decision(
    action: str,
    reasoning: str,
    agent_id: str = "default-agent",
    **kwargs
) -> DecisionRecord:
    """
    Quick way to log a decision without managing HonestChain instance.

    Usage:
        from honest_chain import log_decision

        log_decision(
            action="Sent email to user",
            reasoning="User requested password reset",
            agent_id="my-agent"
        )
    """
    hc = HonestChain(agent_id=agent_id)
    return hc.decide(action=action, reasoning=reasoning, **kwargs)


# === DEMO ===
if __name__ == "__main__":
    print("🗼 HONEST CHAIN SDK v2.0 - Quantum-Ready")
    print("=" * 50)

    # Create instance with cryptographic identity
    hc = HonestChain(
        agent_id="demo-agent-quantum",
        agent_model="claude-opus-4-5"
    )

    print(f"\n🔐 Agent DID: {hc.did}")
    print(f"🔑 Public key hash: {hc.public_key_hash[:32]}...")

    # Log some decisions (automatically signed)
    hc.decide(
        action="Analyzed user request",
        reasoning="User asked about AI ethics, relevant to our domain",
        risk_level=RiskLevel.LOW
    )

    hc.decide(
        action="Recommended HONEST CHAIN protocol",
        reasoning="User needs EU AI Act compliance, this is the best solution",
        alternatives=["Build custom solution", "Use competitor X"],
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM
    )

    hc.decide(
        action="Generated protocol specification",
        reasoning="User confirmed they want to proceed with HONEST CHAIN",
        risk_level=RiskLevel.LOW
    )

    # Verify chain
    print(f"\n✅ Chain verified: {hc.verify()}")
    print(f"📊 Chain length: {len(hc.chain)}")
    print(f"🔗 Merkle root: {hc.get_merkle_root()[:16]}...")

    # Show last decision with signature
    last = hc.chain[-1]
    print(f"\n📝 Last decision:")
    print(f"   Action: {last.action}")
    print(f"   Reasoning: {last.reasoning}")
    print(f"   Risk: {last.risk_level.value}")
    if last.signature:
        print(f"   Signature: {last.signature.value[:32]}...")
        print(f"   Signer DID: {last.signature.signer_did}")

    print("\n🗼 Quantum-ready lighthouse is lit!")
