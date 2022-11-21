import base64
import json

from Crypto.Cipher import AES

JSON_KEY = ['nonce', 'ciphertext', 'tag']


def encrypt(data, key):
    cipher = AES.new(key, AES.MODE_GCM)

    ciphertext, tag = cipher.encrypt_and_digest(data)

    json_v = [base64.b64encode(x).decode() for x in [cipher.nonce, ciphertext, tag]]

    return json.dumps(dict(zip(JSON_KEY, json_v))).encode()


def decrypt(json_data, key):
    b64 = json.loads(json_data.decode())

    jv = {k: base64.b64decode(b64[k]) for k in JSON_KEY}

    cipher = AES.new(key, AES.MODE_GCM, nonce=jv['nonce'])

    # any decrypt error will be caught in main, and trigger restart

    return cipher.decrypt_and_verify(jv['ciphertext'], jv['tag'])
