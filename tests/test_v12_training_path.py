"""Unit tests for V12 freeze-v1..freeze-v3.1 training-path check."""

from __future__ import annotations

from scripts import verify_varpart as vv


def _patch_tags(monkeypatch, *, has_v3: bool = True, has_v31: bool = True) -> None:
    def fake_exists(tag: str) -> bool:
        if tag == "freeze-v3":
            return has_v3
        if tag == "freeze-v3.1":
            return has_v31
        return False

    monkeypatch.setattr(vv, "_git_tag_exists", fake_exists)


def _empty_except_eval_hotfix(a: str, b: str, *paths: str) -> str:
    """All training diffs empty; freeze-v3..v3.1 eval path changed (hotfix)."""
    if (
        a == "freeze-v3"
        and b == "freeze-v3.1"
        and paths == ("scripts/evaluate_instruction_holdout.py",)
    ):
        return "scripts/evaluate_instruction_holdout.py"
    return ""


def test_v12_fails_when_v1_v31_train_diff_nonempty(monkeypatch):
    _patch_tags(monkeypatch)

    def fake_diff(a: str, b: str, *paths: str) -> str:
        if a == "freeze-v1" and b == "freeze-v3.1" and "src" in paths:
            return "src/federation/client.py"
        return _empty_except_eval_hotfix(a, b, *paths)

    monkeypatch.setattr(vv, "_git_diff_name_only", fake_diff)
    result = vv.v12()
    assert not result.ok
    assert any("freeze-v1..freeze-v3.1" in msg for msg in result.failures)


def test_v12_passes_when_v1_v31_train_diff_empty(monkeypatch):
    _patch_tags(monkeypatch)
    monkeypatch.setattr(vv, "_git_diff_name_only", _empty_except_eval_hotfix)
    result = vv.v12()
    assert result.ok
    assert any(
        "training path unchanged freeze-v1..freeze-v3.1" in n for n in result.notes
    )
