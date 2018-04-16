import os, sys, socket

python_path = os.path.dirname(sys.executable)

objSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
objSocket.connect(("google.com", 0))
strCurrentIP = objSocket.getsockname()[0]
objSocket.close()

print("1. Use: " + strCurrentIP)
print("2. Use a different IP address for server")
print("3. Use a DNS Hostname")

strChoice = input("\n" + "Type selection: ")

if strChoice == "2":
    strCurrentIP = input("\n" + "Enter IP: ")
elif strChoice == "3":
    strDNSHostname = input("\n" + "Enter DNS Hostname: ")

objClientFile = open("client.py", "r")
arrFileContents = objClientFile.readlines()
objClientFile.close()

if strChoice == "2" or strChoice == "1":
    arrFileContents[6] = "strHost = \"" + strCurrentIP + "\"" + "\n"
else:
    arrFileContents[7] = "strHost = socket.gethostbyname(\"" + strDNSHostname + "\")" + "\n"

objClientFile = open("client.py", "w")
objClientFile.writelines(arrFileContents)
objClientFile.close()

os.system(python_path + "/Scripts/pyinstaller client.py --exclude-module FixTk --exclude-module tcl --exclude-module tk "
                        "--exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter "
                        "--onefile --windowed")
