from providers import context


def test_live_macro_context_bullish_gold(monkeypatch):
    changes = {"DTWEXBGS": -1.0, "DGS10": -10.0}
    monkeypatch.setattr(context, "_fred_change", lambda symbol, percent=True: changes[symbol])
    result = context.live_market_context()
    assert result.macro_bias == "Bullish Gold"
    assert result.macro_confidence == 75
    assert result.source_status == "ok"


def test_fred_change_uses_five_sessions(monkeypatch):
    class Response:
        text = "observation_date,TEST\n" + "\n".join(
            f"2026-01-0{i + 1},{100 + i}" for i in range(7)
        )
        def raise_for_status(self): pass
    monkeypatch.setattr(context.requests, "get", lambda *args, **kwargs: Response())
    assert round(context._fred_change("TEST"), 6) == round((106 / 101 - 1) * 100, 6)


def test_live_macro_context_fails_neutral(monkeypatch):
    def fail(symbol, percent=True):
        raise RuntimeError("offline")
    monkeypatch.setattr(context, "_fred_change", fail)
    result = context.live_market_context()
    assert result.macro_bias == "Neutral"
    assert result.source_status == "unavailable: RuntimeError"
