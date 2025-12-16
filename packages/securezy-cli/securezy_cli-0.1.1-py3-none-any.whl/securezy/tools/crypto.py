from __future__ import annotations

import os
from pathlib import Path

MAGIC = b"SECUREZY1"
SALT_LEN = 16
NONCE_LEN = 12
TAG_LEN = 16
CHUNK_SIZE = 1024 * 1024


def _require_crypto():
    try:
        from cryptography.exceptions import InvalidTag
        from cryptography.hazmat.primitives.ciphers import Cipher
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.ciphers.algorithms import AES
        from cryptography.hazmat.primitives.ciphers.modes import GCM
        from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

        return AESGCM, Scrypt, Cipher, AES, GCM, InvalidTag
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "cryptography is required for crypto features. Install with: pip install 'securezy[crypto]'"
        ) from e


def _derive_key(password: str, salt: bytes) -> bytes:
    _, Scrypt, _, _, _, _ = _require_crypto()
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(data: bytes, password: str) -> bytes:
    AESGCM, _, _, _, _, _ = _require_crypto()
    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = _derive_key(password, salt)
    aes = AESGCM(key)
    ciphertext = aes.encrypt(nonce, data, None)
    return MAGIC + salt + nonce + ciphertext


def decrypt_bytes(blob: bytes, password: str) -> bytes:
    if not blob.startswith(MAGIC):
        raise ValueError("invalid encrypted data")

    header_len = len(MAGIC)
    if len(blob) < header_len + SALT_LEN + NONCE_LEN + 1:
        raise ValueError("invalid encrypted data")

    salt_start = header_len
    salt_end = salt_start + SALT_LEN
    nonce_end = salt_end + NONCE_LEN

    salt = blob[salt_start:salt_end]
    nonce = blob[salt_end:nonce_end]
    ciphertext = blob[nonce_end:]

    AESGCM, _, _, _, _, _ = _require_crypto()
    key = _derive_key(password, salt)
    aes = AESGCM(key)
    return aes.decrypt(nonce, ciphertext, None)


def encrypt_file(in_path: Path, out_path: Path, password: str, *, overwrite: bool = False) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    _, _, Cipher, AES, GCM, _ = _require_crypto()

    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = _derive_key(password, salt)

    encryptor = Cipher(AES(key), GCM(nonce)).encryptor()

    with in_path.open("rb") as src, out_path.open("wb") as dst:
        dst.write(MAGIC)
        dst.write(salt)
        dst.write(nonce)

        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            dst.write(encryptor.update(chunk))

        dst.write(encryptor.finalize())
        dst.write(encryptor.tag)


def decrypt_file(in_path: Path, out_path: Path, password: str, *, overwrite: bool = False) -> None:
    if out_path.exists() and not overwrite:
        raise FileExistsError(str(out_path))

    _, _, Cipher, AES, GCM, InvalidTag = _require_crypto()

    with in_path.open("rb") as src:
        magic = src.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("invalid encrypted data")

        salt = src.read(SALT_LEN)
        nonce = src.read(NONCE_LEN)
        if len(salt) != SALT_LEN or len(nonce) != NONCE_LEN:
            raise ValueError("invalid encrypted data")

        file_size = in_path.stat().st_size
        header_len = len(MAGIC) + SALT_LEN + NONCE_LEN
        if file_size < header_len + TAG_LEN:
            raise ValueError("invalid encrypted data")

        src.seek(file_size - TAG_LEN)
        tag = src.read(TAG_LEN)
        if len(tag) != TAG_LEN:
            raise ValueError("invalid encrypted data")

        key = _derive_key(password, salt)
        decryptor = Cipher(AES(key), GCM(nonce, tag)).decryptor()

        remaining = file_size - header_len - TAG_LEN
        src.seek(header_len)

        with out_path.open("wb") as dst:
            while remaining > 0:
                to_read = min(CHUNK_SIZE, remaining)
                chunk = src.read(to_read)
                if not chunk:
                    raise ValueError("invalid encrypted data")
                remaining -= len(chunk)
                dst.write(decryptor.update(chunk))

            try:
                dst.write(decryptor.finalize())
            except InvalidTag as e:
                raise ValueError("invalid password or corrupted data") from e
