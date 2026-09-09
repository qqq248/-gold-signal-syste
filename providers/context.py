from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from io import StringIO
import math

import pandas as pd
import requests

@dataclass
class MarketContext:
    macro_bias: str="Neutral"
    macro_confidence: float=0
    high_impact_events: list[dict]=field(default_factory=list)
    dxy_change: float|None=None
    yield_change: float|None=None
    spread: float|None=None
    source_status: str="not_configured"

    def news_within(self, minutes=90, now=None):
        now=now or datetime.now(timezone.utc)
        for event in self.high_impact_events:
            try:
                t=datetime.fromisoformat(event["time"].replace("Z","+00:00"))
                if abs((t-now).total_seconds()) <= minutes*60 and event.get("impact","").lower()=="high": return True
            except (KeyError,ValueError,TypeError): pass
        return False


def _fred_change(series: str, percent: bool = True) -> float:
    """Return a five-observation change from the Federal Reserve's FRED CSV."""
    start_date = (datetime.now(timezone.utc) - timedelta(days=30)).date().isoformat()
    response = requests.get(
        "https://fred.stlouisfed.org/graph/fredgraph.csv",
        params={"id": series, "cosd": start_date},
        timeout=15,
    )
    response.raise_for_status()
    values = pd.read_csv(StringIO(response.text))[series]
    values = pd.to_numeric(values, errors="coerce").dropna()
    if len(values) < 2:
        raise ValueError(f"No usable FRED data for {series}")
    start = float(values.iloc[-6] if len(values) >= 6 else values.iloc[0])
    end = float(values.iloc[-1])
    if not math.isfinite(start) or not math.isfinite(end) or start == 0:
        raise ValueError(f"Invalid FRED data for {series}")
    return (end / start - 1) * 100 if percent else (end - start) * 100


def live_market_context() -> MarketContext:
    """Build a conservative gold macro bias from DXY and the US 10Y yield.

    A falling dollar/yield supports gold and a rising dollar/yield pressures it.
    Mixed or very small moves remain neutral. Failures are exposed explicitly.
    """
    try:
        dxy_change = _fred_change("DTWEXBGS")
        yield_change = _fred_change("DGS10", percent=False)
        dxy_signal = -1 if dxy_change > 0.15 else 1 if dxy_change < -0.15 else 0
        yield_signal = -1 if yield_change > 5 else 1 if yield_change < -5 else 0
        score = (dxy_signal + yield_signal) / 2
        if score >= 0.5:
            bias = "Bullish Gold"
        elif score <= -0.5:
            bias = "Bearish Gold"
        else:
            bias = "Neutral"
        confidence = 35 if score == 0 else 60 if abs(score) == 0.5 else 75
        return MarketContext(
            macro_bias=bias,
            macro_confidence=confidence,
            dxy_change=dxy_change,
            yield_change=yield_change,
            source_status="ok",
        )
    except Exception as exc:
        return MarketContext(source_status=f"unavailable: {type(exc).__name__}")
