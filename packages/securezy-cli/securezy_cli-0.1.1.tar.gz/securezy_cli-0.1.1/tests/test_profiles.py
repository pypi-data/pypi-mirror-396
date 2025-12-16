from securezy.tools.profiles import PortScanProfile, get_profile, list_profiles, set_profile


def test_profiles_roundtrip(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("SECUREZY_HOME", str(tmp_path))

    p = PortScanProfile(name="local", target="127.0.0.1", ports="1-10", concurrency=50, timeout=0.2)
    set_profile(p)

    got = get_profile("local")
    assert got.target == "127.0.0.1"

    allp = list_profiles()
    assert [x.name for x in allp] == ["local"]
