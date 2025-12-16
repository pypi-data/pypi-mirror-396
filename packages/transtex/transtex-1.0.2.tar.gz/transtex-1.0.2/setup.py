from __future__ import annotations

import pathlib
import tomllib
from setuptools import find_packages, setup


BASE_DIR = pathlib.Path(__file__).parent
PYPROJECT = tomllib.loads((BASE_DIR / "pyproject.toml").read_text())
PROJECT = PYPROJECT.get("project", {})


def _read_long_description() -> str:
    readme_path = BASE_DIR / PROJECT.get("readme", "README.md")
    return readme_path.read_text(encoding="utf-8") if readme_path.exists() else PROJECT.get("description", "")


setup(
    name=PROJECT.get("name"),
    version=PROJECT.get("version"),
    description=PROJECT.get("description", ""),
    long_description=_read_long_description(),
    long_description_content_type="text/markdown",
    python_requires=PROJECT.get("requires-python", ">=3.12"),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=PROJECT.get("dependencies", []),
    license=PROJECT.get("license", {}).get("text") if isinstance(PROJECT.get("license"), dict) else None,
    project_urls=PROJECT.get("urls") or {},
)
