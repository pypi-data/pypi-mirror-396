"""
1. To use FDB
```python
from utils.context import fdb
from agents.code_logician.graph import graph

async def your_function():
    async with fdb():
        await graph.invoke(...)
```

2. To use FDB in a notebook, execute the following code at the beginning cell of the
notebook.
```python
import asyncio
import atexit

from utils.context import fdb as fdb_context

# Global variables to store the connection manager and instance
_fdb_context_manager = None
_fdb_instance = None

async def init_fdb():
    global _fdb_context_manager, _fdb_instance
    if _fdb_instance is None:
        _fdb_context_manager = fdb_context()
        _fdb_instance = await _fdb_context_manager.__aenter__()
    return _fdb_instance

# Function to clean up resources when notebook kernel shuts down
async def cleanup_fdb():
    global _fdb_context_manager, _fdb_instance
    if _fdb_context_manager is not None and _fdb_instance is not None:
        await _fdb_context_manager.__aexit__(None, None, None)
        _fdb_instance = None
        _fdb_context_manager = None

# Register cleanup to happen at kernel shutdown
def cleanup_wrapper():
    asyncio.run(cleanup_fdb())

atexit.register(cleanup_wrapper)

fdb = await init_fdb()
```
"""

from __future__ import annotations

import asyncio
import datetime
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from os import environ

from asyncpg.pool import create_pool
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from fastapi import FastAPI
from google.auth.credentials import TokenState
from google.auth.transport import requests
from google.cloud.sql.connector import create_async_connector
from google.cloud.sql.connector.client import API_VERSION, CloudSQLClient
from google.cloud.sql.connector.connection_info import ConnectionInfo
from google.cloud.sql.connector.connection_name import ConnectionName
from google.cloud.sql.connector.refresh_utils import _downscope_credentials, retry_50x
from pgvector.asyncpg import register_vector

from .fdb.fdb import FDB, create_fdb

db_config = {
    "db": environ.get("IU_FDB_DB_NAME", "iu_fdb"),
    "user": environ.get("IU_FDB_DB_USER"),
}

super_get_connection_info = CloudSQLClient.get_connection_info


# This is required to get the credentials refresh (blocking) off the async context
async def get_connection_info(
    self,
    conn_name: ConnectionName,
    keys: asyncio.Future,
    enable_iam_auth: bool,
) -> ConnectionInfo:
    # before making Cloud SQL Admin API calls, refresh creds if required
    if self._credentials.token_state != TokenState.FRESH:
        # Note: this is the edit - using the async credentials
        await asyncio.to_thread(self._credentials.refresh, requests.Request())
    return await super_get_connection_info(self, conn_name, keys, enable_iam_auth)


CloudSQLClient.get_connection_info = get_connection_info  # ty: ignore[invalid-assignment]


async def _get_ephemeral(
    self,
    project: str,
    instance: str,
    pub_key: str,
    enable_iam_auth: bool = False,
) -> tuple[str, datetime.datetime]:
    """Asynchronously requests an ephemeral certificate from the Cloud SQL Instance.

    Args:
        project (str):  A string representing the name of the project.
        instance (str):  string representing the name of the instance.
        pub_key (str): A string representing PEM-encoded RSA public key.
        enable_iam_auth (bool): Enables automatic IAM database
             authentication for Postgres or MySQL instances.

    Returns:
        A tuple containing an ephemeral certificate from
        the Cloud SQL instance as well as a datetime object
        representing the expiration time of the certificate.
    """
    headers = {
        "Authorization": f"Bearer {self._credentials.token}",
    }

    url = (
        f"{self._sqladmin_api_endpoint}/sql/{API_VERSION}/projects/{project}"
        + f"/instances/{instance}:generateEphemeralCert"
    )

    data = {"public_key": pub_key}

    # Note: this is the changed part!
    # Ee need to run the credential refresh away from the the async threads
    if enable_iam_auth:
        # down-scope credentials with only IAM login scope (refreshes them too)
        login_creds = await asyncio.to_thread(_downscope_credentials, self._credentials)
        data["access_token"] = login_creds.token

    resp = await self._client.post(url, headers=headers, json=data)
    if resp.status >= 500:
        resp = await retry_50x(self._client.post, url, headers=headers, json=data)
    # try to get response json for better error message
    try:
        ret_dict = await resp.json()
        if resp.status >= 400:
            # if detailed error message is in json response, use as error message
            message = ret_dict.get("error", {}).get("message")
            if message:
                resp.reason = message
    # skip, raise_for_status will catch all errors in finally block
    except Exception:
        pass
    finally:
        resp.raise_for_status()

    ephemeral_cert: str = ret_dict["ephemeralCert"]["cert"]

    # decode cert to read expiration
    x509 = load_pem_x509_certificate(ephemeral_cert.encode("UTF-8"), default_backend())
    expiration = x509.not_valid_after_utc
    # for IAM authentication OAuth2 token is embedded in cert so it
    # must still be valid for successful connection
    if enable_iam_auth:
        token_expiration: datetime.datetime = login_creds.expiry
        # google.auth library strips timezone info for backwards compatibality
        # reasons with Python 2. Add it back to allow timezone aware datetimes.
        # Ref: https://github.com/googleapis/google-auth-library-python/blob/49a5ff7411a2ae4d32a7d11700f9f961c55406a9/google/auth/_helpers.py#L93-L99
        token_expiration = token_expiration.replace(tzinfo=datetime.UTC)

        if expiration > token_expiration:
            expiration = token_expiration
    return ephemeral_cert, expiration


CloudSQLClient._get_ephemeral = _get_ephemeral  # ty: ignore[invalid-assignment]


@asynccontextmanager
async def fdb() -> AsyncGenerator[FDB, None]:
    if environ.get("FDB_ENV") != "local":
        async with await create_async_connector(enable_iam_auth=True) as connector:

            async def getconn(instance_name, **kwargs):
                return await connector.connect_async(instance_name, "asyncpg", **kwargs)

            async def initconn(conn):
                await register_vector(conn)

            async with create_pool(
                environ["CLOUD_SQL_INSTANCE"],
                min_size=2,
                max_size=10,
                command_timeout=30,
                connect=getconn,
                init=initconn,
                **db_config,
            ) as pg_pool:
                yield create_fdb(pg_pool)

    else:

        async def initconn(conn):
            await register_vector(conn)

        env_prefix = "LOCAL_FDB_"
        async with create_pool(
            database="iu_fdb",
            host=environ.get(env_prefix + "HOST"),
            port=environ.get(env_prefix + "PORT"),
            user=environ.get(env_prefix + "USER"),
            password=environ.get(env_prefix + "PASSWORD"),
            min_size=2,
            init=initconn,
        ) as pg_pool:
            yield create_fdb(pg_pool)


@asynccontextmanager
async def fdb_lifespan(server: FastAPI) -> AsyncGenerator[None, None]:
    async with fdb():
        yield


def with_fdb(func):
    """A decorator to wrap the function with the fdb context.
    Example:
        ```python
        @with_fdb
        async def your_function():
            ...

        your_function()  # fdb context will be entered here
        ```
    """

    async def wrapper(*args, **kwargs):
        async with fdb():
            return await func(*args, **kwargs)

    return wrapper
