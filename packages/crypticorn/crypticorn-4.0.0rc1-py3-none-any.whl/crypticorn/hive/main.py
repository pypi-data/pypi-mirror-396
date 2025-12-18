from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from crypticorn.hive.client import (
    ApiClient,
    Configuration,
    ModelsApi,
    StatusApi,
)
from crypticorn.hive.wrapper import DataApiWrapper  # wraps DataApi

if TYPE_CHECKING:
    from aiohttp import ClientSession


class HiveClient(DataApiWrapper, ModelsApi, StatusApi):
    """
    A client for interacting with the Crypticorn Hive API.
    """

    config_class = Configuration

    def __init__(
        self,
        config: Configuration,
        http_client: Optional[ClientSession] = None,
        is_sync: bool = False,
    ):
        self.config = config
        self.base_client = ApiClient(configuration=self.config)
        if http_client is not None:
            self.base_client.rest_client.pool_manager = http_client
        # Pass sync context to REST client for proper session management
        self.base_client.rest_client.is_sync = is_sync
        super().__init__(self.base_client, is_sync=is_sync)
