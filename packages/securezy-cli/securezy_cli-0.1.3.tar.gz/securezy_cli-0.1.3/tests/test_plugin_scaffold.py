from pathlib import Path

from securezy.tools.plugin_scaffold import create_plugin_skeleton


def test_create_plugin_skeleton(tmp_path: Path) -> None:
    created = create_plugin_skeleton(plugin_name="demo", out_dir=tmp_path)
    assert (created / "pyproject.toml").exists()
    assert (created / "README.md").exists()
    assert (created / "src").exists()
