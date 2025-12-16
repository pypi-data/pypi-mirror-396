from securezy.tools.plugins import load_plugins


def test_plugins_include_hello() -> None:
    plugins = load_plugins()
    assert "hello" in plugins
