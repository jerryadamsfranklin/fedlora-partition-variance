"""Unit tests for scripts/analysis/make_tables.py presentation helpers."""

from __future__ import annotations

from scripts.analysis.make_tables import (
    fmt_int_range,
    fmt_range,
    round_half_up,
    sci_tex,
)


def test_round_half_up_992_25():
    assert round_half_up(992.25, 1) == "992.3"


def test_sci_tex_zero():
    assert sci_tex(0.0) == "0"


def test_sci_tex_scientific():
    assert sci_tex(4.0937e-6) == r"$4.09{\times}10^{-6}$"


def test_fmt_range_collapsed():
    assert fmt_range(2578.125, 2578.125, 1) == "2578.1"


def test_fmt_int_range_span():
    assert fmt_int_range(9, 10) == "9--10"
