# Python Backdoor

This project is an open source, backdoor/reverse tcp/RAT for Windows made in Python3 which contains many features such as multi-client support and cross-platform server.

![image](.github/resources/setup.png)

## Installation

You will need:

* [Python 3.10+](https://www.python.org/downloads) (Add python to PATH during installation)
* A Windows computer for buildin the client
* Any OS with python support for the server

1. Download the repository via GitHub or git eg. `git clone https://github.com/xp4xbox/Python-Backdoor`
2. Install the required modules by running `python -m pip install -r requirements.txt`

## Features

Currently, this program has several features, notably:

* Multi-client support
* Cross-platform server
* Fernet encryption
* Built-in keylogger
* Ability to send commands to all clients
* Ability to capture screenshots
* Ability to upload/download files
* Ability to open remote shell or python interpreter
* Ability to disable a process
* Ability to run shellcode (x86 python only)
* Ability to melt file
* VM/sandboxie check

## Quick Usage

1. Run `setup.py` and configure options to build the client
2. Check the `dist` folder for the .exe.
3. Disable your firewall on the server or configure your firewall to allow the port chosen.
4. Run the `src/server.py -p <port>` to start the server and accept connections.

> If you plan on using the program with DNS hostname or external IP, you must port forward your chosen port.

## Help

If you need any help at all, feel free to open a "help" issue.

## Contributing

Contributing is encouraged and will help make this a better program. Please refer to [this](https://gist.github.com/MarcDiethelm/7303312) before contributing.

## Disclaimer

This program is for educational purposes only. I take no responsibility or liability for own personal use.

## License

[License](https://github.com/xp4xbox/Python-Backdoor/blob/master/license)
