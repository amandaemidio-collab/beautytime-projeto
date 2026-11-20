"""Formatting helpers shared by BeautyTime pages."""


def price_label(price_cents: int) -> str:
    """Format an integer amount in cents as Brazilian reais."""
    return f"R$ {price_cents // 100},{price_cents % 100:02d}"
