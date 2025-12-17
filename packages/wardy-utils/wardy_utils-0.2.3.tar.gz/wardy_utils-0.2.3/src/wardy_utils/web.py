"""General internet helpers."""

from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import Final, Literal, overload

from hishel import AsyncSqliteStorage, CacheOptions, SpecificationPolicy, SyncSqliteStorage
from hishel.httpx import AsyncCacheClient, SyncCacheClient

logging.getLogger("httpcore").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# ----- Constants -----

CACHE: Final = timedelta(minutes=30).total_seconds()
TIMEOUT: Final = timedelta(seconds=45).total_seconds()


# ----- Handle httpx client and hishel caching -----


@overload
def cached_client() -> SyncCacheClient: ...
@overload
def cached_client(
    *, sync: Literal[True], force: bool = ..., ttl: float = CACHE, timeout: float = TIMEOUT
) -> SyncCacheClient: ...
@overload
def cached_client(
    *, sync: Literal[False], force: bool = ..., ttl: float = CACHE, timeout: float = TIMEOUT
) -> AsyncCacheClient: ...


def cached_client(
    *, sync: bool = True, force: bool = False, ttl: float = CACHE, timeout: float = TIMEOUT
) -> SyncCacheClient | AsyncCacheClient:
    """Return a cached HTTPX sync client.

    Args:
        sync (bool): Whether to use sync or async client. Defaults to True.
        force (bool): Whether to force cache. Defaults to False.
        ttl (float): Time to live for cache entries in seconds. Defaults to 30 minutes.
        timeout (float): Timeout for requests in seconds. Defaults to 45 seconds.

    Returns:
        hishel.CacheClient: A cached HTTPX client.
    """
    storage = (
        SyncSqliteStorage(default_ttl=ttl) if sync else AsyncSqliteStorage(default_ttl=ttl)
    )
    policy = (
        SpecificationPolicy(cache_options=CacheOptions(allow_stale=True)) if force else None
    )

    client = SyncCacheClient if sync else AsyncCacheClient

    return client(
        follow_redirects=True, storage=storage, policy=policy, timeout=timeout, http2=True
    )


sync_client = cached_client(sync=True)
sync_force_client = cached_client(sync=True, force=True)
async_client = cached_client(sync=False)
async_force_client = cached_client(sync=False, force=True)

if os.getenv("LOGFIRE_TOKEN"):
    try:
        import logfire
    except ImportError:
        logger.exception("logfire is not installed, skipping HTTPX instrumentation.")
    else:
        logfire.instrument_httpx()

# -----
