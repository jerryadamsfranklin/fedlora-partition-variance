"""Tests for optimizer-step / discarded-sample formulas (Phase C addendum)."""

from __future__ import annotations

from src.data.partition_stats import discarded_trailing_samples, optimizer_steps_for_n


def test_optimizer_steps_tinyllama_4x4():
    kwargs = {"batch_size": 4, "grad_accum": 4, "local_epochs": 1}
    assert optimizer_steps_for_n(12, **kwargs) == 0
    assert optimizer_steps_for_n(13, **kwargs) == 1
    assert optimizer_steps_for_n(16, **kwargs) == 1
    assert optimizer_steps_for_n(32, **kwargs) == 2


def test_optimizer_steps_llama_2x8():
    kwargs = {"batch_size": 2, "grad_accum": 8, "local_epochs": 1}
    assert optimizer_steps_for_n(14, **kwargs) == 0
    assert optimizer_steps_for_n(15, **kwargs) == 1


def test_discarded_trailing_samples_examples():
    # 4x4: n=12 -> 3 batches, 0 complete accum blocks -> all discarded
    assert discarded_trailing_samples(12, batch_size=4, grad_accum=4) == 12
    # 4x4: n=13 -> 4 batches, 1 complete block uses all 13
    assert discarded_trailing_samples(13, batch_size=4, grad_accum=4) == 0
    # 4x4: n=17 -> 5 batches, 1 block uses first 4 batches (16 samples), 1 discarded
    assert discarded_trailing_samples(17, batch_size=4, grad_accum=4) == 1
    # 2x8: n=14 -> 7 batches, 0 steps -> all discarded
    assert discarded_trailing_samples(14, batch_size=2, grad_accum=8) == 14
    # 2x8: n=15 -> 8 batches, 1 block uses all 15
    assert discarded_trailing_samples(15, batch_size=2, grad_accum=8) == 0
