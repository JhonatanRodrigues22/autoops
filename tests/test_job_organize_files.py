from __future__ import annotations

from pathlib import Path

from autoops.jobs.organize_files import organize_files


def _touch(path: Path, content: str = "x") -> None:
    path.write_text(content, encoding="utf-8")


def test_organize_files_moves_by_extension(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _touch(src / "a.pdf")
    _touch(src / "b.jpg")
    _touch(src / "c.mp4")
    _touch(src / "d.unknown")

    result = organize_files(
        source_dir=src,
        destination_dir=src,
        dry_run=False,
        preview=False,
        categories={
            "pdf": [".pdf"],
            "images": [".jpg", ".png"],
            "videos": [".mp4"],
        },
        others_dir="others",
    )

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

    result = organize_files(
        source_dir=src,
        destination_dir=src,
        dry_run=True,
        preview=False,
        categories={"pdf": [".pdf"]},
        others_dir="others",
    )

    assert result["moved_total"] == 1
    assert (src / "a.pdf").exists()
    assert not (src / "pdf").exists()


def test_organize_files_preview_lists_moves_but_does_not_move(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _touch(src / "a.pdf")

    result = organize_files(
        source_dir=src,
        destination_dir=src,
        dry_run=False,
        preview=True,
        categories={"pdf": [".pdf"]},
        others_dir="others",
    )

    assert result["moved_total"] == 1
    assert result["preview"] is True
    assert len(result["preview_moves"]) == 1
    assert (src / "a.pdf").exists()
    assert not (src / "pdf").exists()


def test_organize_files_handles_name_collision(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()

    _touch(src / "a.pdf", "one")

    (src / "pdf").mkdir()
    _touch(src / "pdf" / "a.pdf", "existing")

    result = organize_files(
        source_dir=src,
        destination_dir=src,
        dry_run=False,
        preview=False,
        categories={"pdf": [".pdf"]},
        others_dir="others",
    )

    assert result["moved_total"] == 1
    assert (src / "pdf" / "a.pdf").exists()
    assert (src / "pdf" / "a_1.pdf").exists()
    assert not (src / "a.pdf").exists()
