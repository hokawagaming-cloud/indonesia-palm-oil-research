"""Configuration loading. All paths are resolved relative to the project root."""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "quant" / "config"


def _load(name: str) -> dict[str, Any]:
    with open(CONFIG_DIR / name, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@dataclass(frozen=True)
class Config:
    settings: dict[str, Any]
    universe: dict[str, Any]
    sources: dict[str, Any]

    def path(self, key: str) -> Path:
        return PROJECT_ROOT / self.settings["storage"][key]

    @property
    def tickers(self) -> list[str]:
        return list(self.universe["tickers"].keys())

    @property
    def source_ids(self) -> set[str]:
        return set(self.sources["sources"].keys())


@lru_cache(maxsize=1)
def load_config() -> Config:
    return Config(settings=_load("settings.yaml"), universe=_load("universe.yaml"), sources=_load("sources.yaml"))
