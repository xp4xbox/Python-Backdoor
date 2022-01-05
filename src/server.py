"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

from src.server.control import Control
from src.server.socket import Socket
from src.server.view import View


class Server:
    def __init__(self, port):
        self.socket = Socket(port)
        self.socket.listen_asych()
        self.view = View(Control(self.socket))


if __name__ == "__main__":
    Server(3000)
