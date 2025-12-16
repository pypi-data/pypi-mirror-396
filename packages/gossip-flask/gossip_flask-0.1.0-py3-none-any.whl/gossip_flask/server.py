import base64
import json
import logging
import os
import random
import threading
import time

import requests
import semver
from flask import Flask, jsonify
from scipy.stats import entropy

from gossip_flask import __version__
from gossip_flask.db import Message, get_db_session
from gossip_flask.utils import bytes_to_bits

# Configuration from environment variables with defaults

PEER_REFRESH_INTERVAL = int(os.getenv("POLLING_INTERVAL", "3600"))
"""How often to refresh the peer list (in seconds)"""
PEER_LIST_SIZE = int(os.getenv("PEER_LIST_SIZE", "0"))
"""0: unlimited peers, >0: limit to this many peers"""
REBROADCAST_SIZE = int(os.getenv("REBROADCAST_SIZE", "10"))
"""Number of peers to rebroadcast each message to (best-effort)"""
MIN_MESSAGE_ID_ENTROPY = float(os.getenv("MIN_ENTROPY_THRESHOLD", "4.0"))
"""Minimum of 4 bits of entropy for a valid message ID (out of 8 max for a single byte)"""
MIN_MESSAGE_ID_LENGTH = 16
"""Minimum and maximum lengths for a valid message ID (in bytes)"""
MAX_MESSAGE_ID_LENGTH = 64
"""Maximum length for a valid message ID (in bytes)"""

logging.basicConfig(
    level=logging.getLevelNamesMapping()[os.getenv("LOG_LEVEL", "INFO")]
)
_logger = logging.getLogger(__name__)
"""The logger for the gossip node"""


class GossipNode:
    """
    Initializes a gossip node

    Parameters
    ----------
    node_url : str
        The externally visisible URL of this node
    message_handlers : List[Callable], optional
        A list of message handlers, by default None
    peers List[str]: , optional
        A list of peer URLs, by default None
        
        NOTE: The environment variable SEED_PEER can be specified to
        initialize the peer list with a seed peer URL.
    """
    def _log_new_peers(self, new_peers):
        if new_peers:
            _logger.debug(f"New peers added: {new_peers}")

    def start_peer_sync(self):
        """
        Starts the peer synchronization thread
        """
        t = threading.Thread(target=self._peer_sync_loop, daemon=True)
        t.start()

    def _peer_sync_loop(self):
        """
        The peer synchronization loop. This reaches out to existing peers and
        grabs their peer list. The new peer list is then shuffled and reduced
        down to the specified PEER_LIST_SIZE.
        """
        while True:
            if os.environ.get("DEBUG", "0") == "1":
                # Sleep 15 seconds for all nodes in the debug environment to come up.
                time.sleep(15)
            combined_peers = set(self.peers)
            for peer_url in self.peers:
                try:
                    resp = requests.post(
                        f"{peer_url}/peers", json={"node_url": self.node_url}, timeout=2
                    )
                    if resp.status_code == 200:
                        peer_list = resp.json().get("peers", [])
                        combined_peers.update(peer_list)
                except Exception as e:
                    logging.error(
                        f"Failed to get peers from {peer_url}, removing peer: {e}"
                    )
                    self.peers.remove(peer_url)
            combined_peers.discard(self.node_url)
            combined_peers = list(combined_peers)
            random.shuffle(combined_peers)
            current_size = len(self.peers)
            if PEER_LIST_SIZE == 0 or current_size < PEER_LIST_SIZE:
                needed = PEER_LIST_SIZE - current_size
                to_add = [p for p in combined_peers if p not in self.peers][:needed]
                if to_add:
                    self._log_new_peers(to_add)
                self.peers.extend(to_add)
            elif current_size >= PEER_LIST_SIZE:
                random.shuffle(self.peers)
                remove_count = (
                    current_size
                    - (PEER_LIST_SIZE // 2)
                    - (current_size - PEER_LIST_SIZE)
                )
                self.peers = self.peers[remove_count:]
                to_add = [p for p in combined_peers if p not in self.peers][
                    : PEER_LIST_SIZE // 2
                ]
                if to_add:
                    _logger.debug(
                        f"Peer list full. Removed {remove_count} peers. Adding new peers: {to_add}"
                    )
                self.peers.extend(to_add)
            time.sleep(PEER_REFRESH_INTERVAL)

    def __init__(self, node_url, message_handlers=None, peers=None):
        self.node_url = node_url
        self.peers = peers if peers is not None else []
        self.message_handlers = message_handlers if message_handlers else []
        self.db_session = get_db_session()

        seed_peer = os.getenv("SEED_PEER")
        if seed_peer and seed_peer not in self.peers:
            self.peers.append(seed_peer)

        self.app = Flask(node_url)
        self._setup_routes()
        self.start_peer_sync()

    def _setup_routes(self):
        """
        Establishes the flask routes for the gossip node
        """
        from flask import request

        @self.app.route("/message", methods=["PUT"])
        def put_message():
            # Get the message data
            data = request.get_json(force=True)

            # Ensure the message id exists and it has sufficient entropy
            if "message_id" not in data:
                return jsonify({"error": "Missing message_id"}), 400
            # Validate semantic version compatibility if provided
            msg_version = data.get("version")
            if msg_version:
                try:
                    if (
                        semver.VersionInfo.parse(msg_version).major
                        > semver.VersionInfo.parse(__version__).major
                    ):
                        return jsonify({"error": "Incompatible message version"}), 400
                except Exception:
                    return jsonify({"error": "Invalid version format"}), 400
            else:
                return jsonify({"error": "Missing version"}), 400
            _logger.debug(f"Received message: {data}")
            message_id = base64.b64decode(data["message_id"])
            message_id_bits = bytes_to_bits(message_id)
            message_id_entropy = entropy(message_id_bits)
            _logger.debug(f"Message ID entropy: {message_id_entropy}")
            if entropy(message_id_bits) < MIN_MESSAGE_ID_ENTROPY:
                _logger.debug("Message ID entropy too low, ignoring message.")
                return (
                    jsonify({"error": f"Low entropy message_id {message_id_entropy}"}),
                    400,
                )
            if (
                len(message_id) < MIN_MESSAGE_ID_LENGTH
                or len(message_id) > MAX_MESSAGE_ID_LENGTH
            ):
                _logger.debug("Message ID length invalid, ignoring message.")
                return (
                    jsonify({"error": f"Invalid length message_id {len(message_id)}"}),
                    400,
                )
            try:
                existing = (
                    self.db_session.query(Message).filter_by(id=message_id).first()
                )
                if existing:
                    _logger.debug("Message already received; skipping insert.")
                else:
                    self.db_session.add(
                        Message(
                            id=message_id,
                            version=msg_version,
                            message=json.dumps(data)
                        )
                    )
                    self.db_session.commit()
                    _logger.debug("Inserted new message into DB.")
                    try:
                        t = threading.Thread(
                            target=self._rebroadcast, args=(data,), daemon=True
                        )
                        t.start()
                    except Exception as e:
                        _logger.debug(f"Failed to start rebroadcast thread: {e}")
            except Exception as e:
                _logger.error(f"Database error while inserting message: {e}")
                try:
                    self.db_session.rollback()
                except Exception:
                    pass
                return jsonify({"error": f"Invalid message format."}), 400

            for handler in self.message_handlers:
                try:
                    handler(data)
                except Exception as e:
                    logging.error(f"Error in message handler: {e}")
            return jsonify({"status": "received"})

        @self.app.route("/peers", methods=["GET"])
        def get_peers():
            """
            Gets a node's peer list

            Returns
            -------
            List[str]
                A list of peer URLs
            """
            return jsonify({"peers": self.peers})

        @self.app.route("/peers", methods=["POST"])
        def post_peers():
            """
            Allows a node to broadcast its peer url to another node. If the node
            has a limited number of peers specified by the PEER_LIST_SIZE env
            variable, it will prune the peer list by removing a random peer if
            its peer list is full.

            Returns
            -------
            List[str]
                The peer urls.
            """
            data = request.get_json(force=True)
            node_url = data.get("node_url")
            added = False
            if node_url and node_url != self.node_url:
                if node_url not in self.peers:
                    self.peers.append(node_url)
                    self._log_new_peers([node_url])
                    added = True
                    if PEER_LIST_SIZE > 0 and len(self.peers) > PEER_LIST_SIZE:
                        removed = random.choice(self.peers)
                        self.peers.remove(removed)
                        _logger.debug(
                            f"Peer list exceeded size. Removed peer: {removed}"
                        )
            return jsonify({"peers": self.peers, "added": added})

        @self.app.route("/message", methods=["POST"])
        def get_message():
            """Retrieve a stored message by base64-encoded message_id in JSON body.

            Example: POST /message with JSON {"message_id": "BASE64STRING"}
            """
            data = request.get_json(force=True)
            if not data or "message_id" not in data:
                return jsonify({"error": "Missing message_id"}), 400

            message_id_b64 = data.get("message_id")
            try:
                message_id = base64.b64decode(message_id_b64)
            except Exception:
                return jsonify({"error": "Invalid base64 message_id"}), 400

            try:
                existing = (
                    self.db_session.query(Message).filter_by(id=message_id).first()
                )
                if existing:
                    return jsonify(existing.message)
                return jsonify({"error": "Message not found"}), 404
            except Exception as e:
                _logger.error(f"Database error while fetching message: {e}")
                return jsonify({"error": "Internal server error"}), 500

    def add_peer(self, peer_url):
        if peer_url not in self.peers:
            self.peers.append(peer_url)
            self._log_new_peers([peer_url])

    def run(self, host="127.0.0.1", port=5000):
        logging.basicConfig(level=logging.debug)
        logging.debug(
            f"GossipNode server starting on {host}:{port} with node_url={self.node_url}"
        )
        self.app.run(host=host, port=port, threaded=True)

    def add_message_handler(self, handler):
        self.message_handlers.append(handler)

    def remove_message_handler(self, handler):
        if handler in self.message_handlers:
            self.message_handlers.remove(handler)
            return True
        return False

    def _rebroadcast(self, data):
        """Send the message to all known peers (best-effort).

        Runs in a background thread; failures are logged and ignored.
        """
        for peer in random.sample(list(self.peers), REBROADCAST_SIZE):
            # don't send to self
            if peer == self.node_url:
                continue
            try:
                requests.post(f"{peer}/message", json=data, timeout=2)
            except Exception as e:
                _logger.debug(f"Failed to rebroadcast to {peer}: {e}")

    def __del__(self):
        """Clean up resources when the GossipNode is garbage-collected.

        Close the DB session if it exists. This is defensive: exceptions are
        swallowed because __del__ should never raise.
        """
        try:
            if self.db_session is not None:
                try:
                    self.db_session.close()
                except Exception:
                    pass
                try:
                    self.db_session = None
                except Exception:
                    pass
        except Exception:
            pass


def create_app():
    node_url = os.getenv("NODE_URL", "default_node")
    node = GossipNode(node_url)
    logging.basicConfig(
        level=logging.getLevelNamesMapping()[os.getenv("LOG_LEVEL", "INFO")]
    )
    logging.debug(f"GossipNode Flask app created with node_url={node_url}")
    return node.app
