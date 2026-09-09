from datetime import datetime, timezone
from indicators import enrich
from bots.agents import PriceActionBot,SmartMoneyBot,IndicatorBot,MultiTimeframeBot,MacroBot,VolatilityBot,QuantBot
from providers.context import MarketContext
from master_engine.engine import MasterEngine

class Analyzer:
    def __init__(self,threshold=75,min_rr=1.5): self.engine=MasterEngine(threshold,min_rr)
    def analyze(self,df,ctx=None):
        if len(df)<220: raise ValueError("At least 220 OHLC bars are required")
        x=enrich(df).dropna(subset=["atr","ema50","sma200","rsi","adx"])
        ctx=ctx or MarketContext()
        ops=[PriceActionBot().analyze(x),SmartMoneyBot().analyze(x),IndicatorBot().analyze(x),MultiTimeframeBot().analyze(x),MacroBot().analyze(x,ctx),VolatilityBot().analyze(x,ctx),QuantBot().analyze(x)]
        return self.engine.decide(x,ops)

