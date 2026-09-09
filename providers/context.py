from dataclasses import dataclass, field
from datetime import datetime, timezone

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

