def params_for_bronze(params: dict) -> dict:
    return {k: v for k, v in params.items() if k.lower() != "key"}
