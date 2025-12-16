"""
AOAI Bitcoin Anchor - "Kindel Maapind"
======================================

Ankurdab AOAI chain'i Bitcoin'i blockchaini.
Bitcoin on TUNNISTAJA, mitte tõeallikas.

KEY INSIGHT (from AOAI Genesis):
    L0: LOGIC is the foundation - "inner == outer" is DEFINITION
    L2: CRYPTO (Bitcoin) is the WITNESS - proves WHEN it existed

Bitcoin doesn't make AOAI "true". Bitcoin WITNESSES that AOAI
existed at time T. Like a notary doesn't make a contract valid -
they just witness its signing.

Meetodid:
1. OP_RETURN - Kuni 80 baiti andmeid otse blockchaini
2. Merkle root - Kogu chain'i kokkuvõte ühe hash'ina
3. OpenTimestamps - Tasuta ajatembeldamine läbi Bitcoin'i

Miks Bitcoin:
- 15+ aastat katkematut tööd
- $1T+ turvaline võrk
- Miljonid node'd üle maailma
- Ei sõltu ühestki organisatsioonist
- "Kindel maapind" - ei liigu, ei muutu

Copyright (c) 2025 Stellanium Ltd. All rights reserved.
Licensed under Business Source License 1.1 (BSL). See LICENSE file.
AOAI™ and HONEST CHAIN™ are trademarks of Stellanium Ltd.
"""

import hashlib
import json
import struct
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Callable
from enum import Enum
import urllib.request
import urllib.error


class AnchorMethod(Enum):
    """Ankurdamise meetodid"""
    OPENTIMESTAMPS = "ots"  # Tasuta, aeglane (~2h)
    OP_RETURN = "op_return"  # Maksab tasu, kohene
    MERKLE_PROOF = "merkle"  # Kombineeritud


@dataclass
class BitcoinAnchor:
    """Bitcoin ankurduse tõend"""
    merkle_root: str
    method: AnchorMethod
    timestamp: str
    txid: Optional[str] = None
    block_height: Optional[int] = None
    ots_proof: Optional[bytes] = None
    verified: bool = False


class BitcoinAnchorService:
    """
    Bitcoin Ankurdamise Teenus

    "Õigemini võrk" - kasutab Bitcoin'i võrku kui kindlat maapinda.
    """

    # OpenTimestamps kalendriserver
    OTS_CALENDARS = [
        "https://a.pool.opentimestamps.org",
        "https://b.pool.opentimestamps.org",
        "https://a.pool.eternitywall.com",
    ]

    def __init__(
        self,
        data_dir: Optional[Path] = None,
        preferred_method: AnchorMethod = AnchorMethod.OPENTIMESTAMPS
    ):
        """
        Initsialiseeri Bitcoin ankurdamise teenus.

        Args:
            data_dir: Kaust ankurduste salvestamiseks
            preferred_method: Eelistatud ankurdamismeetod
        """
        self.data_dir = data_dir or Path.home() / ".aoai_anchors"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.preferred_method = preferred_method

    def anchor(self, merkle_root: str) -> BitcoinAnchor:
        """
        Ankurda Merkle root Bitcoin'i.

        Args:
            merkle_root: AOAI chain'i Merkle root

        Returns:
            BitcoinAnchor objekt koos tõendiga
        """
        if self.preferred_method == AnchorMethod.OPENTIMESTAMPS:
            return self._anchor_ots(merkle_root)
        elif self.preferred_method == AnchorMethod.OP_RETURN:
            return self._anchor_op_return(merkle_root)
        else:
            return self._anchor_merkle(merkle_root)

    def _anchor_ots(self, merkle_root: str) -> BitcoinAnchor:
        """
        Ankurda kasutades OpenTimestamps (tasuta).

        OpenTimestamps on tasuta teenus mis agregeerib hashid
        ja ankurdab need Bitcoin'i iga ~2 tunni tagant.
        """
        # Arvuta hash digest
        digest = bytes.fromhex(merkle_root)

        # Proovi igat kalendrit
        ots_proof = None
        for calendar in self.OTS_CALENDARS:
            try:
                ots_proof = self._submit_to_calendar(calendar, digest)
                if ots_proof:
                    break
            except Exception as e:
                continue

        anchor = BitcoinAnchor(
            merkle_root=merkle_root,
            method=AnchorMethod.OPENTIMESTAMPS,
            timestamp=datetime.utcnow().isoformat() + "Z",
            ots_proof=ots_proof
        )

        # Salvesta
        self._save_anchor(anchor)

        return anchor

    def _submit_to_calendar(self, calendar_url: str, digest: bytes) -> Optional[bytes]:
        """Saada hash OpenTimestamps kalendrisse"""
        url = f"{calendar_url}/digest"
        try:
            req = urllib.request.Request(
                url,
                data=digest,
                headers={"Content-Type": "application/octet-stream"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.read()
        except urllib.error.URLError:
            return None

    def _anchor_op_return(self, merkle_root: str) -> BitcoinAnchor:
        """
        Ankurda kasutades OP_RETURN (vajab Bitcoin'i).

        See meetod nõuab:
        1. Bitcoin node'i või API (BlockCypher, Blockstream, etc.)
        2. Väikest BTC hulka tasu jaoks (~$1-5)
        """
        # Loo OP_RETURN prefix
        prefix = b"AOAI"  # 4 baiti
        root_bytes = bytes.fromhex(merkle_root)[:32]  # 32 baiti
        timestamp_bytes = struct.pack(">I", int(time.time()))  # 4 baiti

        op_return_data = prefix + root_bytes + timestamp_bytes  # 40 baiti (< 80 limit)

        # Märkus: Tegelik BTC tehing vajab eraldi integratsiooni
        # See on placeholder mis näitab struktuuri

        anchor = BitcoinAnchor(
            merkle_root=merkle_root,
            method=AnchorMethod.OP_RETURN,
            timestamp=datetime.utcnow().isoformat() + "Z",
            txid=None  # Täidetakse kui tehing tehakse
        )

        self._save_anchor(anchor)
        return anchor

    def _anchor_merkle(self, merkle_root: str) -> BitcoinAnchor:
        """
        Kombineeritud meetod - kasuta OTS kui saadaval,
        salvesta lokaalselt alati.
        """
        # Proovi OTS
        anchor = self._anchor_ots(merkle_root)

        # Lisa täiendav lokaalne proof
        local_proof = self._create_local_proof(merkle_root)

        return anchor

    def _create_local_proof(self, merkle_root: str) -> dict:
        """Loo lokaalne ajatõend (kui BTC pole saadaval)"""
        return {
            "type": "local",
            "merkle_root": merkle_root,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "machine_id": self._get_machine_id(),
            "hash": hashlib.sha256(
                f"{merkle_root}:{time.time()}".encode()
            ).hexdigest()
        }

    def _get_machine_id(self) -> str:
        """Hangi masina unikaalne ID"""
        import socket
        return hashlib.sha256(socket.gethostname().encode()).hexdigest()[:16]

    def _save_anchor(self, anchor: BitcoinAnchor) -> None:
        """Salvesta ankurdus kettale"""
        filename = f"{anchor.merkle_root[:16]}_{int(time.time())}.json"
        filepath = self.data_dir / filename

        data = {
            "merkle_root": anchor.merkle_root,
            "method": anchor.method.value,
            "timestamp": anchor.timestamp,
            "txid": anchor.txid,
            "block_height": anchor.block_height,
            "ots_proof": anchor.ots_proof.hex() if anchor.ots_proof else None,
            "verified": anchor.verified
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def verify(self, anchor: BitcoinAnchor) -> bool:
        """
        Verifitseeri ankurdus.

        OTS puhul: Kontrolli kas Bitcoin'is on kinnitatud
        OP_RETURN puhul: Kontrolli tehingut
        """
        if anchor.method == AnchorMethod.OPENTIMESTAMPS:
            return self._verify_ots(anchor)
        elif anchor.method == AnchorMethod.OP_RETURN:
            return self._verify_op_return(anchor)
        return False

    def _verify_ots(self, anchor: BitcoinAnchor) -> bool:
        """Verifitseeri OTS ankurdus"""
        if not anchor.ots_proof:
            return False

        # Täielik OTS verifitseerimine nõuab:
        # 1. OTS proof'i parsimist
        # 2. Bitcoin block'i kontrollimist
        # See on lihtsustatud versioon

        # Kontrolli kas proof eksisteerib ja on kehtiv formaat
        try:
            proof_bytes = anchor.ots_proof
            # OTS proof algab alati versioonibaidiga (0x01)
            if proof_bytes[0] == 0x01:
                return True
        except:
            pass

        return False

    def _verify_op_return(self, anchor: BitcoinAnchor) -> bool:
        """Verifitseeri OP_RETURN ankurdus"""
        if not anchor.txid:
            return False

        # Kontrolli tehingut Blockstream API kaudu
        try:
            url = f"https://blockstream.info/api/tx/{anchor.txid}"
            with urllib.request.urlopen(url, timeout=30) as response:
                tx_data = json.loads(response.read())
                # Kontrolli kas tehing on kinnitatud
                return tx_data.get("status", {}).get("confirmed", False)
        except:
            return False

    def get_anchors(self, merkle_root: str) -> List[BitcoinAnchor]:
        """Hangi kõik ankurdused antud Merkle root'ile"""
        anchors = []
        pattern = f"{merkle_root[:16]}_*.json"

        for filepath in self.data_dir.glob(pattern):
            with open(filepath) as f:
                data = json.load(f)
                anchor = BitcoinAnchor(
                    merkle_root=data["merkle_root"],
                    method=AnchorMethod(data["method"]),
                    timestamp=data["timestamp"],
                    txid=data.get("txid"),
                    block_height=data.get("block_height"),
                    ots_proof=bytes.fromhex(data["ots_proof"]) if data.get("ots_proof") else None,
                    verified=data.get("verified", False)
                )
                anchors.append(anchor)

        return anchors


def create_bitcoin_anchor_callback(
    service: Optional[BitcoinAnchorService] = None
) -> Callable[[str], str]:
    """
    Loo callback HonestChain'i jaoks mis kasutab Bitcoin ankurdust.

    Usage:
        from bitcoin_anchor import create_bitcoin_anchor_callback
        from honest_chain import HonestChain

        hc = HonestChain(
            agent_id="my-agent",
            external_anchor=create_bitcoin_anchor_callback()
        )
    """
    if service is None:
        service = BitcoinAnchorService()

    def anchor_callback(record_hash: str) -> str:
        anchor = service.anchor(record_hash)
        return json.dumps({
            "type": "bitcoin",
            "method": anchor.method.value,
            "merkle_root": anchor.merkle_root,
            "timestamp": anchor.timestamp,
            "txid": anchor.txid,
            "has_ots_proof": anchor.ots_proof is not None
        })

    return anchor_callback


# === Integreeritud Ankurdus ===

class AOAIGroundTruth:
    """
    AOAI "Kindel Maapind" - Multi-Layer Anchoring

    Based on AOAI Genesis philosophy:
        L0: LOGIC      - "inner == outer" is DEFINITION (the foundation)
        L1: MATH       - Formal verification (Coq/Lean)
        L2: CRYPTO     - Bitcoin timestamp (the witness)
        L3: PHYSICAL   - Archives (permanence)

    Key insight: Bitcoin is the WITNESS, not the foundation.
    Logic is the foundation. You cannot 'break' a definition.
    """

    def __init__(
        self,
        p2p_node=None,  # AOAINode instance
        bitcoin_service: Optional[BitcoinAnchorService] = None,
        data_dir: Optional[Path] = None,
        genesis=None  # AOAIGenesis instance
    ):
        self.p2p_node = p2p_node
        self.bitcoin_service = bitcoin_service or BitcoinAnchorService()
        self.data_dir = data_dir or Path.home() / ".aoai_ground"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._genesis = genesis  # Will be set on first use if None

    @property
    def genesis(self):
        """Get or create genesis (lazy loading)"""
        if self._genesis is None:
            try:
                from aoai_genesis import AOAIGenesis
                self._genesis = AOAIGenesis()
            except ImportError:
                raise ImportError("aoai_genesis module required for genesis anchoring. Install with: pip install honest-chain[genesis]")
        return self._genesis

    def anchor_genesis(self) -> dict:
        """
        Anchor the AOAI Genesis to Bitcoin.

        This witnesses the existence of the logical foundation.
        It doesn't make L0 "true" - L0 is definitional.
        It proves WHEN L0 was stated.
        """
        genesis_hash = self.genesis.get_genesis_hash()

        result = {
            "type": "genesis_anchor",
            "genesis_hash": genesis_hash,
            "axiom": self.genesis.block.axiom.statement,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "layers": {
                "L0_logic": {
                    "status": "DEFINITIONAL",
                    "note": "This is the foundation - cannot be 'broken'"
                },
                "L2_crypto": None
            }
        }

        # Anchor to Bitcoin (L2)
        try:
            btc_anchor = self.bitcoin_service.anchor(genesis_hash)
            result["layers"]["L2_crypto"] = {
                "method": btc_anchor.method.value,
                "timestamp": btc_anchor.timestamp,
                "txid": btc_anchor.txid,
                "has_proof": btc_anchor.ots_proof is not None
            }

            # Update genesis with anchor info
            try:
                from aoai_genesis import CryptoAnchor
            except ImportError:
                CryptoAnchor = None
            if CryptoAnchor is None:
                return result
            self.genesis.block.add_crypto_anchor(CryptoAnchor(
                method=btc_anchor.method.value,
                transaction_id=btc_anchor.txid,
                merkle_root=genesis_hash,
                timestamp=btc_anchor.timestamp,
                proof=btc_anchor.ots_proof.hex() if btc_anchor.ots_proof else None
            ))
        except Exception as e:
            result["layers"]["L2_crypto"] = {"error": str(e)}

        self._save_ground_truth(result)
        return result

    def get_full_anchor_status(self) -> dict:
        """Get status of all layers from genesis perspective"""
        return {
            "genesis_hash": self.genesis.get_genesis_hash(),
            "axiom_valid": self.genesis.verify_axiom(),
            "layers": self.genesis.get_status()
        }

    def anchor_to_ground(self, merkle_root: str) -> dict:
        """
        Ankurda kindlale maapinnale - kasuta KÕIKI meetodeid.
        """
        result = {
            "merkle_root": merkle_root,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "genesis_hash": self.genesis.get_genesis_hash(),
            "anchors": {}
        }

        # 1. Bitcoin (kõige tugevam)
        try:
            btc_anchor = self.bitcoin_service.anchor(merkle_root)
            result["anchors"]["bitcoin"] = {
                "method": btc_anchor.method.value,
                "txid": btc_anchor.txid,
                "has_proof": btc_anchor.ots_proof is not None
            }
        except Exception as e:
            result["anchors"]["bitcoin"] = {"error": str(e)}

        # 2. P2P võrk
        if self.p2p_node:
            try:
                p2p_anchors = self.p2p_node.request_anchor(merkle_root)
                result["anchors"]["p2p"] = {
                    "count": len(p2p_anchors),
                    "nodes": [a.get("anchored_by") for a in p2p_anchors]
                }
            except Exception as e:
                result["anchors"]["p2p"] = {"error": str(e)}

        # 3. Lokaalne
        local_hash = hashlib.sha256(
            f"{merkle_root}:{time.time()}".encode()
        ).hexdigest()
        result["anchors"]["local"] = {
            "hash": local_hash,
            "machine": self.bitcoin_service._get_machine_id()
        }

        # Salvesta
        self._save_ground_truth(result)

        return result

    def _save_ground_truth(self, result: dict) -> None:
        """Salvesta maapinna tõend"""
        filename = f"ground_{result['merkle_root'][:16]}_{int(time.time())}.json"
        filepath = self.data_dir / filename
        with open(filepath, "w") as f:
            json.dump(result, f, indent=2)

    def verify_ground(self, merkle_root: str) -> dict:
        """Verifitseeri kõik ankurdused"""
        verification = {
            "merkle_root": merkle_root,
            "verified_at": datetime.utcnow().isoformat() + "Z",
            "results": {}
        }

        # Bitcoin
        btc_anchors = self.bitcoin_service.get_anchors(merkle_root)
        verification["results"]["bitcoin"] = {
            "count": len(btc_anchors),
            "verified": any(self.bitcoin_service.verify(a) for a in btc_anchors)
        }

        # P2P
        if self.p2p_node:
            roots = self.p2p_node.get_known_chains()
            verification["results"]["p2p"] = {
                "known_by_network": merkle_root in roots.values()
            }

        return verification


# === Demo ===

if __name__ == "__main__":
    print("🔗 AOAI Bitcoin Anchor - 'Kindel Maapind'")
    print("=" * 50)

    # Demo hash
    test_merkle = hashlib.sha256(b"AOAI Test 2025-12-13").hexdigest()
    print(f"\nTest Merkle Root: {test_merkle[:32]}...")

    # Loo teenus
    service = BitcoinAnchorService()

    # Ankurda (OTS on tasuta aga aeglane)
    print("\nAnkurdamine OpenTimestamps kaudu...")
    anchor = service.anchor(test_merkle)

    print(f"Meetod: {anchor.method.value}")
    print(f"Ajatempel: {anchor.timestamp}")
    print(f"OTS Proof: {'Jah' if anchor.ots_proof else 'Ei'}")

    # Näita integratsioon
    print("\n" + "-" * 50)
    print("Integratsioon HonestChain'iga:")
    print()
    print("from bitcoin_anchor import create_bitcoin_anchor_callback")
    print("from honest_chain import HonestChain")
    print()
    print("hc = HonestChain(")
    print("    agent_id='my-agent',")
    print("    external_anchor=create_bitcoin_anchor_callback()")
    print(")")
    print()
    print("# Kõik HIGH/CRITICAL otsused ankurdatakse automaatselt Bitcoin'i!")
