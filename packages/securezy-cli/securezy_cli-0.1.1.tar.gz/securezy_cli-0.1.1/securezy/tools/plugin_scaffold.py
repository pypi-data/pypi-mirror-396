from __future__ import annotations

import re
from pathlib import Path


def _sanitize_slug(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9_-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        raise ValueError("invalid name")
    return s


def _sanitize_module(name: str) -> str:
    s = name.strip().lower().replace("-", "_")
    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        raise ValueError("invalid module name")
    if s[0].isdigit():
        s = f"p_{s}"
    return s


def create_plugin_skeleton(
    *,
    plugin_name: str,
    out_dir: Path,
    overwrite: bool = False,
) -> Path:
    slug = _sanitize_slug(plugin_name)
    module = _sanitize_module(plugin_name)

    project_dir = out_dir / f"securezy-plugin-{slug}"
    if project_dir.exists() and not overwrite:
        raise FileExistsError(str(project_dir))

    project_dir.mkdir(parents=True, exist_ok=True)

    pyproject = project_dir / "pyproject.toml"
    readme = project_dir / "README.md"
    src_dir = project_dir / "src" / module
    src_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "__init__.py").write_text("__all__ = ['plugin']\n", encoding="utf-8")

    (src_dir / "plugin.py").write_text(
        "from __future__ import annotations\n\n"
        "from typing import List\n\n\n"
        "def run(args: List[str]) -> int:\n"
        "    msg = ' '.join(args) if args else 'hello from plugin'\n"
        "    print(msg)\n"
        "    return 0\n",
        encoding="utf-8",
    )

    pyproject.write_text(
        "[build-system]\n"
        "requires = ['hatchling>=1.21.0']\n"
        "build-backend = 'hatchling.build'\n\n"
        "[project]\n"
        f"name = 'securezy-plugin-{slug}'\n"
        "version = '0.1.0'\n"
        "description = 'Securezy plugin'\n"
        "readme = 'README.md'\n"
        "requires-python = '>=3.9'\n"
        "dependencies = ['securezy-cli>=0.1.0']\n\n"
        f"[project.entry-points.'securezy.plugins']\n"
        f"{slug} = '{module}.plugin:run'\n\n"
        "[tool.hatch.build.targets.wheel]\n"
        f"packages = ['src/{module}']\n",
        encoding="utf-8",
    )

    readme.write_text(
        "# Securezy Plugin\n\n"
        "## Install\n\n"
        "```powershell\n"
        "py -m venv .venv\n"
        ".\\.venv\\Scripts\\python -m pip install -U pip\n"
        ".\\.venv\\Scripts\\python -m pip install -e .\n"
        "```\n\n"
        "## Run\n\n"
        "```powershell\n"
        f".\\.venv\\Scripts\\python -m securezy plugins list\n"
        f".\\.venv\\Scripts\\python -m securezy plugins run {slug} \"hello\"\n"
        "```\n",
        encoding="utf-8",
    )

    return project_dir
