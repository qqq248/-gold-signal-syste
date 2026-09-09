import numpy as np
import pandas as pd
from core import BotOpinion, Direction
from providers.context import MarketContext

def d(score, dead=0.15): return Direction.BUY if score>dead else Direction.SELL if score<-dead else Direction.NO_TRADE
def conf(score): return min(95., max(20., 50+abs(score)*35))

class PriceActionBot:
    name="Price Action"
    def analyze(self,x):
        r=x.iloc[-1]; recent=x.iloc[-21:-1]; score=(1 if r.close>recent.high.max() else -1 if r.close<recent.low.min() else 0)
        score += .45 if r.close>r.open and (r.close-r.open)>.5*(r.high-r.low) else -.45 if r.close<r.open and (r.open-r.close)>.5*(r.high-r.low) else 0
        trend=(x.close.iloc[-1]-x.close.iloc[-10])/max(r.atr,1e-9); score+=np.clip(trend/5,-.7,.7)
        return BotOpinion(self.name,d(score),conf(score),["20-bar structure/breakout", "candle rejection and momentum"],metadata={"score":float(score)})

class SmartMoneyBot:
    name="Smart Money"
    def analyze(self,x):
        r=x.iloc[-1]; w=x.iloc[-25:-1]; sweep_low=r.low<w.low.min() and r.close>w.low.min(); sweep_high=r.high>w.high.max() and r.close<w.high.max()
        score=1 if sweep_low else -1 if sweep_high else np.clip((r.close-(w.low.min()+w.high.max())/2)/(w.high.max()-w.low.min()+1e-9),-.5,.5)
        return BotOpinion(self.name,d(score,.25),conf(score),["liquidity sweep", "premium/discount location"],metadata={"score":float(score)})

class IndicatorBot:
    name="Indicators"
    def analyze(self,x):
        r=x.iloc[-1]; votes=[1 if r.ema20>r.ema50 else -1,1 if r.macd>r.macd_signal else -1,1 if 50<r.rsi<72 else -1 if 28<r.rsi<50 else 0,1 if r.close>r.sma200 else -1]
        score=sum(votes)/len(votes)
        return BotOpinion(self.name,d(score,.2),conf(score),["EMA trend", "MACD/RSI/SMA confluence"],metadata={"score":score})

class MultiTimeframeBot:
    name="Multi-Timeframe"
    def analyze(self,x):
        h1=1 if x.ema20.iloc[-1]>x.ema50.iloc[-1] else -1
        h4=x.resample("4h").agg({"open":"first","high":"max","low":"min","close":"last"}).dropna()
        h4trend=1 if len(h4)>15 and h4.close.iloc[-1]>h4.close.rolling(12).mean().iloc[-1] else -1
        score=(h1+h4trend)/2; conflict=h1!=h4trend
        return BotOpinion(self.name,d(score,.2),35 if conflict else 85,["H1 and H4 alignment" if not conflict else "H1/H4 conflict"],risk=35 if conflict else 5,metadata={"score":score,"conflict":conflict})

class MacroBot:
    name="Macro"
    def analyze(self,x,ctx:MarketContext):
        score={"Bullish Gold":1,"Bearish Gold":-1}.get(ctx.macro_bias,0)
        risk=75 if ctx.news_within() else 15 if ctx.source_status!="ok" else 5
        details=[f"macro bias: {ctx.macro_bias}",f"source: {ctx.source_status}"]
        if ctx.dxy_change is not None: details.append(f"DXY 5-session change: {ctx.dxy_change:+.2f}%")
        if ctx.yield_change is not None: details.append(f"US10Y 5-session change: {ctx.yield_change:+.1f} bp")
        return BotOpinion(self.name,d(score,.2),ctx.macro_confidence if score else 35,details,risk=risk,metadata={"score":score,"news_near":ctx.news_within()})

class VolatilityBot:
    name="Volatility"
    def analyze(self,x,ctx):
        ratio=x.atr.iloc[-1]/x.atr.rolling(100).median().iloc[-1]; suitable=.55<=ratio<=2.2
        risk=min(100,abs(np.log(max(ratio,1e-9)))*55)+(50 if ctx.news_within() else 0)
        return BotOpinion(self.name,Direction.NO_TRADE,75 if suitable else 25,[f"ATR regime {ratio:.2f}x median"],min(100,risk),{"atr_ratio":float(ratio),"suitable":suitable,"score":0})

class QuantBot:
    name="Quant"
    def analyze(self,x):
        ret=x.close.pct_change(); mom=x.close.pct_change(12).iloc[-1]; vol=ret.rolling(50).std().iloc[-1]; z=mom/(vol*np.sqrt(12)+1e-9); score=float(np.clip(z/2,-1,1))
        return BotOpinion(self.name,d(score,.2),conf(score),["12-bar normalized momentum", "volatility regime"],metadata={"score":score})
