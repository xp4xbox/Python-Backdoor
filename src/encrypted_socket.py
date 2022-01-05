"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
import json

from cryptography.fernet import Fernet

from src.defs import *


class EncryptedSocket(object):
    def __init__(self):
        self.key = None
        self.encryptor = None
        self.socket = None

    def close(self):
        self.socket.close()

    def recvall(self, buffer, encrypted=True):
        if encrypted and self.encryptor is None:
            raise Exception("Key is not set")

        data = b""
        while len(data) < buffer:
            data += self.recv()

        if encrypted:
            return self.encryptor.decrypt(data)
        else:
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

        if self.encryptor is None:
            raise Exception("Key is not set")

    def recv_json(self, encrypted=True):
        return json.loads(self.recv(encrypted).decode())

    def send_json(self, key, value=None, encrypted=True):
        command = json.dumps({"key": key, "value": value}).encode()

        if encrypted:
            self.send(command)
        else:
            self.send(command, False)

    def sendall_json(self, key, data, encrypted=True, is_bytes=False):
        if not is_bytes:
            data = data.encode()

        if encrypted:
            data = self.encryptor.encrypt(data)

        self.send_json(key, len(data), encrypted)
        self.send(data, False)

    def set_key(self, key):
        self.key = key
        self.encryptor = Fernet(key)

    def new_key(self):
        self.key = Fernet.generate_key()
        self.encryptor = Fernet(self.key)
