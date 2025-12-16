from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal

@dataclass
class RepoConfig:
    location: str
    repo_type: Literal["filesystem"] = "filesystem"

    @property
    def root_path(self) -> Path:
        return Path(self.location)

@dataclass
class DatabaseConfig:
    url: str
    echo: bool = False
    schema: Optional[str] = None
