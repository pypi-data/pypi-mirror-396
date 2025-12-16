"""bd-wubi Python SDK，为多语言项目提供五笔数据查询能力。"""

from __future__ import annotations

from typing import Optional, Sequence

from .dictionary import WubiDictionary, WubiDictionaryOptions
from .dataset import WubiEntry

__all__ = [
    "initialize",
    "is_initialized",
    "get_by_text",
    "get_by_code",
    "get_all_entries",
    "guess_code",
    "WubiEntry",
    "WubiDictionaryOptions",
]


def initialize(options: Optional[WubiDictionaryOptions] = None) -> None:
    """初始化全局词典。"""
    WubiDictionary.initialize(options)


def is_initialized() -> bool:
    return WubiDictionary.is_initialized()


def _ensure_initialized() -> WubiDictionary:
    if not WubiDictionary.is_initialized():
        WubiDictionary.initialize()
    return WubiDictionary.instance()


def get_by_text(text: str) -> Sequence[WubiEntry]:
    return _ensure_initialized().get_by_text(text)


def get_by_code(code: str) -> Sequence[WubiEntry]:
    return _ensure_initialized().get_by_code(code)


def get_all_entries() -> Sequence[WubiEntry]:
    return _ensure_initialized().get_all_entries()


def guess_code(text: str) -> str:
    return _ensure_initialized().guess_code(text)
