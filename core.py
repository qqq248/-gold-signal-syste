from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any

class Direction(str, Enum):
    BUY="BUY"; SELL="SELL"; NO_TRADE="NO TRADE"

@dataclass
class BotOpinion:
    name: str
    direction: Direction
    confidence: float
    reasons: list[str] = field(default_factory=list)
    risk: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class Signal:
    decision: Direction
    confidence: float
    market_bias: str="Neutral"
    entry: float|None=None
    entry_low: float|None=None
    entry_high: float|None=None
    stop_loss: float|None=None
    tp1: float|None=None
    tp2: float|None=None
    extended_target: float|None=None
    risk_reward: float|None=None
    execution_timeframe: str="M15"
    higher_timeframe_bias: str="H4 / Daily Neutral"
    reasons: list[str]=field(default_factory=list)
    invalidation: str=""
    major_risk: str=""
    support: list[float]=field(default_factory=list)
    resistance: list[float]=field(default_factory=list)
    bot_summary: dict[str, str]=field(default_factory=dict)
    scores: dict[str, float]=field(default_factory=dict)
    official: bool=True
    def as_dict(self):
        d=asdict(self); d["decision"]=self.decision.value; return d

