"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

import json
import logging

from cryptography.fernet import Fernet

from src.defs import *


class EncryptedSocket(object):
    def __init__(self):
        self.key = None
        self.encryptor = None
        self.socket = None
        self.logger = logging.getLogger(LOGGER_ID)

    def close(self):
        self.socket.close()

    def recvall(self, buffer, encrypted=True):
        if encrypted and self.encryptor is None:
            raise Exception("Key is not set")

        data = b""
        while len(data) < buffer:
            data += self.socket.recv(BUFFER)

        if encrypted:
            data = self.encryptor.decrypt(data)

        self.logger.debug(f"recvall: {data}")

        return data

    def send(self, data, encrypted=True):
        if not encrypted:
            self.socket.send(data)
        else:
            if self.encryptor is None:
                raise Exception("Key is not set")
            else:
                self.socket.send(self.encryptor.encrypt(data))

    def recv(self, encrypted=True):
        if not encrypted:
            return self.socket.recv(BUFFER)
        else:
            if self.encryptor is None:
                raise Exception("Key is not set")

            return self.encryptor.decrypt(self.socket.recv(BUFFER))

    def recv_json(self, encrypted=True):
        data = self.recv(encrypted).decode()

        self.logger.debug(f"recv: {data}")

        return json.loads(data)

    def send_json(self, key, value=None, encrypted=True):
        command = json.dumps({"key": key, "value": value})

        self.logger.debug(f"send: {command}")

        command = command.encode()

        if encrypted:
            self.send(command)
        else:
            self.send(command, False)

    def sendall_json(self, key, data, sub_value=None, encrypted=True, is_bytes=False):
        if not is_bytes:
            data = data.encode()

        if encrypted:
            data = self.encryptor.encrypt(data)

        self.send_json(key, {"buffer": len(data), "value": sub_value}, encrypted)
        self.send(data, False)

    def set_key(self, key):
        self.key = key
        self.encryptor = Fernet(key)

    def new_key(self):
        self.key = Fernet.generate_key()
        self.encryptor = Fernet(self.key)
