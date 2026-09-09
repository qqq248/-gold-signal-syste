from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    price_provider: str = os.getenv("PRICE_PROVIDER", "twelvedata")
    symbol: str = os.getenv("XAU_SYMBOL", "XAU/USD")
    twelve_data_api_key: str = os.getenv("TWELVE_DATA_API_KEY", "")
    price_interval: str = os.getenv("PRICE_INTERVAL", "15min")
    price_output_size: int = int(os.getenv("PRICE_OUTPUT_SIZE", "5000"))
    allow_proxy_fallback: bool = os.getenv("ALLOW_PROXY_FALLBACK", "false").lower() == "true"
    csv_path: str = os.getenv("CSV_DATA_PATH", "")
    database_path: str = os.getenv("DATABASE_PATH", "data/signals.db")
    confidence_threshold: float = float(os.getenv("CONFIDENCE_THRESHOLD", "75"))
    min_rr: float = float(os.getenv("MIN_RR", "1.5"))
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")
