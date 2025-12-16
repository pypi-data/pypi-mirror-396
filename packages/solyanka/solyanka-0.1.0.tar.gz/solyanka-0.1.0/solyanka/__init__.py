"""Solyanka – lightweight helpers for statement generation tooling."""

from importlib import metadata as importlib_metadata
from pathlib import Path

import tomllib

from .transaction_patterns.service import EEA_COUNTRIES, Pattern, PatternsService

__all__ = ["EEA_COUNTRIES", "Pattern", "PatternsService"]


def _read_local_version() -> str:
    root = Path(__file__).resolve().parent.parent
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return "0.0.0"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project", {})
    version = project.get("version")
    if isinstance(version, str):
        return version
    return "0.0.0"


try:
    __version__ = importlib_metadata.version("solyanka")
except importlib_metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = _read_local_version()
