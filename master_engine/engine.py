from core import Signal, Direction

BASE={"Price Action":.20,"Smart Money":.16,"Indicators":.15,"Multi-Timeframe":.22,"Macro":.12,"Quant":.15}

class MasterEngine:
    def __init__(self,threshold=75,min_rr=1.5): self.threshold=threshold; self.min_rr=min_rr
    def decide(self,x,opinions):
        by={o.name:o for o in opinions}; adx=float(x.adx.iloc[-1]); weights=BASE.copy()
        if adx>=25: weights.update({"Price Action":.24,"Multi-Timeframe":.27,"Quant":.17,"Smart Money":.11})
        elif adx<18: weights.update({"Smart Money":.23,"Quant":.22,"Indicators":.18,"Multi-Timeframe":.17,"Price Action":.12})
        total=sum(weights.values()); weights={k:v/total for k,v in weights.items()}
        signed=0
        for name,w in weights.items():
            o=by[name]; s=o.metadata.get("score",0); signed+=w*s*(o.confidence/100)
        bull=max(0,signed)*100; bear=max(0,-signed)*100
        risk=max(by["Volatility"].risk,by["Macro"].risk,by["Multi-Timeframe"].risk)
        quality=min(100,abs(signed)*130+35); confidence=max(0,min(99,quality-risk*.55))
        direction=Direction.BUY if signed>0 else Direction.SELL
        reason=[]
        if by["Multi-Timeframe"].metadata.get("conflict"): reason.append("H1 and H4 are conflicting")
        if not by["Volatility"].metadata.get("suitable"): reason.append("abnormal volatility regime")
        if by["Macro"].metadata.get("news_near"): reason.append("high-impact news is too close")
        if confidence<self.threshold: reason.append(f"confidence {confidence:.1f}% is below {self.threshold:.1f}% threshold")
        r=x.iloc[-1]; atr=float(r.atr); entry=float(r.close); sl=entry-1.2*atr if direction==Direction.BUY else entry+1.2*atr
        tp1=entry+1.8*atr if direction==Direction.BUY else entry-1.8*atr; tp2=entry+2.6*atr if direction==Direction.BUY else entry-2.6*atr
        rr=abs(tp1-entry)/abs(entry-sl)
        if rr + 1e-9 < self.min_rr: reason.append("risk/reward below minimum")
        if reason: direction=Direction.NO_TRADE
        supports=[float(x.low.iloc[-50:].min()),float(x.low.iloc[-20:].min())]; resist=[float(x.high.iloc[-20:].max()),float(x.high.iloc[-50:].max())]
        summaries={o.name:"%s — %.0f%%; %s"%(o.direction.value,o.confidence,"; ".join(o.reasons)) for o in opinions}
        scores={"bullish":bull,"bearish":bear,"risk":risk,"quality":quality,"signed":signed}
        if direction==Direction.NO_TRADE:
            return Signal(direction,confidence,reasons=reason or ["No clear directional edge"],support=supports,resistance=resist,bot_summary=summaries,scores=scores,major_risk="; ".join(reason))
        zone=.12*atr
        return Signal(direction,confidence,"Bullish" if direction==Direction.BUY else "Bearish",entry,entry-zone,entry+zone,sl,tp1,tp2,entry+(3.5*atr if direction==Direction.BUY else -3.5*atr),rr,"M15","H4 / Daily aligned",["Weighted multi-agent confluence",f"ADX regime {adx:.1f}","H1/H4 alignment", "ATR-based levels", "No nearby configured high-impact event"],f"H1 close beyond {sl:.2f}","Data/news completeness and slippage risk",supports,resist,summaries,scores)
