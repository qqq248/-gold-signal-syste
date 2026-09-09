import pandas as pd
from core import Direction

class Backtester:
    def __init__(self,analyzer,horizon=24): self.analyzer=analyzer; self.horizon=horizon
    def run(self,df,start=300,step=24):
        trades=[]
        for i in range(start,len(df)-self.horizon,step):
            s=self.analyzer.analyze(df.iloc[:i])
            if s.decision==Direction.NO_TRADE: continue
            future=df.iloc[i:i+self.horizon]; buy=s.decision==Direction.BUY
            slhit=(future.low<=s.stop_loss) if buy else (future.high>=s.stop_loss); tphit=(future.high>=s.tp1) if buy else (future.low<=s.tp1)
            first_sl=slhit.idxmax() if slhit.any() else None; first_tp=tphit.idxmax() if tphit.any() else None
            won=first_tp is not None and (first_sl is None or first_tp<first_sl); r=s.risk_reward if won else -1
            mfe=((future.high.max()-s.entry) if buy else (s.entry-future.low.min()))/abs(s.entry-s.stop_loss); mae=((s.entry-future.low.min()) if buy else (future.high.max()-s.entry))/abs(s.entry-s.stop_loss)
            trades.append({"time":df.index[i],"direction":s.decision.value,"confidence":s.confidence,"r":r,"win":won,"mfe":mfe,"mae":mae,"session":"London" if 7<=df.index[i].hour<13 else "New York" if 13<=df.index[i].hour<21 else "Other"})
        t=pd.DataFrame(trades)
        if t.empty: return t,{"total_signals":0}
        equity=t.r.cumsum(); dd=(equity.cummax()-equity).max(); wins=t[t.r>0].r; losses=t[t.r<0].r
        stats={"total_signals":len(t),"win_rate":float(t.win.mean()),"loss_rate":float(1-t.win.mean()),"profit_factor":float(wins.sum()/abs(losses.sum())) if len(losses) else None,"average_r":float(t.r.mean()),"expectancy":float(t.r.mean()),"max_drawdown_r":float(dd),"average_win":float(wins.mean()) if len(wins) else 0,"average_loss":float(losses.mean()) if len(losses) else 0,"longest_losing_streak":_streak(~t.win),"by_direction":t.groupby("direction").r.agg(["count","mean"]).to_dict("index"),"by_session":t.groupby("session").r.agg(["count","mean"]).to_dict("index"),"by_confidence":t.assign(bucket=pd.cut(t.confidence,[0,75,85,100])).groupby("bucket",observed=True).r.agg(["count","mean"]).to_dict("index")}
        return t,stats
    def walk_forward(self,df,train_bars=1000,test_bars=250,thresholds=(70,75,80)):
        """Tune only on each training window, then evaluate the following unseen window."""
        folds=[]
        for end in range(train_bars,len(df)-test_bars+1,test_bars):
            train=df.iloc[end-train_bars:end]; test=df.iloc[max(0,end-300):end+test_bars]
            candidates=[]
            for threshold in thresholds:
                old=self.analyzer.engine.threshold; self.analyzer.engine.threshold=threshold
                _,stats=self.run(train,start=max(220,min(300,len(train)//2)),step=24)
                candidates.append((stats.get("expectancy",-999),threshold))
                self.analyzer.engine.threshold=old
            _,chosen=max(candidates); old=self.analyzer.engine.threshold; self.analyzer.engine.threshold=chosen
            _,out=self.run(test,start=max(220,min(300,len(test)//2)),step=24); self.analyzer.engine.threshold=old
            folds.append({"train_end":str(df.index[end-1]),"threshold":chosen,"out_of_sample":out})
        return folds
def _streak(s):
    best=cur=0
    for v in s: cur=cur+1 if v else 0; best=max(best,cur)
    return best
