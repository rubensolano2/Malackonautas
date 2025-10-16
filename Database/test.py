# test.py
from db_crypto import encrypt, decrypt

raw = b"Secret message for the DB"
pw = "mystrongpassphrase"

blob = encrypt(raw, pw)
print("Encrypted blob length:", len(blob))

plain = decrypt(blob, pw)
print("Decrypted:", plain.decode())
