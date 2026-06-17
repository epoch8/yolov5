"""Build a pip-installable yolov5 package without changing the repo layout."""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import setuptools

BASE_DIR = Path(__file__).resolve().parent
PKG_DIR = BASE_DIR / "yolov5"

ROOT_FILES = (
    "benchmarks.py",
    "detect.py",
    "export.py",
    "hubconf.py",
    "train.py",
    "val.py",
)
ROOT_DIRS = ("classify", "data", "models", "segment", "utils")


def _package_version() -> str:
    """CalVer from the HEAD commit date: YYYY.M.D (PEP 440)."""
    try:
        commit_date = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "HEAD"],
            cwd=BASE_DIR,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        year, month, day = commit_date.split("-")
        return f"{year}.{int(month)}.{int(day)}"
    except (OSError, subprocess.CalledProcessError, ValueError):
        source_date_epoch = __import__("os").environ.get("SOURCE_DATE_EPOCH")
        if source_date_epoch:
            dt = datetime.fromtimestamp(int(source_date_epoch), tz=timezone.utc)
            return f"{dt.year}.{dt.month}.{dt.day}"
        return "0.0.0"


def stage_package_tree(version: str) -> None:
    if PKG_DIR.exists():
        shutil.rmtree(PKG_DIR)
    PKG_DIR.mkdir(parents=True)

    for name in ROOT_FILES:
        shutil.copy2(BASE_DIR / name, PKG_DIR / name)
    for name in ROOT_DIRS:
        shutil.copytree(BASE_DIR / name, PKG_DIR / name)

    PKG_DIR.joinpath("__init__.py").write_text(
        "\n".join(
            [
                '"""Pip package tree staged from the repository root by setup.py."""',
                "from pathlib import Path",
                "",
                "ROOT = Path(__file__).resolve().parent",
                f'__version__ = "{version}"',
                "",
            ]
        ),
        encoding="utf-8",
    )


PACKAGE_VERSION = _package_version()
stage_package_tree(PACKAGE_VERSION)

setuptools.setup(
    name="yolov5",
    version=PACKAGE_VERSION,
    description="Ultralytics YOLOv5 packaged for pip install",
    long_description=(BASE_DIR / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/epoch8/yolov5",
    license="AGPL-3.0",
    packages=setuptools.find_packages(include=["yolov5", "yolov5.*"]),
    python_requires=">=3.10",
    include_package_data=True,
)
