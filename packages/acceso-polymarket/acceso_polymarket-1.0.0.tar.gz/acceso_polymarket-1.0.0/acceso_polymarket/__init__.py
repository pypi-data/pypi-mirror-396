"""
Acceso Polymarket Python SDK - Prediction Markets

A Python SDK for Polymarket prediction markets via Acceso API.
"""

__version__ = "1.0.0"
__author__ = "Acceso"
__email__ = "dev@acceso.dev"

from .client import PolymarketClient, PolymarketError
from .types import (
    PolymarketConfig,
    Market,
    Event,
    OrderBook,
    Trade,
    Position,
    Order,
    PriceHistory,
)

__all__ = [
    "PolymarketClient",
    "PolymarketError",
    "PolymarketConfig",
    "Market",
    "Event",
    "OrderBook",
    "Trade",
    "Position",
    "Order",
    "PriceHistory",
]
