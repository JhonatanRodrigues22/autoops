from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass(frozen=True)
class OrganizeFilesLoadedConfig:
    source_dir: Path
    destination_dir: Path
    dry_run: bool
    categories: Dict[str, list[str]]
    others_dir: str = "others"


def _project_root(from_path: Path) -> Path:
    """
    Find project root by walking up until we find pyproject.toml.
    Falls back to the config file parent if not found.
    """
    cur = from_path.resolve().parent
    for _ in range(10):
        if (cur / "pyproject.toml").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return from_path.resolve().parent


def _expand_placeholders(raw: str, project_root: Path) -> str:
    home = Path.home().resolve()
    return (
        raw.replace("${PROJECT_ROOT}", str(project_root))
        .replace("${HOME}", str(home))
    )


def _as_path(value: Any, project_root: Path) -> Path:
    if value is None:
        raise ValueError("Path value is required")

    s = str(value)
    s = _expand_placeholders(s, project_root)

    p = Path(s)
    if not p.is_absolute():
        p = (project_root / p).resolve()
    return p


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        raise ValueError("Config root must be a mapping (YAML dict)")
    return data


def load_organize_files_config(
    config_path: Path,
    *,
    source_dir: Optional[Path] = None,
    destination_dir: Optional[Path] = None,
    dry_run: Optional[bool] = None,
) -> OrganizeFilesLoadedConfig:
    """
    Load organize_files config from YAML, applying CLI overrides (when provided).
    Precedence: CLI > YAML > defaults.

    Path resolution rules:
    - Supports ${PROJECT_ROOT} and ${HOME} placeholders in YAML strings.
    - Relative paths are resolved relative to PROJECT_ROOT (where pyproject.toml is).

    destination_dir behavior:
    - If destination_dir is not provided (CLI/YAML), defaults to source_dir.
    """
    config_path = config_path.resolve()
    project_root = _project_root(config_path)

    data = load_yaml(config_path)
    section = data.get("organize_files", {}) or {}
    if not isinstance(section, dict):
        raise ValueError("organize_files section must be a mapping")

    # Defaults (YAML)
    yaml_source = section.get("source_dir", "${HOME}/Downloads")
    yaml_dest = section.get("destination_dir", None)  # optional on purpose
    yaml_dry = section.get("dry_run", True)
    yaml_others = section.get("others_dir", "others")
    yaml_categories = section.get("categories", {})

    if not isinstance(yaml_categories, dict):
        raise ValueError("organize_files.categories must be a mapping")

    # Apply overrides / resolve final paths
    final_source = _as_path(source_dir if source_dir is not None else yaml_source, project_root)

    if destination_dir is not None:
        final_dest = _as_path(destination_dir, project_root)
    elif yaml_dest is not None:
        final_dest = _as_path(yaml_dest, project_root)
    else:
        final_dest = final_source  # <<< key behavior: same folder

    final_dry = bool(dry_run if dry_run is not None else yaml_dry)

    # Normalize category extensions to list[str]
    categories: Dict[str, list[str]] = {}
    for cat, exts in yaml_categories.items():
        if isinstance(exts, str):
            exts = [exts]
        if not isinstance(exts, list):
            raise ValueError(f"Category '{cat}' extensions must be a list")
        categories[str(cat)] = [str(e) for e in exts]

    return OrganizeFilesLoadedConfig(
        source_dir=final_source,
        destination_dir=final_dest,
        dry_run=final_dry,
        categories=categories,
        others_dir=str(yaml_others),
    )
