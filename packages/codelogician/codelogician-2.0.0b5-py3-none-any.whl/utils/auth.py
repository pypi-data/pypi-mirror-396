from langgraph_sdk import Auth, get_client

auth = Auth()

USER_ID_HEADER = b"imandra-developer-email"

# Populated by the internal HTTPRoute
AGENT_HEADER = b"imandra-universe-agent"


@auth.authenticate
async def authenticate(
    authorization: str | None, headers: dict[bytes, bytes]
) -> Auth.types.MinimalUserDict:
    if (
        (user_id := headers.get(USER_ID_HEADER))
        and (auth_key := authorization)
        and auth_key.startswith("Bearer ")
        and (agent := headers.get(AGENT_HEADER))
    ):
        return {
            "identity": user_id.decode(),
            "imandra_api_key": auth_key.removeprefix("Bearer "),
            "imandra_universe_agent": agent.decode(),
        }
    else:
        raise Auth.exceptions.HTTPException(
            status_code=401, detail="Missing authentication"
        )


@auth.on.threads.create_run
async def check_assistant_id(ctx: Auth.types.AuthContext, value: Auth.types.RunsCreate):
    if assistant_id := value.get("assistant_id"):
        assistant = await get_client().assistants.get(str(assistant_id))
        if ctx.user.imandra_universe_agent == assistant["graph_id"]:
            return {"owner": ctx.user.identity}
        else:
            raise Auth.exceptions.HTTPException(
                status_code=401, detail="Requested graph not available"
            )
    else:
        raise Auth.exceptions.HTTPException(status_code=500, detail="Missing graph_id")


@auth.on
async def add_owner(ctx: Auth.types.AuthContext, value: dict):
    """Make resources private to their creator."""
    metadata = value.setdefault("metadata", {})
    metadata.update({"owner": ctx.user.identity})
    return {"owner": ctx.user.identity}


@auth.on.assistants.read
async def allow_get_assistants(
    ctx: Auth.types.AuthContext, value: Auth.types.AssistantsRead
):
    # Required for checking assistants on run creation
    return True


@auth.on.assistants.search
async def allow_search_assistants(
    ctx: Auth.types.AuthContext, value: Auth.types.AssistantsSearch
):
    # Allows access via LangGraph Platform Studio
    # Can't use {"graph_id": ctx.user.imandra_universe_agent}, filters apply to metadata
    return True


@auth.on.assistants
async def block_assistants(ctx: Auth.types.AuthContext, value: dict):
    """Block assistants API."""
    raise Auth.exceptions.HTTPException(
        status_code=403, detail="Assistants API is disabled"
    )


@auth.on.crons
async def block_crons(ctx: Auth.types.AuthContext, value: dict):
    """Block crons API."""
    raise Auth.exceptions.HTTPException(status_code=403, detail="Crons API is disabled")
