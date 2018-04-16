# Python Backdoor
[![Build status](https://ci.appveyor.com/api/projects/status/5tdy7lpopxpinui9?svg=true)](https://ci.appveyor.com/project/xp4xbox/python-backdoor)

This program is an opensource, hidden and undetectable backdoor/reverse shell/RAT for Windows made in Python 3 which contains many features such as multi-client support and cross-platform server.

## Installation
You will need:
* [Python 3.6+](https://www.python.org/downloads)
* [Pywin32](https://sourceforge.net/projects/pywin32/files/pywin32/)
* [Pyinstaller](http://www.pyinstaller.org/downloads.html#)

To install the two modules, simply run `python -m pip install -r requirements.txt`

## Features
Currently this program has several features such as:
* Multi-client support
* Cross-platform server
* Built-in keylogger
* Ability to send command to all clients
* Ability to capture screenshots
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

1. Run `setup.py` and follow the directions on screen to build the client to .exe.
2. Check the `dist` folder for the .exe.
3. **Disable your firewall on the server or configure your firewall to allow port 3000.**
4. Run the `server.py` to start accepting connections.

> If you plan on using the program outside of your network, you must port forward port 3000.

For more information please refer to the [instructable](https://www.instructables.com/id/Simple-Python-Backdoor/).

## Help

If you need any help at all, feel free to post a "help" issue or a comment on my [instructable](https://www.instructables.com/id/Simple-Python-Backdoor/).

## Contributing

Contributing is encouraged and will help make a better program. Please refer to [this](https://gist.github.com/MarcDiethelm/7303312) before contributing.

## Disclaimer

This program must be used for legal purposes! I am not responsible for anything you do with it.

## License
[License](https://github.com/xp4xbox/Python-Backdoor/blob/master/license)
