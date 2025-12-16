from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Literal

ModelType = Literal["dimension", "fact", "view", "other"]

@dataclass
class ModelDefinition:
    name: str
    type: ModelType
    deploy_procedure: Optional[str] = None
    tables_used: List[str] = field(default_factory=list)
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(
            name=data.get("name"),
            type=data.get("type", "other"),
            deploy_procedure=data.get("deploy_procedure"),
            tables_used=data.get("tables_used", []),
            description=data.get("description"),
            metadata=data.get("metadata", {}),
        )
