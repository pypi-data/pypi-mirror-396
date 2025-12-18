from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from crypticorn.indicator.client import (
    ApiClient,
    Configuration,
    SentimentApi,
    NewsApi,
    PredictionsApi,
    StatusApi,
)

if TYPE_CHECKING:
    from aiohttp import ClientSession


class IndicatorClient(
    SentimentApi,
    NewsApi,
    PredictionsApi,
    StatusApi,
):
    """
    A client for interacting with the Crypticorn Indicator API.
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
