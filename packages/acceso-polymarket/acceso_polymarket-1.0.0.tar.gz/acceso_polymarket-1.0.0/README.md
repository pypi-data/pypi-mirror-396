# Acceso Polymarket Python SDK

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Polymarket](https://img.shields.io/badge/Polymarket-6366F1?style=for-the-badge&logo=chart-line&logoColor=white)

**Prediction Markets SDK for Python**

[Documentation](https://docs.acceso.dev) • [API Reference](https://api.acceso.dev/docs) • [Get API Key](https://acceso.dev)

</div>

---

## 📦 Installation

```bash
pip install acceso-polymarket
```

## ⚡ Quick Start

```python
from acceso_polymarket import PolymarketClient, PolymarketConfig

client = PolymarketClient(PolymarketConfig(api_key="your_key"))

# Get trending markets
markets = client.get_trending_markets(limit=5)
for market in markets:
    print(f"{market.question}")
    print(f"  Yes: {market.outcome_prices[0]:.0%}")
    print(f"  No: {market.outcome_prices[1]:.0%}")
    print(f"  Volume: ${market.volume:,.0f}")
```

## 📖 API Reference

### Markets

```python
# Get active markets
markets = client.get_markets(active=True, limit=50)

# Get specific market
market = client.get_market("market_id")

# Search markets
results = client.search_markets("election")

# Get trending markets
trending = client.get_trending_markets()
```

### Events

```python
# Get events
events = client.get_events(category="politics")

# Get specific event
event = client.get_event("event_id")
```

### Trading

```python
# Get order book
orderbook = client.get_order_book("market_id", "Yes")

# Get price history
history = client.get_price_history("market_id", "Yes", interval="1h")

# Place order
order = client.place_order(
    market_id="...",
    outcome="Yes",
    side="buy",
    price=0.55,
    size=100
)

# Cancel order
client.cancel_order("order_id")
```

### Positions

```python
# Get positions
positions = client.get_positions()

# Get orders
orders = client.get_orders(status="open")
```

## 📄 License

MIT © [Acceso](https://acceso.dev)
