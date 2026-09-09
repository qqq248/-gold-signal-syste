import sys
import os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

# Streamlit Community Cloud stores private values in st.secrets instead of .env.
# Copy them into the environment before importing Settings so local and cloud
# deployments use the same configuration code.
try:
    for key, value in st.secrets.items():
        os.environ.setdefault(key, str(value))
except FileNotFoundError:
    pass

from config.settings import Settings
from main import provider
from service import Analyzer
# Live FRED macro context; this import also verifies the deployed provider version.\nfrom providers.context import live_market_context
from database.journal import Journal
from formatting import format_signal
st.set_page_config(page_title="Gold Signal System",layout="wide")
st.title("XAUUSD Daily Signal")
cfg=Settings(); journal=Journal(cfg.database_path)
if st.button("ANALYZE GOLD NOW",type="primary"):
    try:
        df=provider(cfg).history(interval=cfg.price_interval); ctx=live_market_context(); s=Analyzer(cfg.confidence_threshold,cfg.min_rr).analyze(df,ctx); journal.save(s); st.metric("Current XAU/USD spot",f"{df.close.iloc[-1]:.2f}"); st.caption(f"Latest candle: {df.index[-1]} UTC · Provider: {cfg.price_provider}"); st.metric("Master confidence",f"{s.confidence:.0f}%"); st.code(format_signal(s)); st.json(s.bot_summary)
    except Exception as e: st.error(f"Analysis unavailable: {e}")
st.subheader("Previous analyses"); st.dataframe(journal.recent())
