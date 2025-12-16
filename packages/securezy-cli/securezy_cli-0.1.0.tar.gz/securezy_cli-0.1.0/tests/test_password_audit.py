from securezy.tools.password_audit import audit_password


def test_password_audit_found(tmp_path) -> None:
    wl = tmp_path / "wl.txt"
    wl.write_text("password\nadmin\nletmein\n", encoding="utf-8")
    r = audit_password(password="letmein", wordlist_path=wl)
    assert r.found is True


def test_password_audit_not_found(tmp_path) -> None:
    wl = tmp_path / "wl.txt"
    wl.write_text("password\nadmin\n", encoding="utf-8")
    r = audit_password(password="letmein", wordlist_path=wl)
    assert r.found is False
