import os

from langgraph_sdk import Auth

auth = Auth()


@auth.authenticate
async def authenticate() -> Auth.types.MinimalUserDict:
    return {"identity": "local_user", "imandra_api_key": os.environ["IMANDRA_API_KEY"]}


@auth.on
async def add_imandra_api_key(ctx: Auth.types.AuthContext, value: dict):
    """Add Imandra API Key to metadata implicitly."""
    metadata = value.setdefault("metadata", {})
    metadata.update({"imandra_api_key": ctx.user.imandra_api_key})
    return True
