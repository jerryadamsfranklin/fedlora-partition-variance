# Public repo scan findings (19 Sep 2026)

Do **not** rewrite history without Jerry's OK. Findings below are HEAD + sampled history.

## Tokens / credentials
- HEAD: **none** found (hf_/ghp_/github_pat_/sk-/AKIA/private keys)
- History (sampled): **none** found

## SSH host:port / IPs (FINDING — redaction candidate)
Committed in docs (not live credentials, but operational endpoints):
- `docs/phase_f_report.md`, `docs/phase_g_report.md`: destroyed Phase F/G hosts (`116.127…`, `115.75…`, `1.193…`, wrong-IP note)
- `analysis/n8_machine_gates.txt`: live M2 `<REDACTED-HOST>`

Recommend: redact IPs in those docs in a normal forward commit (not history rewrite). Destroyed hosts are low risk; live M2 endpoint should not stay in a public file.

## Absolute paths with local username (FINDING — minor)
- At least one analysis CSV row embeds `/Users/jerryadamsfranklin/Documents/Git Repos/...` (smoke holdout path). Cosmetic; no secret.

## OJ-CS / fedlora-protocols (FINDING — meta only, not manuscript body)
References exist in plan/DECISIONS/PROVENANCE/`overlap_check.py` as **overlap-boundary instructions** (read old repo in place; do not copy). No OJ-CS body/supplement text appears to have been imported. Still worth a human skim of those files before submission.

## Zenodo
- Repo is PUBLIC; release `v0.9.0-n8-prep` exists
- Still need Jerry to enable Zenodo GitHub integration, then cut `v0.9.1` for the concept DOI
