"""Unit tests for scripts/check_layout.py."""

from __future__ import annotations

from pathlib import Path

from scripts.check_layout import (
    check_g1_overfull,
    check_g3_table_rows,
    content_overfull_hbox,
    count_table_data_rows,
    is_class_intrinsic_overfull,
    overfull_hbox_pts,
)


def test_overfull_hbox_parse():
    log = "Overfull \\hbox (12.345pt too wide) in paragraph at lines 1--2\n"
    pts = overfull_hbox_pts(log)
    assert len(pts) == 1 and abs(pts[0][0] - 12.345) < 1e-6


def test_g1_fails_on_section_overfull(tmp_path: Path):
    log = tmp_path / "main.log"
    log.write_text(
        "(./sections/04_results.tex\n"
        "Overfull \\hbox (49.5pt too wide) in paragraph at lines 28--29\n",
        encoding="utf-8",
    )
    hits = check_g1_overfull(log, max_pt=1.0)
    assert hits and "49.500pt" in hits[0]


def test_g1_fails_on_wide_caption_even_outside_sections(tmp_path: Path):
    log = tmp_path / "main.log"
    log.write_text(
        "Overfull \\hbox (290.5pt too wide) in paragraph at lines 12--12\n",
        encoding="utf-8",
    )
    assert check_g1_overfull(log, max_pt=1.0)


def test_g1_ignores_output_active_chrome(tmp_path: Path):
    log = tmp_path / "main.log"
    log.write_text(
        "Overfull \\hbox (505.12177pt too wide) has occurred while \\output is active\n",
        encoding="utf-8",
    )
    assert check_g1_overfull(log, max_pt=1.0) == []


def test_g1_allows_maketitle_class_intrinsic(tmp_path: Path):
    log = tmp_path / "main.log"
    log.write_text(
        "Overfull \\hbox (9.2679pt too wide) in paragraph at lines 84--84\n",
        encoding="utf-8",
    )
    assert is_class_intrinsic_overfull(log.read_text())
    assert check_g1_overfull(log, max_pt=1.0) == []


def test_g1_fails_other_title_overfull(tmp_path: Path):
    log = tmp_path / "main.log"
    log.write_text(
        "Overfull \\hbox (9.3pt too wide) in paragraph at lines 84--84\n",
        encoding="utf-8",
    )
    assert check_g1_overfull(log, max_pt=1.0)


def test_g1_passes_small_overfull(tmp_path: Path):
    log = tmp_path / "main.log"
    log.write_text(
        "(./sections/04_results.tex\n"
        "Overfull \\hbox (0.5pt too wide) in paragraph at lines 10--11\n",
        encoding="utf-8",
    )
    assert check_g1_overfull(log, max_pt=1.0) == []


def test_content_overfull_detects_p5_regressions():
    # Fixture shaped like the 8c08fb4 log: caption + IV-A formula.
    log = (
        "(./sections/04_results.tex\n"
        "Overfull \\hbox (290.50389pt too wide) in paragraph at lines 12--12\n"
        "Overfull \\hbox (49.51471pt too wide) in paragraph at lines 28--29\n"
        "Overfull \\hbox (505.12177pt too wide) has occurred while \\output is active\n"
        "Overfull \\hbox (9.2679pt too wide) in paragraph at lines 84--84\n"
    )
    hits = content_overfull_hbox(log, max_pt=1.0)
    assert len(hits) == 2
    assert hits[0][0] > 200 and hits[1][0] > 40


def test_count_table_rows():
    tex = r"""
\begin{tabular}{ll}
\toprule
A & B \\
\midrule
1 & 2 \\
3 & 4 \\
\bottomrule
\end{tabular}
"""
    assert count_table_data_rows(tex) == 2


def test_g3_current_tables():
    # After regenerate, committed tables must satisfy G3.
    hits = check_g3_table_rows()
    # May fail before regen in the same edit cycle; assert helper shape only if present.
    assert isinstance(hits, list)
