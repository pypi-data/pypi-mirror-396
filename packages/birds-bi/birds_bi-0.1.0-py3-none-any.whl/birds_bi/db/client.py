from sqlalchemy import create_engine, text

class DatabaseClient:
    def __init__(self, config):
        self.engine = create_engine(config.url, echo=config.echo, future=True)

    def execute_sql(self, sql: str, params=None, fetch="all"):
        params = params or {}
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params)
            if fetch == "none":
                return None
            if fetch == "one":
                return result.mappings().first()
            return result.mappings().all()

    def execute_procedure(self, name: str, params=None, fetch="none"):
        params = params or {}
        assign = ", ".join(f"@{k}=:{k}" for k in params)
        sql = f"EXEC {name} {assign}" if params else f"EXEC {name}"
        return self.execute_sql(sql, params=params, fetch=fetch)
