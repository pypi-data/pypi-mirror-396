def get_tables_for_model(name, repo_client, db_client):
    model = repo_client.load_model(name)
    return model.tables_used
