from __future__ import annotations

from typing import TYPE_CHECKING, Awaitable, Optional, Union

from pydantic import StrictInt, StrictStr

from crypticorn._internal.utils import optional_import
from crypticorn.metrics import (
    ExchangesApi,
    MarketcapApi,
    MarketType,
    TimeInterval,
    TokensApi,
    TradingStatus,
)

try:
    import pandas as pd
except ImportError:
    pd = None

if TYPE_CHECKING:
    pass


class MarketcapApiWrapper(MarketcapApi):
    """
    A wrapper for the MarketcapApi class.
    """

    def get_marketcap_symbols_fmt(
        self,
        start_timestamp: Optional[StrictInt] = None,
        end_timestamp: Optional[StrictInt] = None,
        interval: Optional[StrictStr] = None,
        market: Optional[MarketType] = None,
        exchange: Optional[StrictStr] = None,
        **kwargs,
    ) -> Union["pd.DataFrame", Awaitable["pd.DataFrame"]]:
        """
        Get the marketcap symbols in a pandas dataframe
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_marketcap_symbols_fmt_sync(
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                interval=interval,
                market=market,
                exchange=exchange,
                **kwargs,
            )
        else:
            return self._get_marketcap_symbols_fmt_async(
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                interval=interval,
                market=market,
                exchange=exchange,
                **kwargs,
            )

    def _get_marketcap_symbols_fmt_sync(
        self,
        start_timestamp: Optional[StrictInt] = None,
        end_timestamp: Optional[StrictInt] = None,
        interval: Optional[StrictStr] = None,
        market: Optional[MarketType] = None,
        exchange: Optional[StrictStr] = None,
        **kwargs,
    ) -> "pd.DataFrame":
        """
        Get the marketcap symbols in a pandas dataframe (sync version)
        """
        pd = optional_import("pandas", "extra")
        response = self._get_marketcap_symbols_sync(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            interval=interval,
            market=market,
            exchange=exchange,
            **kwargs,
        )
        rows = []
        for item in response:
            row: dict[Union[int, str], Union[int, str, None]] = {
                "timestamp": item.timestamp
            }
            row.update({i + 1: sym for i, sym in enumerate(item.symbols)})
            rows.append(row)
        df = pd.DataFrame(rows)
        return df

    async def _get_marketcap_symbols_fmt_async(
        self,
        start_timestamp: Optional[StrictInt] = None,
        end_timestamp: Optional[StrictInt] = None,
        interval: Optional[StrictStr] = None,
        market: Optional[MarketType] = None,
        exchange: Optional[StrictStr] = None,
        **kwargs,
    ) -> "pd.DataFrame":
        """
        Get the marketcap symbols in a pandas dataframe (async version)
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_marketcap_symbols_async(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            interval=interval,
            market=market,
            exchange=exchange,
            **kwargs,
        )
        rows = []
        for item in response:
            row: dict[Union[int, str], Union[int, str, None]] = {
                "timestamp": item.timestamp
            }
            row.update({i + 1: sym for i, sym in enumerate(item.symbols)})
            rows.append(row)
        df = pd.DataFrame(rows)
        return df


class TokensApiWrapper(TokensApi):
    """
    A wrapper for the TokensApi class.
    """

    def get_stable_tokens_fmt(
        self, **kwargs
    ) -> Union["pd.DataFrame", Awaitable["pd.DataFrame"]]:
        """
        Get the tokens in a pandas dataframe
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_stable_tokens_fmt_sync(**kwargs)
        else:
            return self._get_stable_tokens_fmt_async(**kwargs)

    def _get_stable_tokens_fmt_sync(self, **kwargs) -> "pd.DataFrame":
        """
        Get the tokens in a pandas dataframe (sync version)
        """
        pd = optional_import("pandas", "extra")
        response = self._get_stable_tokens_sync(**kwargs)
        return pd.DataFrame(response)

    async def _get_stable_tokens_fmt_async(self, **kwargs) -> "pd.DataFrame":
        """
        Get the tokens in a pandas dataframe (async version)
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_stable_tokens_async(**kwargs)
        return pd.DataFrame(response)

    def get_wrapped_tokens_fmt(
        self, **kwargs
    ) -> Union["pd.DataFrame", Awaitable["pd.DataFrame"]]:
        """
        Get the wrapped tokens in a pandas dataframe
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_wrapped_tokens_fmt_sync(**kwargs)
        else:
            return self._get_wrapped_tokens_fmt_async(**kwargs)

    def _get_wrapped_tokens_fmt_sync(self, **kwargs) -> "pd.DataFrame":
        """
        Get the wrapped tokens in a pandas dataframe (sync version)
        """
        pd = optional_import("pandas", "extra")
        response = self._get_wrapped_tokens_sync(**kwargs)
        return pd.DataFrame(response)

    async def _get_wrapped_tokens_fmt_async(self, **kwargs) -> "pd.DataFrame":
        """
        Get the wrapped tokens in a pandas dataframe (async version)
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_wrapped_tokens_async(**kwargs)
        return pd.DataFrame(response)


class ExchangesApiWrapper(ExchangesApi):
    """
    A wrapper for the ExchangesApi class.
    """

    def get_available_exchanges_fmt(
        self,
        market: MarketType,
        symbol: StrictStr,
        interval: Optional[TimeInterval] = None,
        start_timestamp: Optional[StrictInt] = None,
        end_timestamp: Optional[StrictInt] = None,
        quote_currency: Optional[StrictStr] = None,
        status: Optional[TradingStatus] = None,
        **kwargs,
    ) -> Union["pd.DataFrame", Awaitable["pd.DataFrame"]]:
        """
        Get the exchanges in a pandas dataframe
        Works in both sync and async contexts.
        """
        if self.is_sync:
            return self._get_available_exchanges_fmt_sync(
                market=market,
                symbol=symbol,
                interval=interval,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                quote_currency=quote_currency,
                status=status,
                **kwargs,
            )
        else:
            return self._get_available_exchanges_fmt_async(
                market=market,
                symbol=symbol,
                interval=interval,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                quote_currency=quote_currency,
                status=status,
                **kwargs,
            )

    def _get_available_exchanges_fmt_sync(
        self,
        market: MarketType,
        symbol: StrictStr,
        interval: Optional[TimeInterval] = None,
        start_timestamp: Optional[StrictInt] = None,
        end_timestamp: Optional[StrictInt] = None,
        quote_currency: Optional[StrictStr] = None,
        status: Optional[TradingStatus] = None,
        **kwargs,
    ) -> "pd.DataFrame":  # noqa: F821
        """
        Get the exchanges in a pandas dataframe (sync version)
        """
        pd = optional_import("pandas", "extra")
        response = self._get_available_exchanges_sync(
            market=market,
            symbol=symbol,
            interval=interval,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            quote_currency=quote_currency,
            status=status,
            **kwargs,
        )

        # Create list of dictionaries with timestamp and flattened exchange data
        rows = []
        for item in response:
            row: dict[str, Union[int, bool]] = {"timestamp": item.timestamp}
            row.update(
                item.exchanges
            )  # This spreads the exchanges dict into individual columns
            rows.append(row)

        df = pd.DataFrame(rows)
        return df

    async def _get_available_exchanges_fmt_async(
        self,
        market: MarketType,
        symbol: StrictStr,
        interval: Optional[TimeInterval] = None,
        start_timestamp: Optional[StrictInt] = None,
        end_timestamp: Optional[StrictInt] = None,
        quote_currency: Optional[StrictStr] = None,
        status: Optional[TradingStatus] = None,
        **kwargs,
    ) -> "pd.DataFrame":  # noqa: F821
        """
        Get the exchanges in a pandas dataframe (async version)
        """
        pd = optional_import("pandas", "extra")
        response = await self._get_available_exchanges_async(
            market=market,
            symbol=symbol,
            interval=interval,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            quote_currency=quote_currency,
            status=status,
            **kwargs,
        )

        # Create list of dictionaries with timestamp and flattened exchange data
        rows = []
        for item in response:
            row: dict[str, Union[int, bool]] = {"timestamp": item.timestamp}
            row.update(
                item.exchanges
            )  # This spreads the exchanges dict into individual columns
            rows.append(row)

        df = pd.DataFrame(rows)
        return df
