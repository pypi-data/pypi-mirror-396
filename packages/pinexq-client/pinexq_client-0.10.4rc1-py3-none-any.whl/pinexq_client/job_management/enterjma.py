from typing import TypeVar, Type

import httpx
from httpx import Client, _config
# from hishel.httpx import SyncCacheClient
from httpx_caching import CachingClient

import warnings

from pinexq_client.core import Entity
from pinexq_client.core.enterapi import enter_api
from pinexq_client.core.hco.hco_base import Hco
from pinexq_client.job_management.hcos.entrypoint_hco import EntryPointHco
from pinexq_client.job_management.model.sirenentities import EntryPointEntity
import pinexq_client.job_management

THco = TypeVar("THco", bound=Hco)


def _version_match_major_minor(ver1: list[int], ver2: list[int]) -> bool:
    return all([v1 == v2 for v1, v2 in zip(ver1[:2], ver2[:2])])

def create_pinexq_client(
        pinexq_api_endpoint: str,
        api_key:str,
        timeout: _config.TimeoutTypes = _config.DEFAULT_TIMEOUT_CONFIG,
        use_client_cache: bool = True) -> httpx.Client:
    """
    Will create a httpx client, optional with caching, to be used with the API objects.

    Args:
        pinexq_api_endpoint: The endpoint for the pinexq API.
        api_key: The API key for the pinexq API.
        timeout: The timeout passed to the http client for operations.
        use_client_cache: Whether to use a httpx client with caching.

    """

    headers = { 'x-api-key': api_key }
    if use_client_cache:
        # for now, we use the persistent cache, which is also shared between instances
        # use  if you need each client to have a own cache storage=InMemoryStorage()
        # broken, will cache SSE stream
        #return SyncCacheClient(
        #    base_url=pinexq_api_endpoint,
        #    headers=headers,
        #    timeout=timeout)
        client = Client(
            base_url=pinexq_api_endpoint,
            headers=headers,
            timeout=timeout)
        return CachingClient(client)
    else:
        return Client(
            base_url=pinexq_api_endpoint,
            headers=headers,
            timeout=timeout)


def enter_jma(
    client: httpx.Client,
    entrypoint_hco_type: Type[THco] = EntryPointHco,
    entrypoint_entity_type: Type[Entity] = EntryPointEntity,
    entrypoint: str = "api/EntryPoint",
) -> EntryPointHco:
    """
    Gets the entrypoint object for the pinexq API. Will use the configured base url from the client.
    Will check the current API version against the version of the client to ensure compatibility.

    Args:
        client: The configured pinexq client.
        entrypoint_hco_type: The type to represent the api resource of the  entrypoint object [optional].
        entrypoint_entity_type: The type of the entrypoint object containing typed properties [optional].
        entrypoint: The path segment leading to the api entrypoint resource [optional].
    """
    entry_point_hco = enter_api(client, entrypoint_hco_type, entrypoint_entity_type, entrypoint)

    info = entry_point_hco.info_link.navigate()

    # Check for matching protocol versions
    client_version = pinexq_client.job_management.__jma_version__
    jma_version = [int(i) for i in str.split(info.api_version, '.')]
    if not _version_match_major_minor(jma_version, client_version):
        warnings.warn(
            f"Version mismatch between 'pinexq_client' (v{'.'.join(map(str ,client_version))}) "
            f"and 'JobManagementAPI' (v{'.'.join(map(str, jma_version))})! "
        )

    return entry_point_hco
