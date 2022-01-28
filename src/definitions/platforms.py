"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
import platform

WINDOWS = 0
LINUX = 1
DARWIN = 2
UNKNOWN = -1

UNIX = 3

match platform.system().lower():
    case "linux":
        OS = LINUX
    case "darwin":
        OS = DARWIN
    case 'windows':
        OS = WINDOWS
    case _:
        OS = UNKNOWN
