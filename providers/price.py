from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd
import requests

REQUIRED={"open","high","low","close"}

def normalize(frame: pd.DataFrame) -> pd.DataFrame:
    df=frame.copy()
    df.columns=[str(c).lower().replace(" ","_") for c in df.columns]
    if "datetime" in df.columns: df=df.set_index("datetime")
    if "date" in df.columns: df=df.set_index("date")
    if not REQUIRED.issubset(df.columns): raise ValueError(f"Missing OHLC columns: {REQUIRED-set(df.columns)}")
    df.index=pd.to_datetime(df.index, utc=True)
    for c in REQUIRED|{"volume"}: 
        if c in df: df[c]=pd.to_numeric(df[c], errors="coerce")
    return df.sort_index().dropna(subset=list(REQUIRED))

class PriceProvider(ABC):
    @abstractmethod
    def history(self, interval="1h", period="2y") -> pd.DataFrame: ...

class CSVPriceProvider(PriceProvider):
    def __init__(self,path): self.path=Path(path)
    def history(self, interval="1h", period="2y"):
        if not self.path.exists(): raise FileNotFoundError(self.path)
        return normalize(pd.read_csv(self.path))

class YahooPriceProvider(PriceProvider):
    def __init__(self,symbol="GC=F"): self.symbol=symbol
    def history(self, interval="1h", period="2y"):
        try: import yfinance as yf
        except ImportError as e: raise RuntimeError("Install yfinance") from e
        df=yf.download(self.symbol, period=period, interval=interval, auto_adjust=False, progress=False)
        if df.empty: raise RuntimeError("Provider returned no market data")
        if isinstance(df.columns,pd.MultiIndex): df.columns=df.columns.get_level_values(0)
        return normalize(df)

class TwelveDataPriceProvider(PriceProvider):
    """Direct spot XAU/USD candles from Twelve Data (API key required)."""
    endpoint="https://api.twelvedata.com/time_series"
    def __init__(self,api_key,symbol="XAU/USD",output_size=5000):
        if not api_key: raise ValueError("TWELVE_DATA_API_KEY is required for direct XAU/USD prices")
        self.api_key=api_key; self.symbol=symbol; self.output_size=output_size
    def history(self,interval="15min",period=None):
        response=requests.get(self.endpoint,params={"symbol":self.symbol,"interval":interval,"outputsize":self.output_size,"timezone":"UTC","apikey":self.api_key},timeout=20)
        response.raise_for_status(); payload=response.json()
        if payload.get("status")=="error": raise RuntimeError(payload.get("message","Twelve Data error"))
        values=payload.get("values")
        if not values: raise RuntimeError("Twelve Data returned no XAU/USD candles")
        frame=normalize(pd.DataFrame(values))
        age=(pd.Timestamp.now(tz="UTC")-frame.index[-1]).total_seconds()/60
        limits={"1min":5,"5min":15,"15min":45,"30min":90,"1h":180}
        if age>limits.get(interval,180): raise RuntimeError(f"Latest XAU/USD candle is stale ({age:.0f} minutes old)")
        return frame
