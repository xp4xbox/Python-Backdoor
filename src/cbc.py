from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

BLOCK_SIZE = AES.block_size


def encrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=get_random_bytes(BLOCK_SIZE))

    data = pad(data, BLOCK_SIZE)

    # include the iv to the ciphertext
    return cipher.iv + cipher.encrypt(data)


def decrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=data[:BLOCK_SIZE])

    plaintext = cipher.decrypt(data[BLOCK_SIZE:])

    return unpad(plaintext, BLOCK_SIZE)
