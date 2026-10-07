"""Unit tests for scripts/check_typography.py LaTeX --- rule."""

from __future__ import annotations

from pathlib import Path

from scripts.check_typography import check_latex_em_dash


def test_latex_em_dash_flags_triple_hyphen():
    path = Path("fixture.tex")
    assert check_latex_em_dash(path, "a---b", 1) == [
        "fixture.tex:1: LaTeX em dash (---)"
    ]


def test_latex_em_dash_allows_en_dash_and_hyphen():
    path = Path("fixture.tex")
    assert check_latex_em_dash(path, "a--b", 1) == []
    assert check_latex_em_dash(path, "a-b", 1) == []


def test_latex_em_dash_skips_comment_lines():
    path = Path("fixture.tex")
    assert check_latex_em_dash(path, "% a---b", 1) == []
    assert check_latex_em_dash(path, "  % a---b", 1) == []


def test_latex_em_dash_skips_non_tex():
    path = Path("fixture.bib")
    assert check_latex_em_dash(path, "a---b", 1) == []
