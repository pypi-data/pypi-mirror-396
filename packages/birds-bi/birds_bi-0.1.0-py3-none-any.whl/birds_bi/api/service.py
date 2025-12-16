from dataclasses import dataclass
from ..config import RepoConfig, DatabaseConfig
from ..repo import RepoClient
from ..db import DatabaseClient
from ..engine.deploy.dim_deployer import deploy_dimension
from ..engine.inspection.lineage import get_tables_for_model

@dataclass
class BIService:
    repo_client: RepoClient
    db_client: DatabaseClient

    @classmethod
    def from_configs(cls, repo_config: RepoConfig, db_config: DatabaseConfig):
        return cls(RepoClient(repo_config), DatabaseClient(db_config))

    def list_models(self):
        return self.repo_client.list_models()

    def deploy_dimension(self, name: str, extra_params=None):
        return deploy_dimension(name, self.repo_client, self.db_client, extra_params)

    def get_tables_for_model(self, name: str):
        return get_tables_for_model(name, self.repo_client, self.db_client)
