from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class OrganizeFilesConfig:
    source_dir: Path
    destination_dir: Path
    dry_run: bool
    categories: Dict[str, List[str]]  # category -> extensions (with dot)
    others_dir: str = "others"


def _normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    if not ext:
        return ext
    return ext if ext.startswith(".") else f".{ext}"


def _build_extension_map(categories: Dict[str, List[str]]) -> Dict[str, str]:
    """
    Returns a map: extension -> category
    """
    ext_to_cat: Dict[str, str] = {}
    for cat, exts in categories.items():
        for ext in exts:
            ext_to_cat[_normalize_ext(ext)] = cat
    return ext_to_cat


def _safe_destination_path(dest_dir: Path, filename: str) -> Path:
    """
    If file exists, add _1, _2, ... before extension.
    """
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    i = 1
    while True:
        new_name = f"{stem}_{i}{suffix}"
        candidate2 = dest_dir / new_name
        if not candidate2.exists():
            return candidate2
        i += 1


def organize_files(cfg: OrganizeFilesConfig) -> Dict:
    src = cfg.source_dir
    dst_root = cfg.destination_dir

    ext_to_cat = _build_extension_map(cfg.categories)

    moved_by_category: Dict[str, int] = {cat: 0 for cat in cfg.categories.keys()}
    moved_by_category["others"] = 0

    planned_moves = []

    for item in src.iterdir():
        if item.is_dir():
            continue

        ext = item.suffix.lower()
        category = ext_to_cat.get(ext, "others")

        target_dir_name = category if category != "others" else cfg.others_dir
        target_dir = dst_root / target_dir_name

        target_path = _safe_destination_path(target_dir, item.name)

        planned_moves.append((item, target_dir, target_path, category))

    # execute moves
    for src_file, target_dir, target_path, category in planned_moves:
        if not cfg.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            src_file.replace(target_path)

        moved_by_category[category] += 1

    moved_total = sum(moved_by_category.values())

    return {
        "moved_total": moved_total,
        "moved_by_category": moved_by_category,
        "dry_run": cfg.dry_run,
        "source_dir": str(cfg.source_dir),
        "destination_dir": str(cfg.destination_dir),
    }
