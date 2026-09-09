from pathlib import Path

def test_dashboard_loads_dotenv_before_settings():
    text=(Path(__file__).resolve().parents[1]/"dashboard"/"app.py").read_text()
    assert text.index("load_dotenv()") < text.index("from config.settings import Settings")

def test_dashboard_loads_streamlit_secrets_before_settings():
    text=(Path(__file__).resolve().parents[1]/"dashboard"/"app.py").read_text()
    assert text.index("st.secrets.items()") < text.index("from config.settings import Settings")
