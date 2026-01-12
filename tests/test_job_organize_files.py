from __future__ import annotations

from pathlib import Path

from autoops.jobs.organize_files import OrganizeFilesConfig, organize_files


def _touch(path: Path, content: str = "x") -> None:
    path.write_text(content, encoding="utf-8")


def test_organize_files_moves_by_extension(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _touch(src / "a.pdf")
    _touch(src / "b.jpg")
    _touch(src / "c.mp4")
    _touch(src / "d.unknown")

    cfg = OrganizeFilesConfig(
        source_dir=src,
        destination_dir=src,
        dry_run=False,
        categories={
            "pdf": [".pdf"],
            "images": [".jpg", ".png"],
            "videos": [".mp4"],
        },
        others_dir="others",
    )

    result = organize_files(cfg)

    assert result["moved_total"] == 4
    assert result["moved_by_category"]["pdf"] == 1
    assert result["moved_by_category"]["images"] == 1
    assert result["moved_by_category"]["videos"] == 1
    assert result["moved_by_category"]["others"] == 1

    assert (src / "pdf" / "a.pdf").exists()
    assert (src / "images" / "b.jpg").exists()
    assert (src / "videos" / "c.mp4").exists()
    assert (src / "others" / "d.unknown").exists()


def test_organize_files_dry_run_does_not_move(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _touch(src / "a.pdf")

    cfg = OrganizeFilesConfig(
        source_dir=src,
        destination_dir=src,
        dry_run=True,
        categories={"pdf": [".pdf"]},
        others_dir="others",
    )

    result = organize_files(cfg)

    assert result["moved_total"] == 1
    assert (src / "a.pdf").exists()
    assert not (src / "pdf").exists()


def test_organize_files_handles_name_collision(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    # same filename coming from source
    _touch(src / "a.pdf", "one")

    # create destination folder and a file with same name already there
    (src / "pdf").mkdir()
    _touch(src / "pdf" / "a.pdf", "existing")

    cfg = OrganizeFilesConfig(
        source_dir=src,
        destination_dir=src,
        dry_run=False,
        categories={"pdf": [".pdf"]},
        others_dir="others",
    )

    result = organize_files(cfg)

    assert result["moved_total"] == 1
    assert (src / "pdf" / "a.pdf").exists()
    # collision should create a new file
    assert (src / "pdf" / "a_1.pdf").exists()
    assert (src / "a.pdf").exists() is False
