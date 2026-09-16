"""Held-out formatter must match FederatedClient Dolly/context training format."""

from __future__ import annotations

from scripts.evaluate_instruction_holdout import format_instruction_texts


def test_dolly_context_formatter_matches_client_strings():
    # Hard-coded expected strings copied character-for-character from
    # src/federation/client.py tokenize() (instruction/context/response branch).
    examples = {
        "instruction": ["Write a summary.", "Say hello."],
        "context": ["Long article text.", ""],
        "response": ["A short summary.", "Hello!"],
    }
    expected = [
        (
            "### Instruction:\nWrite a summary.\n\n"
            "### Context:\nLong article text.\n\n"
            "### Response:\nA short summary."
        ),
        "### Instruction:\nSay hello.\n\n### Response:\nHello!",
    ]
    assert format_instruction_texts(examples) == expected


def test_instruction_response_without_context_column_unchanged():
    examples = {
        "instruction": ["Q?"],
        "response": ["A."],
    }
    assert format_instruction_texts(examples) == [
        "### Instruction:\nQ?\n\n### Response:\nA."
    ]
