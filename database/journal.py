import json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from core import Signal

SCHEMA="""CREATE TABLE IF NOT EXISTS signals(id INTEGER PRIMARY KEY,date TEXT NOT NULL,time TEXT NOT NULL,direction TEXT NOT NULL,entry REAL,sl REAL,tp1 REAL,tp2 REAL,confidence REAL,bot_scores TEXT,market_bias TEXT,reasons TEXT,result TEXT,mfe REAL,mae REAL,official INTEGER NOT NULL DEFAULT 1);"""
class Journal:
    def __init__(self,path): self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True); self.setup()
    def connect(self): return sqlite3.connect(self.path)
    def setup(self):
        with self.connect() as c:
            row=c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='signals'").fetchone()
            if row and "UNIQUE(date,official)" in row[0].replace(" ",""):
                c.execute("ALTER TABLE signals RENAME TO signals_locked")
                c.execute(SCHEMA)
                c.execute("INSERT INTO signals SELECT * FROM signals_locked")
                c.execute("DROP TABLE signals_locked")
            else: c.execute(SCHEMA)
    def official_for(self,date):
        with self.connect() as c:
            row=c.execute("SELECT direction,confidence,reasons,entry,sl,tp1,tp2 FROM signals WHERE date=? AND official=1",(date,)).fetchone()
        return row
    def save(self,s:Signal,now=None):
        now=now or datetime.now(timezone.utc); vals=(now.date().isoformat(),now.isoformat(),s.decision.value,s.entry,s.stop_loss,s.tp1,s.tp2,s.confidence,json.dumps(s.scores),s.market_bias,json.dumps(s.reasons),None,None,None,1 if s.official else 0)
        with self.connect() as c: c.execute("INSERT INTO signals(date,time,direction,entry,sl,tp1,tp2,confidence,bot_scores,market_bias,reasons,result,mfe,mae,official) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    def recent(self,n=20):
        with self.connect() as c: return c.execute("SELECT date,direction,confidence,entry,sl,tp1,tp2,result FROM signals ORDER BY time DESC LIMIT ?",(n,)).fetchall()
