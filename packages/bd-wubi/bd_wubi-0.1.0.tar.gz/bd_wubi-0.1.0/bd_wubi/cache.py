from __future__ import annotations

from collections import OrderedDict
from threading import RLock
from typing import Callable, Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class LruCache(Generic[K, V]):
    """线程安全的 LRU 缓存，用于重复查询的快速返回。"""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self._capacity = capacity
        self._store: "OrderedDict[K, V]" = OrderedDict()
        self._lock = RLock()

    def get_or_add(self, key: K, factory: Callable[[], V]) -> V:
        value = self._try_get(key)
        if value is not None:
            return value

        created = factory()
        with self._lock:
            existing = self._store.get(key)
            if existing is not None:
                self._store.move_to_end(key)
                return existing

            self._store[key] = created
            if len(self._store) > self._capacity:
                self._store.popitem(last=False)

        return created

    def _try_get(self, key: K) -> Optional[V]:
        with self._lock:
            value = self._store.get(key)
            if value is not None:
                self._store.move_to_end(key)
            return value
