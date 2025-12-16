import pytest

import bd_wubi
from bd_wubi.dictionary import WubiDictionary


def setup_module(module):
    if not bd_wubi.is_initialized():
        bd_wubi.initialize()


def test_lookup_by_text_returns_entries():
    result = bd_wubi.get_by_text("工")
    assert result
    assert any(entry.code == "a" for entry in result)


def test_lookup_by_code_returns_entries():
    result = bd_wubi.get_by_code("a")
    assert result
    assert any(entry.text == "工" for entry in result)


def test_lookup_reuses_cached_reference():
    first = bd_wubi.get_by_text("工")
    second = bd_wubi.get_by_text("工")
    assert first is second


def test_guess_code_two_characters_matches_rule():
    expected = _compose_expected("信息")
    assert bd_wubi.guess_code("信息") == expected


def test_guess_code_three_characters_matches_rule():
    expected = _compose_expected("发展中")
    assert bd_wubi.guess_code("发展中") == expected


def test_guess_code_five_characters_matches_rule():
    text = "中华人民共和国"
    expected = _compose_expected(text)
    assert bd_wubi.guess_code(text) == expected


def test_initialize_only_once():
    with pytest.raises(RuntimeError):
        bd_wubi.initialize()


def _compose_expected(text: str) -> str:
    chars = [char for char in text]
    entries = bd_wubi.get_all_entries()
    lookup = {entry.text: entry.code for entry in entries if entry.text in chars}
    codes = [lookup[char] for char in chars]

    if len(codes) == 1:
        return codes[0]
    if len(codes) == 2:
        return codes[0][:2] + codes[1][:2]
    if len(codes) == 3:
        return codes[0][:1] + codes[1][:1] + codes[2][:2]
    return codes[0][:1] + codes[1][:1] + codes[2][:1] + codes[-1][:1]
