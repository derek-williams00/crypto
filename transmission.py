import socket
import time
import random


#MIGHT NEED LATER:  HOST = "127.0.0.1"
PORT = 50505 #TODO: consider changing this port

SERVER_BACKLOG = 5

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

    def has_socket(self):
        return self.socket != None

    def get_session_id(self):
        if self.session_id == None:
            pass #TODO
        return self.session_id

    def connect(self, node_session_id):
        if self.socket == None:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, PORT))
        if self.session_id == None:
            self.socket.sendall(node_session_id[0:8])
            self.session_id = self.socket.recv(8)

    def ping(self):
        if not self.has_socket():
            self.connect()
        pass #TODO






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

    def start_server(self):
        if self.server_socket == None:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
        client_socket, client_addr = self.server_socket.accept()
        client_socket.setblocking(False)
        client_socket.settimeout(None)
        peer = Peer(socket=client_socket)
        self.add_peer(peer)







