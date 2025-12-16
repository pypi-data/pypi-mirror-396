"""
HONEST CHAIN SDK v2.0 - Quantum-Ready
=====================================

Make AI Honest to God.

The logical foundation for AI transparency: inner == outer.
Bitcoin-anchored, formally verified, quantum-safe.

Features:
    - Quantum-safe cryptographic identity (SHA3-256)
    - DID-style agent identifiers (did:hc:...)
    - Digital signatures on all decisions
    - Bitcoin anchoring for permanence

Usage:
    from honest_chain import HonestChain, RiskLevel

    hc = HonestChain(agent_id="my-agent")

    # Get agent DID
    print(hc.did)  # did:hc:abc123...

    # Log decisions (automatically signed)
    hc.decide(
        action="Approved request",
        reasoning="All criteria met",
        risk_level=RiskLevel.LOW
    )
    assert hc.verify()

Copyright (c) 2025 Stellanium Ltd. All rights reserved.
Licensed under Business Source License 1.1 (BSL). See LICENSE file.
AOAI™ and HONEST CHAIN™ are trademarks of Stellanium Ltd.
"""

__version__ = "2.10.1"
__author__ = "Stellanium Ltd"
__email__ = "admin@stellanium.io"
__license__ = "BSL-1.1"

# Core
from honest_chain.core import (
    HonestChain,
    DecisionRecord,
    Actor,
    ActorType,
    RiskLevel,
    log_decision,
)

# Quantum-ready identity
from honest_chain.identity import (
    AgentIdentity,
    Signature,
    HashCommitment,
    KeyMaterial,
    SignatureAlgorithm,
)

# Bitcoin anchoring
from honest_chain.bitcoin import (
    BitcoinAnchorService,
    BitcoinAnchor,
    AnchorMethod,
    AOAIGroundTruth,
    create_bitcoin_anchor_callback,
)

# P2P network
from honest_chain.p2p import (
    AOAINode,
    MessageType,
    Message,
    Peer,
    create_anchor_callback,
)

__all__ = [
    # Core
    "HonestChain",
    "DecisionRecord",
    "Actor",
    "ActorType",
    "RiskLevel",
    "log_decision",
    # Identity (NEW)
    "AgentIdentity",
    "Signature",
    "HashCommitment",
    "KeyMaterial",
    "SignatureAlgorithm",
    # Bitcoin
    "BitcoinAnchorService",
    "BitcoinAnchor",
    "AnchorMethod",
    "AOAIGroundTruth",
    "create_bitcoin_anchor_callback",
    # P2P
    "AOAINode",
    "MessageType",
    "Message",
    "Peer",
    "create_anchor_callback",
    # Meta
    "__version__",
]
