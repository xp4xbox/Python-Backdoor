# Python Backdoor

This project is an open source, backdoor/reverse tcp/RAT for Windows made in Python3 which contains many features such as multi-client support and cross-platform server.

![image](.github/resources/demo.png)

## Installation

You will need:

* [Python 3.10+](https://www.python.org/downloads) (Add python to PATH during installation)
* A Windows computer for building the client
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
* Ability to inject shellcode
* Ability to melt file
* VM/sandboxie check

## Quick Usage

1. Run `src/setup.pyw` and configure options to build the client
2. Check the `dist` folder for the .exe.
3. Disable your firewall on the server or configure your firewall to allow the port chosen.
4. If running the server on a different machine, run `pip install cryptography` to install the server dependency
5. Run the `src/main_server.py -p <port>` to start the server and accept connections.

> If you plan on using the program with DNS hostname or external IP, you must port forward your chosen port.

![image](.github/resources/setup.png)

## File breakdown

### /src

- `./setup.pyw`: Windowed setup file to configure and build the client
- `./main_server.py`: Main file for server
- `./main_client.py`: Main file for client
- `./logger.py`: Handles logging with the use of the syslog standard
- `./helper.py`: Collection of useful functions
- `./errors.py`: Collection of internal errors
- `./encrypted_socket.py`: Parent socket class for server and client
- `./command_defs.py`: Constants for all commands/menu options
- `./args.py`: Handles client and server file arguments

### /src/server

- `./view.py`: Handles menu interaction between user and server
- `./socket.py`: Child socket class stores connections and client info
- `./control.py`: Executes the server commands

### /src/client

- `./socket.py`: Child socket class for client
- `./persistence.py`: Functions for adding persistence/detection
- `./keylogger.py`: Keylogger module
- `./control.py`: Executes client commands
- `./command_handler.py`: Parses command from server

## Common problems

- Injecting shellcode requires the architecture specified by the command. eg. x64: `msfvenom windows/x64/meterpreter/reverse_tcp`
- For use outside of network specified port is not open, check specified port with a [port scanner](https://www.whatismyip.com/port-scanner/)

## TODO

- Configure the client to be cross platform (windows only tools will remain and show only with correct os)
- Add webcam module (openCV maybe, if there is a smaller dependency)

## Disclaimer

This program is for educational purposes only. I take no responsibility or liability for own personal use.

## License

[License](https://github.com/xp4xbox/Python-Backdoor/blob/master/license)
