"""
AOAI P2P Node Network
=====================

Decentralized network for HONEST CHAIN propagation.
Ensures "peatamatus" (unstoppability) - no single point of failure.

Architecture:
- Each node stores its own chain + peers' chains
- Merkle roots are shared for quick verification
- Full chain sync on demand
- Gossip protocol for propagation

Copyright (c) 2025 Stellanium Ltd. All rights reserved.
Licensed under Business Source License 1.1 (BSL). See LICENSE file.
AOAI™ and HONEST CHAIN™ are trademarks of Stellanium Ltd.
"""

import asyncio
import hashlib
import json
import socket
import struct
import threading
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable
from enum import Enum
import secrets


class MessageType(Enum):
    """P2P message types"""
    PING = "ping"
    PONG = "pong"
    ANNOUNCE = "announce"           # Announce new merkle root
    REQUEST_CHAIN = "request_chain"  # Request full chain
    CHAIN_DATA = "chain_data"        # Full chain response
    PEER_LIST = "peer_list"          # Share known peers
    ANCHOR_REQUEST = "anchor_req"    # Request anchoring from peers
    ANCHOR_CONFIRM = "anchor_conf"   # Confirm anchor received


@dataclass
class Peer:
    """Known peer in the network"""
    node_id: str
    host: str
    port: int
    last_seen: float = 0.0
    merkle_root: str = ""
    trust_score: float = 1.0


@dataclass
class Message:
    """P2P message format"""
    msg_type: MessageType
    sender_id: str
    payload: dict
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    signature: str = ""

    def to_bytes(self) -> bytes:
        """Serialize message for network transmission"""
        data = {
            "type": self.msg_type.value,
            "sender": self.sender_id,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "signature": self.signature
        }
        json_bytes = json.dumps(data).encode('utf-8')
        # Prefix with length for framing
        return struct.pack('>I', len(json_bytes)) + json_bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Message':
        """Deserialize message from network"""
        json_data = json.loads(data.decode('utf-8'))
        return cls(
            msg_type=MessageType(json_data["type"]),
            sender_id=json_data["sender"],
            payload=json_data["payload"],
            timestamp=json_data["timestamp"],
            signature=json_data.get("signature", "")
        )


class AOAINode:
    """
    AOAI P2P Node - "Peatamatus" (Unstoppability)

    Each node is both client and server:
    - Stores local chain data
    - Connects to peers
    - Propagates updates
    - Provides anchoring service
    """

    VERSION = "1.0"
    DEFAULT_PORT = 7777  # AOAI port
    MAX_PEERS = 50
    PEER_TIMEOUT = 300  # 5 minutes

    def __init__(
        self,
        node_id: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = DEFAULT_PORT,
        data_dir: Optional[Path] = None,
        bootstrap_peers: Optional[List[str]] = None
    ):
        """
        Initialize AOAI P2P node.

        Args:
            node_id: Unique node identifier (generated if not provided)
            host: Host to bind to
            port: Port to listen on
            data_dir: Directory for storing chain data
            bootstrap_peers: Initial peers to connect to (host:port format)
        """
        self.node_id = node_id or f"node:{secrets.token_hex(8)}"
        self.host = host
        self.port = port

        # Data storage
        self.data_dir = data_dir or Path.home() / ".aoai_node" / self.node_id
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Network state
        self.peers: Dict[str, Peer] = {}
        self.bootstrap_peers = bootstrap_peers or []
        self._lock = threading.Lock()

        # Chain data (merkle roots from all known chains)
        self.known_roots: Dict[str, str] = {}  # agent_id -> merkle_root
        self._load_state()

        # Server
        self._server_socket: Optional[socket.socket] = None
        self._running = False

        # Callbacks
        self._on_anchor_request: Optional[Callable[[str], str]] = None

    def _load_state(self) -> None:
        """Load persisted state"""
        state_file = self.data_dir / "state.json"
        if state_file.exists():
            with open(state_file) as f:
                data = json.load(f)
                self.known_roots = data.get("known_roots", {})
                for peer_data in data.get("peers", []):
                    peer = Peer(**peer_data)
                    self.peers[peer.node_id] = peer

    def _save_state(self) -> None:
        """Persist state to disk"""
        with self._lock:
            state_file = self.data_dir / "state.json"
            data = {
                "known_roots": self.known_roots,
                "peers": [asdict(p) for p in self.peers.values()]
            }
            with open(state_file, "w") as f:
                json.dump(data, f, indent=2)

    def start(self) -> None:
        """Start the P2P node"""
        self._running = True

        # Start server thread
        server_thread = threading.Thread(target=self._run_server, daemon=True)
        server_thread.start()

        # Connect to bootstrap peers
        for peer_addr in self.bootstrap_peers:
            try:
                host, port = peer_addr.split(":")
                self._connect_to_peer(host, int(port))
            except Exception as e:
                print(f"Failed to connect to bootstrap peer {peer_addr}: {e}")

        print(f"AOAI Node started: {self.node_id}")
        print(f"Listening on {self.host}:{self.port}")

    def stop(self) -> None:
        """Stop the P2P node"""
        self._running = False
        if self._server_socket:
            self._server_socket.close()
        self._save_state()
        print(f"AOAI Node stopped: {self.node_id}")

    def _run_server(self) -> None:
        """Run the TCP server"""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)
        self._server_socket.settimeout(1.0)

        while self._running:
            try:
                client_socket, address = self._server_socket.accept()
                # Handle in separate thread
                handler = threading.Thread(
                    target=self._handle_connection,
                    args=(client_socket, address),
                    daemon=True
                )
                handler.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    print(f"Server error: {e}")

    def _handle_connection(self, client_socket: socket.socket, address: tuple) -> None:
        """Handle incoming connection"""
        try:
            client_socket.settimeout(30.0)

            # Read message length
            length_data = client_socket.recv(4)
            if len(length_data) < 4:
                return
            msg_length = struct.unpack('>I', length_data)[0]

            # Read message
            msg_data = b""
            while len(msg_data) < msg_length:
                chunk = client_socket.recv(min(4096, msg_length - len(msg_data)))
                if not chunk:
                    break
                msg_data += chunk

            message = Message.from_bytes(msg_data)
            response = self._process_message(message, address)

            if response:
                client_socket.sendall(response.to_bytes())

        except Exception as e:
            print(f"Connection error from {address}: {e}")
        finally:
            client_socket.close()

    def _process_message(self, message: Message, address: tuple) -> Optional[Message]:
        """Process incoming message and return response"""
        sender = message.sender_id

        # Update peer info
        with self._lock:
            if sender not in self.peers:
                self.peers[sender] = Peer(
                    node_id=sender,
                    host=address[0],
                    port=message.payload.get("port", self.DEFAULT_PORT)
                )
            self.peers[sender].last_seen = time.time()

        if message.msg_type == MessageType.PING:
            return Message(
                msg_type=MessageType.PONG,
                sender_id=self.node_id,
                payload={"version": self.VERSION}
            )

        elif message.msg_type == MessageType.ANNOUNCE:
            # New merkle root announced
            agent_id = message.payload.get("agent_id")
            merkle_root = message.payload.get("merkle_root")
            if agent_id and merkle_root:
                with self._lock:
                    self.known_roots[agent_id] = merkle_root
                self._save_state()
                # Propagate to other peers (gossip)
                self._gossip_announce(agent_id, merkle_root, exclude=sender)
            return None

        elif message.msg_type == MessageType.REQUEST_CHAIN:
            agent_id = message.payload.get("agent_id")
            chain_file = self.data_dir / "chains" / f"{agent_id}.json"
            if chain_file.exists():
                with open(chain_file) as f:
                    chain_data = json.load(f)
                return Message(
                    msg_type=MessageType.CHAIN_DATA,
                    sender_id=self.node_id,
                    payload={"agent_id": agent_id, "chain": chain_data}
                )
            return None

        elif message.msg_type == MessageType.PEER_LIST:
            # Return known peers
            peer_list = [
                {"node_id": p.node_id, "host": p.host, "port": p.port}
                for p in self.peers.values()
                if time.time() - p.last_seen < self.PEER_TIMEOUT
            ][:20]  # Limit response size
            return Message(
                msg_type=MessageType.PEER_LIST,
                sender_id=self.node_id,
                payload={"peers": peer_list}
            )

        elif message.msg_type == MessageType.ANCHOR_REQUEST:
            # External anchoring request - store hash and return confirmation
            record_hash = message.payload.get("record_hash")
            if record_hash and self._on_anchor_request:
                anchor_proof = self._on_anchor_request(record_hash)
                return Message(
                    msg_type=MessageType.ANCHOR_CONFIRM,
                    sender_id=self.node_id,
                    payload={
                        "record_hash": record_hash,
                        "anchor_proof": anchor_proof,
                        "anchored_by": self.node_id,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                )
            return None

        return None

    def _connect_to_peer(self, host: str, port: int) -> bool:
        """Connect to a peer and exchange info"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            sock.connect((host, port))

            # Send ping
            ping = Message(
                msg_type=MessageType.PING,
                sender_id=self.node_id,
                payload={"port": self.port, "version": self.VERSION}
            )
            sock.sendall(ping.to_bytes())

            # Read response
            length_data = sock.recv(4)
            if len(length_data) < 4:
                return False
            msg_length = struct.unpack('>I', length_data)[0]
            msg_data = sock.recv(msg_length)
            response = Message.from_bytes(msg_data)

            if response.msg_type == MessageType.PONG:
                with self._lock:
                    self.peers[response.sender_id] = Peer(
                        node_id=response.sender_id,
                        host=host,
                        port=port,
                        last_seen=time.time()
                    )
                print(f"Connected to peer: {response.sender_id}")
                return True

        except Exception as e:
            print(f"Failed to connect to {host}:{port}: {e}")
        finally:
            sock.close()

        return False

    def _gossip_announce(self, agent_id: str, merkle_root: str, exclude: str = None) -> None:
        """Gossip announce to all peers except sender"""
        message = Message(
            msg_type=MessageType.ANNOUNCE,
            sender_id=self.node_id,
            payload={"agent_id": agent_id, "merkle_root": merkle_root}
        )

        for peer in list(self.peers.values()):
            if peer.node_id == exclude:
                continue
            if time.time() - peer.last_seen > self.PEER_TIMEOUT:
                continue
            try:
                self._send_message(peer, message)
            except Exception:
                pass  # Ignore send failures in gossip

    def _send_message(self, peer: Peer, message: Message) -> Optional[Message]:
        """Send message to peer and optionally get response"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        try:
            sock.connect((peer.host, peer.port))
            sock.sendall(message.to_bytes())

            # Read response if expected
            length_data = sock.recv(4)
            if len(length_data) < 4:
                return None
            msg_length = struct.unpack('>I', length_data)[0]
            msg_data = sock.recv(msg_length)
            return Message.from_bytes(msg_data)
        finally:
            sock.close()

    # === Public API ===

    def announce_chain(self, agent_id: str, merkle_root: str) -> None:
        """Announce a chain's merkle root to the network"""
        with self._lock:
            self.known_roots[agent_id] = merkle_root
        self._save_state()
        self._gossip_announce(agent_id, merkle_root)

    def request_anchor(self, record_hash: str) -> List[dict]:
        """Request anchoring from multiple peers (for redundancy)"""
        anchors = []
        message = Message(
            msg_type=MessageType.ANCHOR_REQUEST,
            sender_id=self.node_id,
            payload={"record_hash": record_hash}
        )

        for peer in list(self.peers.values())[:5]:  # Ask up to 5 peers
            try:
                response = self._send_message(peer, message)
                if response and response.msg_type == MessageType.ANCHOR_CONFIRM:
                    anchors.append(response.payload)
            except Exception:
                continue

        return anchors

    def get_peer_count(self) -> int:
        """Get number of active peers"""
        return len([
            p for p in self.peers.values()
            if time.time() - p.last_seen < self.PEER_TIMEOUT
        ])

    def get_known_chains(self) -> Dict[str, str]:
        """Get all known chain merkle roots"""
        return dict(self.known_roots)

    def set_anchor_handler(self, handler: Callable[[str], str]) -> None:
        """Set callback for handling anchor requests"""
        self._on_anchor_request = handler


def create_anchor_callback(node: AOAINode) -> Callable[[str], str]:
    """
    Create external anchor callback for HonestChain integration.

    Usage:
        node = AOAINode()
        node.start()

        from honest_chain import HonestChain
        hc = HonestChain(
            agent_id="my-agent",
            external_anchor=create_anchor_callback(node)
        )
    """
    def anchor(record_hash: str) -> str:
        anchors = node.request_anchor(record_hash)
        if anchors:
            # Return proof from first successful anchor
            return json.dumps({
                "p2p_anchors": anchors,
                "anchor_count": len(anchors),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        return f"local:{node.node_id}:{record_hash[:16]}"

    return anchor


# === Demo ===

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "node1":
        # First node
        node = AOAINode(node_id="node-alpha", port=7777)
        node.start()
        print("Node 1 running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            node.stop()

    elif len(sys.argv) > 1 and sys.argv[1] == "node2":
        # Second node connecting to first
        node = AOAINode(
            node_id="node-beta",
            port=7778,
            bootstrap_peers=["127.0.0.1:7777"]
        )
        node.start()
        print(f"Node 2 running. Peers: {node.get_peer_count()}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            node.stop()

    else:
        print("AOAI P2P Node Network")
        print("=" * 50)
        print("Usage:")
        print("  python p2p_node.py node1  # Start first node on port 7777")
        print("  python p2p_node.py node2  # Start second node on port 7778")
        print()
        print("Integration with HonestChain:")
        print("  from p2p_node import AOAINode, create_anchor_callback")
        print("  from honest_chain import HonestChain")
        print()
        print("  node = AOAINode()")
        print("  node.start()")
        print()
        print("  hc = HonestChain(")
        print("      agent_id='my-agent',")
        print("      external_anchor=create_anchor_callback(node)")
        print("  )")
