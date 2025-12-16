from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import IO, Iterable, List, Optional


@dataclass(frozen=True)
class WubiEntry:
    text: str
    code: str
    weight: Optional[int]
    stem: Optional[str]


class WubiDataset:
    """负责从 JSON 文件加载 bd-wubi 数据集。"""

    def __init__(self, entries: Iterable[WubiEntry]) -> None:
        self.entries = tuple(entries)

    @classmethod
    def load(cls, dataset_path: Optional[str] = None) -> "WubiDataset":
        with _open_dataset_stream(dataset_path) as stream:
            payload = json.load(stream)

        rows = payload.get("entries") or []
        entries: List[WubiEntry] = []
        for row in rows:
            text = row.get("Text") or row.get("text")
            code = row.get("Code") or row.get("code")
            if not text or not code:
                continue

            weight = row.get("Weight") or row.get("weight")
            stem = row.get("Stem") or row.get("stem")
            entries.append(WubiEntry(text=text, code=code, weight=weight, stem=stem))

        return cls(entries)


def _open_dataset_stream(dataset_path: Optional[str]) -> IO[str]:
    candidates = list(
        filter(
            None,
            [
                dataset_path,
                os.getenv("BD_WUBI_JSON"),
                _env_root_candidate(os.getenv("BD_WUBI_ROOT")),
                _env_root_candidate(os.getenv("BDWUBI_ROOT")),
            ],
        )
    )

    for candidate in candidates:
        path = Path(candidate).expanduser()
        if path.is_file():
            return path.open("r", encoding="utf-8")

    try:
        resource = resources.files("bd_wubi.data").joinpath("bd-wubi.json")
        return resource.open("r", encoding="utf-8")
    except FileNotFoundError as exc:  # pragma: no cover - 理论上不会触发
        raise FileNotFoundError("未找到内嵌数据集资源 bd-wubi.json") from exc


def _env_root_candidate(root: Optional[str]) -> Optional[str]:
    if not root:
        return None
    root_path = Path(root).expanduser()
    json_path = root_path / "data" / "json" / "bd-wubi.json"
    if json_path.is_file():
        return str(json_path)
    return None
