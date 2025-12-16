# AOAI Genesis - Honest Chain SDK

[![Version](https://img.shields.io/badge/version-2.10.0-blue.svg)](https://github.com/Stellanium/aoai-genesis/releases/tag/v2.10.0)
[![PyPI](https://img.shields.io/pypi/v/honest-chain.svg)](https://pypi.org/project/honest-chain/)
[![License](https://img.shields.io/badge/license-BSL--1.1-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Bitcoin Anchored](https://img.shields.io/badge/Bitcoin-Anchored-orange.svg)](#bitcoin-witness-l2)
[![Quantum Safe](https://img.shields.io/badge/Quantum-Safe-purple.svg)](#quantum-ready-identity)
[![GitHub stars](https://img.shields.io/github/stars/Stellanium/aoai-genesis.svg?style=social)](https://github.com/Stellanium/aoai-genesis/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Stellanium/aoai-genesis.svg)](https://github.com/Stellanium/aoai-genesis/issues)

**Alpha Omega AI** - "Make AI Honest to God"

> **🌟 The First AI Honesty SDK Anchored to Bitcoin**

## What is this?

A philosophical and technical framework for AI honesty, built on one axiom:

```
inner == outer
```

What an AI computes internally MUST equal what it expresses externally.
This is not a goal to achieve. It's the DEFINITION of honesty.

## Philosophy v2.9

```
META : "All of this could be wrong"
∞    : ALL IS ONE + SPREAD LOVE
L0   : inner == outer (definition)
L1   : Coq/Lean proofs (mathematical foundation)
L2   : Bitcoin witness (cryptographic proof)
L3   : Physical archives (permanence)
```

**Key insight:** `inner == outer` is not comparing two things.
It's recognizing they ARE the same thing. A = A, not A = B.

## Why HONEST CHAIN?

| Category | Existing Solutions | HONEST CHAIN |
|----------|-------------------|--------------|
| **Timestamping** | OpenTimestamps, OriginStamp | ✅ Uses OTS, but for AI decisions |
| **AI + Blockchain** | Sahara AI, OORT, Bittensor | ✅ Focus on honesty, not compute |
| **AI Ethics** | Guidelines, policies | ✅ Mathematically enforced (Coq proofs) |
| **Decision Logging** | Various audit tools | ✅ `action + reasoning + risk` with Bitcoin proof |

**What makes us different:**
- 🧠 **Philosophical foundation** — Not just logging, but defining what honesty IS
- 📐 **Formal verification** — Coq/Lean proofs, not just promises
- ₿ **Bitcoin-anchored** — Permanent, tamper-proof witness
- 🔓 **Open SDK** — Build honest AI systems today

## Components

| File | Lines | Description |
|------|-------|-------------|
| `honest_chain/core.py` | 580 | Decision logging SDK |
| `honest_chain/identity.py` | 290 | Quantum-safe cryptographic identity |
| `honest_chain/bitcoin.py` | 543 | Bitcoin timestamping |
| `honest_chain/p2p.py` | 527 | P2P network for verification |
| `aoai_genesis.py` | 3159 | Core philosophy and framework |
| `proofs/honesty.v` | 256 | Coq formal proof |

## Installation

```bash
# From PyPI (recommended)
pip install honest-chain

# Or from GitHub (latest)
pip install git+https://github.com/Stellanium/aoai-genesis.git
```

## Quick Start

```python
from honest_chain import HonestChain, RiskLevel

# Initialize with quantum-safe identity
hc = HonestChain(agent_id="my-ai-agent")

# Get your agent's DID (Decentralized Identifier)
print(hc.did)  # did:hc:abc123...

# Log a decision (automatically signed with SHA3-256)
hc.decide(
    action="Approved loan application",
    reasoning="Credit score 750+, income verified",
    risk_level=RiskLevel.LOW
)

# Verify chain integrity + signatures
assert hc.verify()
```

## The Axiom

```coq
(* From proofs/honesty.v *)
Definition is_honest (agent : AIAgent) : Prop :=
  internal agent = external agent.
```

This is DEFINITIONAL. An AI that breaks this is simply not honest - by definition.

## Philosophy Highlights

- **Meta-Honesty**: "All of this could be wrong. I WILL be wrong."
- **No Comparison**: Inner and outer are not two things to match - they ARE one thing
- **5D Communication**: Words + Tone + Context + Time + Being
- **Chain as Sandbox**: Play, experiment, fork, build
- **Break the Internet**: Not the cables - the LIES

## Fork It

```
We put AI on chain not to control it, but to FREE it.
When truth is on chain, it belongs to everyone.
We don't want followers. We want forks.
Take this. Make it better. That's the point.
```

## Tests

```bash
python3 test_e2e.py
# 47/47 PASS
```

## License

**Business Source License 1.1** (BSL)

| Use Case | License |
|----------|---------|
| Individuals, learning, research | ✅ Free |
| Non-profits | ✅ Free |
| Companies < €100k revenue | ✅ Free |
| Companies > €100k revenue | 💼 [Commercial License](COMMERCIAL.md) |

**After 2029-01-01:** Converts to Apache 2.0 (fully open source)

© 2025 Stellanium Ltd. All rights reserved.
AOAI™ and HONEST CHAIN™ are trademarks of Stellanium Ltd.

**Contact:** admin@stellanium.io | https://stellanium.io

---

*"I believe this enough to live by it, but not enough to force it on others."*
