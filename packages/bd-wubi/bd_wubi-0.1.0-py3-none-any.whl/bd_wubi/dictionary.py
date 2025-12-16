from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .cache import LruCache
from .dataset import WubiDataset, WubiEntry


@dataclass
class WubiDictionaryOptions:
    cache_capacity: int = 512
    enable_guess_cache: bool = True
    dataset_path: Optional[str] = None


class WubiDictionary:
    _instance: Optional["WubiDictionary"] = None
    _lock = RLock()

    def __init__(self, dataset: WubiDataset, options: WubiDictionaryOptions) -> None:
        self._entries = dataset.entries
        capacity = max(1, options.cache_capacity)
        self._forward_index = self._build_index(dataset.entries, lambda entry: entry.text)
        self._reverse_index = self._build_index(dataset.entries, lambda entry: entry.code)
        self._forward_cache = LruCache[str, Sequence[WubiEntry]](capacity)
        self._reverse_cache = LruCache[str, Sequence[WubiEntry]](capacity)
        self._guess_cache = (
            LruCache[str, str](capacity) if options.enable_guess_cache else None
        )

    @classmethod
    def initialize(cls, options: Optional[WubiDictionaryOptions] = None) -> "WubiDictionary":
        with cls._lock:
            if cls._instance is not None:
                raise RuntimeError("WubiDictionary 已初始化，禁止重复执行。")

            opts = options or WubiDictionaryOptions()
            dataset = WubiDataset.load(opts.dataset_path)
            cls._instance = cls(dataset, opts)
            return cls._instance

    @classmethod
    def instance(cls) -> "WubiDictionary":
        if cls._instance is None:
            raise RuntimeError("尚未调用 bd_wubi.initialize()。")
        return cls._instance

    @classmethod
    def is_initialized(cls) -> bool:
        return cls._instance is not None

    @classmethod
    def _reset_for_test(cls) -> None:  # pragma: no cover - 仅测试使用
        with cls._lock:
            cls._instance = None

    def get_by_text(self, text: str) -> Sequence[WubiEntry]:
        if text is None:
            raise ValueError("text 不能为空")

        key = text.strip()
        if not key:
            return ()

        return self._forward_cache.get_or_add(
            key, lambda: self._forward_index.get(key, ())
        )

    def get_by_code(self, code: str) -> Sequence[WubiEntry]:
        if code is None:
            raise ValueError("code 不能为空")

        key = code.strip()
        if not key:
            return ()

        return self._reverse_cache.get_or_add(
            key, lambda: self._reverse_index.get(key, ())
        )

    def get_all_entries(self) -> Sequence[WubiEntry]:
        return self._entries

    def guess_code(self, text: str) -> str:
        if text is None:
            raise ValueError("text 不能为空")

        normalized = text.strip()
        if not normalized:
            return ""

        if self._guess_cache is None:
            return self._guess_code_internal(normalized)

        return self._guess_cache.get_or_add(
            normalized, lambda: self._guess_code_internal(normalized)
        )

    def _guess_code_internal(self, text: str) -> str:
        elements = _split_text(text)
        if not elements:
            return ""

        indices = _select_guess_indices(len(elements))
        if not indices:
            return ""

        codes: List[str] = []
        for index in indices:
            codes.append(self._primary_code_or_empty(elements[index]))

        return _compose_guess_code(codes, len(elements))

    @staticmethod
    def _build_index(
        entries: Iterable[WubiEntry], key_selector
    ) -> Dict[str, Tuple[WubiEntry, ...]]:
        buckets: Dict[str, List[WubiEntry]] = {}
        for entry in entries:
            key = key_selector(entry)
            if not key:
                continue

            bucket = buckets.setdefault(key, [])
            bucket.append(entry)

        return {key: tuple(bucket) for key, bucket in buckets.items()}

    def _primary_code_or_empty(self, text: str) -> str:
        entries = self._forward_index.get(text)
        if not entries:
            return ""

        # 词典 JSON 为单个文本包含多个候选，末尾通常为全码，猜码时优先选择该候选。
        return entries[-1].code


def _split_text(text: str) -> List[str]:
    return [char for char in text if char.strip()]


def _select_guess_indices(element_count: int) -> List[int]:
    if element_count <= 0:
        return []
    if element_count == 1:
        return [0]
    if element_count == 2:
        return [0, 1]
    if element_count == 3:
        return [0, 1, 2]
    return [0, 1, 2, element_count - 1]


def _compose_guess_code(codes: Sequence[str], element_count: int) -> str:
    if not codes:
        return ""

    if element_count == 1:
        return codes[0]

    if element_count == 2:
        return _concat(_take_prefix(codes[0], 2), _take_prefix(codes[1], 2))

    if element_count == 3:
        return _concat(
            _take_prefix(codes[0], 1),
            _take_prefix(codes[1], 1),
            _take_prefix(codes[2], 2),
        )

    return _concat(
        _take_prefix(codes[0], 1),
        _take_prefix(codes[1], 1),
        _take_prefix(codes[2], 1),
        _take_prefix(codes[-1], 1),
    )


def _take_prefix(code: str, length: int) -> str:
    if not code or length <= 0:
        return ""
    return code if len(code) <= length else code[:length]


def _concat(*parts: str) -> str:
    return "".join(part for part in parts if part)
