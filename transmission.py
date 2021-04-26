import socket
import time
import random


PORT = 50505

SERVER_BACKLOG = 5
SERVER_TIMEOUT = 1.0

MAX_SESSION_ID = 1073741824
MIN_SESSION_ID = 2048





class Peer:
    '''
        Node's relationship to a particular peer.
    '''

    def __init__(self, host=None, socket=None):
        if host == None:
            self.host = client_socket.getpeername()[0]
        else:
            self.host = host
        self.socket = socket
        self.session_id = None

    def connect(self, node_session_id):
        if self.socket == None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, PORT))
        self.socket.sendall(b'SIDR')
        self.socket.sendall(node_session_id[0:8])
        self.session_id = self.socket.recv(8)

    def disconnect(self):
        if self.socket != None:
            self.socket.sendall(b'TERM')
            self.socket.close()
            self.socket = None

    def is_connected(self):
        return self.socket != None

    def ping(self):
        if not self.is_connected():
            self.connect()
        self.socket.sendall(b'PING')

    def handle(self, **kwargs):
        transcode = self.socket.recv(4)
        if transcode == b'SIDR':
            # Session ID report
            self.session_id = self.socket.recv(8)
        elif transcode == b'SIDQ':
            # Session ID request
            if not kwargs.has_key("local_sid"):
                return
            self.socket.sendall(b'SIDR')
            self.socket.sendall(kwargs["local_sid"])
        elif transcode == b'PING':
            # PING - time and latency check
            self.socket.sendall(b'TIME')
            cur_time_ms = int(time.time() * 1000)
            self.socket.sendall(bytes(hex(cur_time_ms), "utf-8"))
        elif transcode == b'TIME':
            # TIME - time report
            time_msg = self.socket.recv(32)
            time_reported = int(time_msg.decode("utf-8"))
            latency = int(time.time()) - int(time_reported)
            print("[SID {}] time: {}, latency: {} s".format(self.session_id, time_reported, latency))
        elif transcode == b'TERM':
            self.socket.close()
            self.socket = None




#TODO implement client-only functionality
class Node:
    '''
        Handles connections with other nodes.
        Nodes form a peer-to-peer network.
        Nodes deal in artifacts.
    '''

    def __init__(self):
        self.server_socket = None
        self.peers = dict() # maps session ids to Peer objects
        self.session_id = None
        self._new_session_id()

    def _new_session_id(self):
        session_n = random.randint(MIN_SESSION_ID, MAX_SESSION_ID)
        session_n_hex = hex(session_n)[2:].rjust(8, "0")
        self.session_id = bytes(session_n_hex, "utf-8")

    def str_sid(self):
        return str(self.session_id, "utf-8")

    def n_peers(self):
        return len(self.peers)

    def start_server(self):
        if self.server_socket == None:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.settimeout(SERVER_TIMEOUT)
            self.server_socket.bind(('', PORT))
            self.server_socket.listen(SERVER_BACKLOG)
        else:
            raise Exception("Server already started.")

    def stop_server(self):
        if self.server_socket != None:
            self.server_socket.close()
            self.server_socket = None

    def add_peer(self, peer, connect=True):
        self.peers[peer.get_session_id()] = peer
        if connect:
            peer.connect(self.session_id)

    def purge_unresponsive_peers(self):
        pass #TODO

    def handle_new_connections(self):
        try:
            client_socket, client_addr = self.server_socket.accept()
            client_socket.setblocking(False)
            client_socket.settimeout(None)
            peer = Peer(socket=client_socket)
            self.add_peer(peer)
            return True # Return true if new connections are opened
        except socket.timeout:
            return False # Return false for no new connections







