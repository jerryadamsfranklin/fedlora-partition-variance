"""Unit tests for scripts/check_typography.py."""

from __future__ import annotations

from pathlib import Path

from scripts.check_typography import (
    abstract_word_count,
    check_abstract_word_count,
    check_latex_em_dash,
)


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


def _abstract_fixture(n_words: int) -> str:
    words = " ".join(f"w{i}" for i in range(n_words))
    return f"\\begin{{abstract}}\n{words}\n\\end{{abstract}}\n"


def test_abstract_word_count_251_fails():
    tex = _abstract_fixture(251)
    assert abstract_word_count(tex) == 251
    hits = check_abstract_word_count(Path("manuscript/main.tex"), tex)
    assert hits and "251" in hits[0]


def test_abstract_word_count_200_passes():
    tex = _abstract_fixture(200)
    assert abstract_word_count(tex) == 200
    assert check_abstract_word_count(Path("manuscript/main.tex"), tex) == []


def test_abstract_word_count_skips_non_main():
    tex = _abstract_fixture(251)
    assert check_abstract_word_count(Path("sections/00_abstract.tex"), tex) == []
