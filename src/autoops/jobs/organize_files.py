from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Tuple


def _dedupe_target_path(target_path: Path) -> Path:
    """
    If target_path exists, create a non-colliding variant like:
    file.ext -> file_1.ext -> file_2.ext ...
    """
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    i = 1
    while True:
        candidate = parent / f"{stem}_{i}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def organize_files(
    source_dir: Path,
    destination_dir: Path,
    categories: Dict[str, List[str]],
    others_dir: str,
    dry_run: bool = True,
    preview: bool = False,
) -> Dict:
    moved_by_category: Dict[str, int] = {}
    preview_moves: List[Tuple[str, str]] = []

    for category in categories:
        moved_by_category[category] = 0
    moved_by_category[others_dir] = 0

    source_dir = source_dir.resolve()
    destination_dir = destination_dir.resolve()

    for item in source_dir.iterdir():
        if not item.is_file():
            continue

        ext = item.suffix.lower()
        target_category = None

        for category, extensions in categories.items():
            if ext in extensions:
                target_category = category
                break

        if target_category is None:
            target_category = others_dir

        target_dir = destination_dir / target_category
        target_path = target_dir / item.name

        # preview list uses relative paths to be readable
        preview_moves.append(
            (
                str(item.relative_to(source_dir)),
                str(target_path.relative_to(destination_dir)),
            )
        )

        # dry-run / preview: count but do not touch filesystem
        if preview or dry_run:
            moved_by_category[target_category] += 1
            continue

        target_dir.mkdir(parents=True, exist_ok=True)

        # Avoid collisions safely
        final_target = _dedupe_target_path(target_path)

        shutil.move(str(item), str(final_target))
        moved_by_category[target_category] += 1

    return {
        "moved_total": sum(moved_by_category.values()),
        "moved_by_category": moved_by_category,
        "dry_run": dry_run,
        "preview": preview,
        "source_dir": str(source_dir),
        "destination_dir": str(destination_dir),
        "preview_moves": preview_moves if preview else [],
    }
