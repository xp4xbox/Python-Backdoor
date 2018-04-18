# simple test to ensure connection occurs using appveyor

import threading, time, sys

# append path created by appveyor
sys.path.append("C:/projects/python-backdoor")

# set error level to be 0
ERRORLEVEL = 0


def Start(arg):  # simple function to run the server and the client and to check for errors
    global ERRORLEVEL
    if arg == "server":
        try:
            import server
        except Exception as error:
            # if there is an error, print it and set error level to be 2
            print(error)
            ERRORLEVEL = 2
    elif arg == "client":
        try:
            import client
        except Exception as error:
            print(error)
            ERRORLEVEL = 2


# open client for reading to get all lines
objClientFile = open("client.py", "r")
arrFileContents = objClientFile.readlines()
objClientFile.close()

# use loop in order to ensure that line number doesnt matter
for intCounter in range(0, len(arrFileContents)):
    if arrFileContents[intCounter][0:9] == "strHost =":
        # set IP to be local
        arrFileContents[intCounter] = "strHost = \"127.0.0.1\"" + "\n"
        break

# write updated client with local IP
objClientFile = open("client.py", "w")
objClientFile.writelines(arrFileContents)
objClientFile.close()

# run threads for server and client to test for errors
thread_server_test = threading.Thread(target=Start, args=["server"], daemon=True).start()
thread_client_test = threading.Thread(target=Start, args=["client"], daemon=True).start()

# wait 3 seconds
time.sleep(3)

# check error level to determine exit code
if ERRORLEVEL != 0:
    sys.exit(ERRORLEVEL)
else:
    sys.exit(0)
