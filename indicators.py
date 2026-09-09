import numpy as np
import pandas as pd

def enrich(df: pd.DataFrame) -> pd.DataFrame:
    x=df.copy(); c=x.close
    x["ema20"]=c.ewm(span=20,adjust=False).mean(); x["ema50"]=c.ewm(span=50,adjust=False).mean()
    x["sma200"]=c.rolling(200).mean()
    delta=c.diff(); gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False).mean()
    x["rsi"]=100-(100/(1+gain/loss.replace(0,np.nan)))
    e12=c.ewm(span=12,adjust=False).mean(); e26=c.ewm(span=26,adjust=False).mean(); x["macd"]=e12-e26; x["macd_signal"]=x.macd.ewm(span=9,adjust=False).mean()
    prev=c.shift(); tr=pd.concat([(x.high-x.low),(x.high-prev).abs(),(x.low-prev).abs()],axis=1).max(axis=1)
    x["atr"]=tr.ewm(alpha=1/14,adjust=False).mean()
    up=x.high.diff(); down=-x.low.diff(); plus=up.where((up>down)&(up>0),0); minus=down.where((down>up)&(down>0),0)
    x["adx"]=((100*(plus.ewm(alpha=1/14,adjust=False).mean()-minus.ewm(alpha=1/14,adjust=False).mean()).abs()/tr.ewm(alpha=1/14,adjust=False).mean()).ewm(alpha=1/14,adjust=False).mean()).clip(0,100)
    mid=c.rolling(20).mean(); sd=c.rolling(20).std(); x["bb_upper"]=mid+2*sd; x["bb_lower"]=mid-2*sd
    ll=x.low.rolling(14).min(); hh=x.high.rolling(14).max(); x["stoch"]=100*(c-ll)/(hh-ll)
    if "volume" in x and x.volume.fillna(0).sum()>0: x["vwap"]=(c*x.volume).cumsum()/x.volume.cumsum()
    else: x["vwap"]=np.nan
    return x

