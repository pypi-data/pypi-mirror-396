def deploy_fact(name, repo_client, db_client, extra_params=None):
    model = repo_client.load_model(name)
    if not model.deploy_procedure:
        raise ValueError(f"Fact {name} has no deploy_procedure defined.")
    return db_client.execute_procedure(model.deploy_procedure, params=extra_params or {}, fetch="none")
