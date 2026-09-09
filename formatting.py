from core import Direction
def f(v): return "N/A" if v is None else f"{v:.2f}"
def format_signal(s):
    if s.decision==Direction.NO_TRADE:
        return "\n".join(["XAUUSD DAILY SIGNAL","","Decision:","NO TRADE","",f"Confidence:\n{s.confidence:.0f}%","","Reason:","; ".join(s.reasons),"","Conditions Required Before Entry:","Confidence threshold, H1/H4 alignment, normal volatility, acceptable news window","","Key Levels To Watch:",f"Support: {', '.join(map(f,s.support))}\nResistance: {', '.join(map(f,s.resistance))}"])
    reasons="\n".join(f"{i}. {v}" for i,v in enumerate(s.reasons,1)); bots="\n".join(f"{k}:\n{v}" for k,v in s.bot_summary.items())
    return f"""XAUUSD DAILY SIGNAL

Decision:
{s.decision.value}

Entry:
{f(s.entry)}

Entry Zone:
{f(s.entry_low)} - {f(s.entry_high)}

Stop Loss:
{f(s.stop_loss)}

Take Profit 1:
{f(s.tp1)}

Take Profit 2:
{f(s.tp2)}

Optional Extended Target:
{f(s.extended_target)}

Risk / Reward:
1:{s.risk_reward:.2f}

Confidence:
{s.confidence:.0f}%

Market Bias:
{s.market_bias}

Best Execution Timeframe:
{s.execution_timeframe}

Higher Timeframe Bias:
{s.higher_timeframe_bias}

Reasons:
{reasons}

Invalidation:
{s.invalidation}

Major Risk:
{s.major_risk}

Important Levels:
Resistance: {', '.join(map(f,s.resistance))}
Support: {', '.join(map(f,s.support))}

BOT SUMMARY

{bots}

Master Decision:
{s.decision.value} at {s.confidence:.0f}% confidence"""

