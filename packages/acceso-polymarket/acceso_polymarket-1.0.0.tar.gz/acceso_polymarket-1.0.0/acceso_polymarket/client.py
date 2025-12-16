"""
Polymarket API Client
"""

import logging
from typing import Any, Dict, List, Optional, Union

import requests

from .types import (
    PolymarketConfig,
    Market,
    Event,
    OrderBook,
    Trade,
    Position,
    Order,
    PriceHistory,
    MarketStats,
)


class PolymarketError(Exception):
    """Exception raised for Polymarket API errors"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        status: Optional[int] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class PolymarketClient:
    """
    Client for Polymarket prediction markets via Acceso API.
    
    Example:
        >>> from acceso_polymarket import PolymarketClient, PolymarketConfig
        >>> 
        >>> client = PolymarketClient(PolymarketConfig(api_key="your_key"))
        >>> 
        >>> # Get active markets
        >>> markets = client.get_markets(limit=10)
        >>> for market in markets:
        ...     print(f"{market.question}: {market.outcome_prices}")
    """
    
    def __init__(self, config: Union[PolymarketConfig, Dict[str, Any]]):
        if isinstance(config, dict):
            config = PolymarketConfig(**config)
        
        self.config = config
        self.api_url = config.api_url.rstrip("/")
        self.timeout = config.timeout
        self.debug = config.debug
        
        self.logger = logging.getLogger("acceso_polymarket")
        if self.debug:
            self.logger.setLevel(logging.DEBUG)
        
        self._session = requests.Session()
        self._session.headers.update({
            "Content-Type": "application/json",
            "X-API-Key": config.api_key,
        })
    
    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Any:
        url = f"{self.api_url}{path}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                json=body,
                params=params,
                timeout=self.timeout,
            )
            
            data = response.json()
            
            if not response.ok:
                raise PolymarketError(
                    data.get("error", f"HTTP {response.status_code}"),
                    status=response.status_code,
                )
            
            return data.get("data", data)
            
        except requests.Timeout:
            raise PolymarketError("Request timeout", code="TIMEOUT")
        except requests.RequestException as e:
            raise PolymarketError(f"Network error: {e}", code="NETWORK_ERROR")
    
    # ========================================
    # Markets
    # ========================================
    
    def get_markets(
        self,
        active: bool = True,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Market]:
        """
        Get prediction markets.
        
        Args:
            active: Only active markets
            category: Filter by category
            limit: Max results
            offset: Pagination offset
        
        Returns:
            List of Market objects
        """
        params = {"active": active, "limit": limit, "offset": offset}
        if category:
            params["category"] = category
        
        data = self._request("GET", "/v1/polymarket/markets", params=params)
        return [Market.from_dict(m) for m in data]
    
    def get_market(self, market_id: str) -> Market:
        """Get a specific market by ID."""
        data = self._request("GET", f"/v1/polymarket/markets/{market_id}")
        return Market.from_dict(data)
    
    def search_markets(self, query: str, limit: int = 20) -> List[Market]:
        """Search markets by keyword."""
        data = self._request(
            "GET",
            "/v1/polymarket/markets/search",
            params={"q": query, "limit": limit},
        )
        return [Market.from_dict(m) for m in data]
    
    def get_trending_markets(self, limit: int = 10) -> List[Market]:
        """Get trending markets by volume."""
        data = self._request(
            "GET",
            "/v1/polymarket/markets/trending",
            params={"limit": limit},
        )
        return [Market.from_dict(m) for m in data]
    
    def get_market_stats(self, market_id: str) -> MarketStats:
        """Get market statistics."""
        data = self._request("GET", f"/v1/polymarket/markets/{market_id}/stats")
        return MarketStats.from_dict(data)
    
    # ========================================
    # Events
    # ========================================
    
    def get_events(
        self,
        active: bool = True,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Event]:
        """Get prediction events."""
        params = {"active": active, "limit": limit}
        if category:
            params["category"] = category
        
        data = self._request("GET", "/v1/polymarket/events", params=params)
        return [Event.from_dict(e) for e in data]
    
    def get_event(self, event_id: str) -> Event:
        """Get a specific event by ID."""
        data = self._request("GET", f"/v1/polymarket/events/{event_id}")
        return Event.from_dict(data)
    
    # ========================================
    # Order Book & Trading
    # ========================================
    
    def get_order_book(self, market_id: str, outcome: str) -> OrderBook:
        """Get order book for a market outcome."""
        data = self._request(
            "GET",
            f"/v1/polymarket/markets/{market_id}/orderbook",
            params={"outcome": outcome},
        )
        return OrderBook.from_dict(data)
    
    def get_trades(
        self,
        market_id: str,
        limit: int = 50,
    ) -> List[Trade]:
        """Get recent trades for a market."""
        data = self._request(
            "GET",
            f"/v1/polymarket/markets/{market_id}/trades",
            params={"limit": limit},
        )
        return [Trade.from_dict(t) for t in data]
    
    def get_price_history(
        self,
        market_id: str,
        outcome: str,
        interval: str = "1h",
        limit: int = 100,
    ) -> PriceHistory:
        """
        Get price history for an outcome.
        
        Args:
            market_id: Market ID
            outcome: Outcome name
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles
        """
        data = self._request(
            "GET",
            f"/v1/polymarket/markets/{market_id}/history",
            params={"outcome": outcome, "interval": interval, "limit": limit},
        )
        return PriceHistory.from_dict(data)
    
    # ========================================
    # User Operations
    # ========================================
    
    def get_positions(self, address: Optional[str] = None) -> List[Position]:
        """Get user's positions."""
        params = {}
        if address:
            params["address"] = address
        
        data = self._request("GET", "/v1/polymarket/positions", params=params)
        return [Position.from_dict(p) for p in data]
    
    def get_orders(
        self,
        status: str = "open",
        address: Optional[str] = None,
    ) -> List[Order]:
        """Get user's orders."""
        params = {"status": status}
        if address:
            params["address"] = address
        
        data = self._request("GET", "/v1/polymarket/orders", params=params)
        return [Order.from_dict(o) for o in data]
    
    def place_order(
        self,
        market_id: str,
        outcome: str,
        side: str,
        price: float,
        size: float,
    ) -> Order:
        """
        Place an order.
        
        Args:
            market_id: Market ID
            outcome: Outcome to trade
            side: "buy" or "sell"
            price: Limit price (0-1)
            size: Order size in shares
        
        Returns:
            Created Order
        """
        data = self._request(
            "POST",
            "/v1/polymarket/orders",
            body={
                "market_id": market_id,
                "outcome": outcome,
                "side": side,
                "price": price,
                "size": size,
            },
        )
        return Order.from_dict(data)
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        data = self._request("DELETE", f"/v1/polymarket/orders/{order_id}")
        return data.get("cancelled", False)
    
    # ========================================
    # Categories
    # ========================================
    
    def get_categories(self) -> List[str]:
        """Get available market categories."""
        data = self._request("GET", "/v1/polymarket/categories")
        return data
    
    def close(self) -> None:
        """Close the client session."""
        self._session.close()
    
    def __enter__(self) -> "PolymarketClient":
        return self
    
    def __exit__(self, *args) -> None:
        self.close()
