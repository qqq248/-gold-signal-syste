from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from config.settings import Settings
from providers.price import CSVPriceProvider,YahooPriceProvider,TwelveDataPriceProvider
from providers.context import live_market_context
from service import Analyzer
from database.journal import Journal
from formatting import format_signal
from core import Signal,Direction
from notifications.telegram import send

def provider(cfg):
    kind=cfg.price_provider.lower()
    if kind=="csv": return CSVPriceProvider(cfg.csv_path)
    if kind=="twelvedata": return TwelveDataPriceProvider(cfg.twelve_data_api_key,cfg.symbol,cfg.price_output_size)
    if kind=="yahoo": return YahooPriceProvider(cfg.symbol)
    raise ValueError(f"Unknown PRICE_PROVIDER: {cfg.price_provider}")
def run(official=True):
    cfg=Settings(); journal=Journal(cfg.database_path)
    try: signal=Analyzer(cfg.confidence_threshold,cfg.min_rr).analyze(provider(cfg).history(interval=cfg.price_interval),live_market_context())
    except Exception as e: signal=Signal(Direction.NO_TRADE,0,reasons=[f"Verified market data unavailable: {type(e).__name__}: {e}"],major_risk="No live data; no price was invented")
    signal.official=official
    if official: journal.save(signal)
    text=format_signal(signal); print(text)
    if official: send(text,cfg.telegram_token,cfg.telegram_chat_id)
if __name__=="__main__": run()
