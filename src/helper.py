"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import os
import ctypes


def loadlib(lib):
    path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    return ctypes.CDLL(path + f"/lib/{lib}")


# function to return string with quotes removed
def remove_quotes(string): return string.replace("\"", "")


# function to return title centered around string
def center(string, title): return f"{{:^{len(string)}}}".format(title)


# function to decode bytes
def decode(data):
    try:
        return data.decode()
    except UnicodeDecodeError:
        try:
            return data.decode("cp437")
        except UnicodeDecodeError:
            return data.decode(errors="replace")
