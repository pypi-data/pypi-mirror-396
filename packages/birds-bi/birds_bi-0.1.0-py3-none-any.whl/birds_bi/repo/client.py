import json
from pathlib import Path
from typing import List
from ..core.models import ModelDefinition
from ..exceptions import RepositoryError
from ..config import RepoConfig

class RepoClient:
    def __init__(self, config: RepoConfig):
        self.config = config

    def list_models(self) -> List[str]:
        root = self.config.root_path
        return sorted(p.stem for p in root.glob("*.json"))

    def load_model(self, name: str) -> ModelDefinition:
        path = self.config.root_path / f"{name}.json"
        if not path.exists():
            raise RepositoryError(f"Model JSON not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("name", name)
        return ModelDefinition.from_json(data)
