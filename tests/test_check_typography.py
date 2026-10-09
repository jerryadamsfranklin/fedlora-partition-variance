"""Unit tests for scripts/check_typography.py."""

from __future__ import annotations

from pathlib import Path

from scripts.check_typography import (
    REQUIRED_ACKNOWLEDGMENT,
    abstract_word_count,
    check_abstract_word_count,
    check_acknowledgment,
    check_float_citations,
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


def test_float_citation_flags_unreferenced_label(tmp_path: Path):
    orphan = tmp_path / "orphan.tex"
    orphan.write_text(
        r"\label{fig:orphan}" + "\n" + r"See Figure~\ref{fig:heldout}." + "\n",
        encoding="utf-8",
    )
    hits = check_float_citations([orphan])
    assert any("fig:orphan" in h for h in hits)


def test_acknowledgment_requires_verbatim_paragraph():
    good = (
        r"\section*{Acknowledgment}" + "\n" + REQUIRED_ACKNOWLEDGMENT + "\n"
    )
    assert check_acknowledgment(Path("manuscript/main.tex"), good) == []
    bad = r"\section*{Acknowledgment}" + "\nOld AI wording.\n"
    assert check_acknowledgment(Path("manuscript/main.tex"), bad)


def test_acknowledgment_skips_non_main():
    assert (
        check_acknowledgment(Path("sections/01_introduction.tex"), "no ack") == []
    )
