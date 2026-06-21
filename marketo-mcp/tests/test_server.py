from __future__ import annotations

from marketo_mcp.server import _clean_params


def test_clean_params_drops_blank_values() -> None:
    assert _clean_params({"a": 1, "b": None, "c": "", "d": "ok"}) == {"a": 1, "d": "ok"}


def test_clean_params_keeps_falsey_non_blank_values() -> None:
    assert _clean_params({"a": 0, "b": False, "c": []}) == {"a": 0, "b": False, "c": []}
