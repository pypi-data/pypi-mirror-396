"""
Type definitions for Polymarket SDK
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class PolymarketConfig:
    """Configuration for Polymarket client"""
    api_key: str
    api_url: str = "https://api.acceso.dev"
    timeout: int = 30
    debug: bool = False


@dataclass
class Market:
    """A prediction market"""
    id: str
    question: str
    description: str
    outcomes: List[str]
    outcome_prices: List[float]
    volume: float
    liquidity: float
    end_date: Optional[str] = None
    resolved: bool = False
    resolution: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None
    slug: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Market":
        return cls(
            id=data.get("id", ""),
            question=data.get("question", ""),
            description=data.get("description", ""),
            outcomes=data.get("outcomes", []),
            outcome_prices=data.get("outcome_prices", data.get("outcomePrices", [])),
            volume=float(data.get("volume", 0)),
            liquidity=float(data.get("liquidity", 0)),
            end_date=data.get("end_date", data.get("endDate")),
            resolved=data.get("resolved", False),
            resolution=data.get("resolution"),
            category=data.get("category"),
            image=data.get("image"),
            slug=data.get("slug"),
        )


@dataclass
class Event:
    """A prediction event containing multiple markets"""
    id: str
    title: str
    description: str
    markets: List[Market]
    category: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    image: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        markets = [Market.from_dict(m) for m in data.get("markets", [])]
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            markets=markets,
            category=data.get("category"),
            start_date=data.get("start_date", data.get("startDate")),
            end_date=data.get("end_date", data.get("endDate")),
            image=data.get("image"),
        )


@dataclass
class OrderBookLevel:
    """A level in the order book"""
    price: float
    size: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderBookLevel":
        return cls(
            price=float(data.get("price", 0)),
            size=float(data.get("size", 0)),
        )


@dataclass
class OrderBook:
    """Order book for a market outcome"""
    market_id: str
    outcome: str
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    spread: float = 0
    mid_price: float = 0
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrderBook":
        bids = [OrderBookLevel.from_dict(b) for b in data.get("bids", [])]
        asks = [OrderBookLevel.from_dict(a) for a in data.get("asks", [])]
        return cls(
            market_id=data.get("market_id", data.get("marketId", "")),
            outcome=data.get("outcome", ""),
            bids=bids,
            asks=asks,
            spread=float(data.get("spread", 0)),
            mid_price=float(data.get("mid_price", data.get("midPrice", 0))),
        )


@dataclass
class Trade:
    """A trade on a market"""
    id: str
    market_id: str
    outcome: str
    side: str  # "buy" or "sell"
    price: float
    size: float
    timestamp: str
    maker: Optional[str] = None
    taker: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Trade":
        return cls(
            id=data.get("id", ""),
            market_id=data.get("market_id", data.get("marketId", "")),
            outcome=data.get("outcome", ""),
            side=data.get("side", ""),
            price=float(data.get("price", 0)),
            size=float(data.get("size", 0)),
            timestamp=data.get("timestamp", ""),
            maker=data.get("maker"),
            taker=data.get("taker"),
        )


@dataclass
class Position:
    """A user's position in a market"""
    market_id: str
    outcome: str
    size: float
    avg_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Position":
        return cls(
            market_id=data.get("market_id", data.get("marketId", "")),
            outcome=data.get("outcome", ""),
            size=float(data.get("size", 0)),
            avg_price=float(data.get("avg_price", data.get("avgPrice", 0))),
            current_price=float(data.get("current_price", data.get("currentPrice", 0))),
            pnl=float(data.get("pnl", 0)),
            pnl_percent=float(data.get("pnl_percent", data.get("pnlPercent", 0))),
        )


@dataclass
class Order:
    """An order on a market"""
    id: str
    market_id: str
    outcome: str
    side: str  # "buy" or "sell"
    price: float
    size: float
    filled: float
    status: str  # "open", "filled", "cancelled", "expired"
    created_at: str
    expires_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Order":
        return cls(
            id=data.get("id", ""),
            market_id=data.get("market_id", data.get("marketId", "")),
            outcome=data.get("outcome", ""),
            side=data.get("side", ""),
            price=float(data.get("price", 0)),
            size=float(data.get("size", 0)),
            filled=float(data.get("filled", 0)),
            status=data.get("status", ""),
            created_at=data.get("created_at", data.get("createdAt", "")),
            expires_at=data.get("expires_at", data.get("expiresAt")),
        )


@dataclass
class PriceHistory:
    """Historical price data"""
    market_id: str
    outcome: str
    prices: List[Dict[str, Any]]  # [{timestamp, price}]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PriceHistory":
        return cls(
            market_id=data.get("market_id", data.get("marketId", "")),
            outcome=data.get("outcome", ""),
            prices=data.get("prices", []),
        )


@dataclass
class MarketStats:
    """Market statistics"""
    market_id: str
    volume_24h: float
    trades_24h: int
    unique_traders: int
    price_change_24h: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketStats":
        return cls(
            market_id=data.get("market_id", data.get("marketId", "")),
            volume_24h=float(data.get("volume_24h", data.get("volume24h", 0))),
            trades_24h=int(data.get("trades_24h", data.get("trades24h", 0))),
            unique_traders=int(data.get("unique_traders", data.get("uniqueTraders", 0))),
            price_change_24h=float(data.get("price_change_24h", data.get("priceChange24h", 0))),
        )
