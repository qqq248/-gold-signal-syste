import sqlite3
from indicators import enrich
from service import Analyzer
from database.journal import Journal
from core import Signal,Direction
from formatting import format_signal
from backtesting.engine import Backtester
from providers.price import normalize,TwelveDataPriceProvider

def test_indicators(prices):
    x=enrich(prices); assert {"ema20","rsi","macd","atr","adx","stoch"}.issubset(x.columns); assert x.atr.dropna().gt(0).all()
def test_provider_normalizes(prices):
    x=prices.reset_index().rename(columns={"index":"datetime","open":"Open"}); assert len(normalize(x))==len(prices)
def test_bots_and_master(prices):
    s=Analyzer().analyze(prices); assert s.decision in Direction; assert 0<=s.confidence<=100; assert len(s.bot_summary)==7
def test_format(prices):
    assert "XAUUSD DAILY SIGNAL" in format_signal(Analyzer().analyze(prices))
def test_repeated_analysis_same_day(tmp_path):
    j=Journal(tmp_path/"x.db"); s=Signal(Direction.NO_TRADE,50,reasons=["test"]); j.save(s); j.save(s); assert len(j.recent())==2
def test_db_fields(tmp_path):
    j=Journal(tmp_path/"x.db"); cols={r[1] for r in sqlite3.connect(j.path).execute("pragma table_info(signals)")}; assert {"mfe","mae","bot_scores","result"}.issubset(cols)
def test_backtest(prices):
    trades,stats=Backtester(Analyzer(threshold=0)).run(prices,start=300,step=50); assert "total_signals" in stats
def test_walk_forward(prices):
    folds=Backtester(Analyzer()).walk_forward(prices,train_bars=300,test_bars=100,thresholds=(70,75)); assert len(folds)==2; assert "out_of_sample" in folds[0]
def test_twelve_data_provider(monkeypatch):
    import pandas as pd
    class R:
        def raise_for_status(self): pass
        def json(self): return {"values":[{"datetime":pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S"),"open":"3500","high":"3502","low":"3499","close":"3501"}]}
    monkeypatch.setattr("providers.price.requests.get",lambda *a,**k:R())
    df=TwelveDataPriceProvider("key").history(); assert df.close.iloc[0]==3501
def test_journal_migrates_daily_lock(tmp_path):
    import sqlite3
    path=tmp_path/"old.db"; c=sqlite3.connect(path); c.execute("CREATE TABLE signals(id INTEGER PRIMARY KEY,date TEXT NOT NULL,time TEXT NOT NULL,direction TEXT NOT NULL,entry REAL,sl REAL,tp1 REAL,tp2 REAL,confidence REAL,bot_scores TEXT,market_bias TEXT,reasons TEXT,result TEXT,mfe REAL,mae REAL,official INTEGER NOT NULL DEFAULT 1,UNIQUE(date,official))"); c.commit(); c.close()
    j=Journal(path); s=Signal(Direction.NO_TRADE,50); j.save(s); j.save(s); assert len(j.recent())==2
