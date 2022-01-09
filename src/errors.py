"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""


class ServerSocket:
    class InvalidIndex(Exception):
        pass


class ClientSocket:
    class KeyloggerError(Exception):
        pass

    class Persistence:
        class StartupError(Exception):
            pass