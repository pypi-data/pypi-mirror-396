from pathlib import Path
from securezy.tools.crypto import decrypt_bytes, decrypt_file, encrypt_bytes, encrypt_file


def test_crypto_roundtrip_bytes() -> None:
    data = b"hello world"
    password = "correct horse battery staple"
    blob = encrypt_bytes(data, password)
    out = decrypt_bytes(blob, password)
    assert out == data


def test_crypto_roundtrip_file(tmp_path: Path) -> None:
    password = "correct horse battery staple"
    src = tmp_path / "src.bin"
    enc = tmp_path / "src.bin.sz"
    dec = tmp_path / "src.dec.bin"
 
    payload = b"abc" * (1024 * 50)
    src.write_bytes(payload)
 
    encrypt_file(src, enc, password)
    decrypt_file(enc, dec, password)
    assert dec.read_bytes() == payload
