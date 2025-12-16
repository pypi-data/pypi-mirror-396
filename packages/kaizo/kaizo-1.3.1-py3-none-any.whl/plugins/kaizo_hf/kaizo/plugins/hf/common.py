from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class HFDir:
    local: Path | None = None
    cache: Path | None = None


@dataclass(frozen=True)
class HFPatterns:
    allow: list[str] | str | None = None
    ignore: list[str] | str | None = None


@dataclass(frozen=True)
class HFCommit:
    message: str | None = None
    description: str | None = None
