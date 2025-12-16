from securezy.tools.hashing import hash_text


def test_hash_text_md5() -> None:
    assert hash_text("md5", "letmein") == "0d107d09f5bbe40cade3de5c71e9e9b7"
