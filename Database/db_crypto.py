# db_crypto.py
# --------------------------------------------------------------
# Encrypt / decrypt arbitrary byte strings (e.g. DB column values)
# using a user‑supplied passphrase.
# --------------------------------------------------------------

import os
from typing import Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# ----------------------------------------------------------------------
# Helper: derive a 256‑bit AES key from a passphrase (always bytes)
# ----------------------------------------------------------------------
def _derive_key(passphrase: str, salt: bytes, iterations: int = 200_000) -> bytes:
    """
    PBKDF2‑HMAC‑SHA256 → 32‑byte key (AES‑256).

    *passphrase* – user supplied secret (unicode string)
    *salt*       – 16‑byte random value stored alongside the ciphertext
    *iterations* – work factor; 200 k is a good default on modern hardware
    """
    # Ensure the passphrase is encoded to UTF‑8 bytes before KDF
    passphrase_bytes = passphrase.encode("utf-8")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,          # 256‑bit key
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(passphrase_bytes)   # ← returns **bytes**


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------
def encrypt(plaintext: bytes, passphrase: str) -> bytes:
    """
    Returns a single blob:
        salt (16 B) || nonce (12 B) || ciphertext+auth_tag
    """
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("plaintext must be bytes")

    # 1️⃣ random salt for key derivation
    salt = os.urandom(16)

    # 2️⃣ derive AES‑256‑GCM key from the passphrase + salt
    key = _derive_key(passphrase, salt)

    # 3️⃣ random nonce (12 B is the recommended size for GCM)
    nonce = os.urandom(12)

    # 4️⃣ encrypt – AESGCM appends the authentication tag
    aesgcm = AESGCM(key)          # key is now a bytes object
    ct = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    # 5️⃣ pack everything together
    return salt + nonce + ct


def decrypt(ciphertext_blob: bytes, passphrase: str) -> bytes:
    """
    Inverse of ``encrypt``.
    Expects the format produced by ``encrypt``:
        salt (16 B) || nonce (12 B) || ciphertext+auth_tag
    """
    if not isinstance(ciphertext_blob, (bytes, bytearray)):
        raise TypeError("ciphertext_blob must be bytes")

    if len(ciphertext_blob) < 28:   # 16 B salt + 12 B nonce minimum
        raise ValueError("Ciphertext blob is too short")

    # 1️⃣ split the components
    salt = ciphertext_blob[:16]
    nonce = ciphertext_blob[16:28]
    ct = ciphertext_blob[28:]

    # 2️⃣ re‑derive the key from the supplied passphrase and extracted salt
    key = _derive_key(passphrase, salt)

    # 3️⃣ decrypt and verify authenticity
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ct, associated_data=None)
