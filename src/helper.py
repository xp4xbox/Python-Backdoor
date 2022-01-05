"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox
"""


# function to return string with quotes removed
def remove_quotes(string): return string.replace("\"", "")


# function to return title centered around string
def center(string, title): return f"{{:^{len(string)}}}".format(title)


# function to decode bytes
def decode(data):
    try:
        return data.decode()
    except UnicodeDecodeError:
        try:
            return data.decode("cp437")
        except UnicodeDecodeError:
            return data.decode(errors="replace")
