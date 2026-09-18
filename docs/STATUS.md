# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase L drafting on phase-l. Setup, Results, and Related Work reviewed with citation fixes applied. Discussion drafted; Introduction and Abstract next.

## Done

- Phases B to E on main; freeze-v1 at 0812fcf; freeze-v2 at 4f9fcf8
- Phase F gates passed; Phase G complete (tl 75/75, l3 45/45); Phase H verifier exits 0
- Phase I complete with pair-level flip and observed-gap power addendum; Phase J figures 505 pt with 8 pt fonts
- Setup and Results drafted, verified, revised
- Related Work revised: QQP not QNLI; FFA SD>gap positioning; NIID-Bench; FLoRA 1-3 rounds / 1444 MMLU / 10 clients; Hsu alpha-degradation; To our knowledge; bib corrections; source comments
- Discussion drafted (~500 words): reporting recommendations, pairing limits, cross-scale, limitations, no method recommendation

## Citation verification (18 Sep 2026)

- Picard: 89.01% to 90.83% over 10,000 seeds = 1.82 pp; ImageNet about 0.5%. arXiv:2109.08203
- Hsu et al.: Dirichlet alpha degradation (30.1% to 76.9% figure verified but not used in prose). arXiv:1909.06335 (preprint only)
- LEAF: arXiv:1812.01097, 2018 (preprint)
- Bouthillier et al.: MLSys vol 3, pages 747 to 769
- NIID-Bench: Li, Diao, Chen, He, ICDE 2022, pages 965 to 978, DOI 10.1109/ICDE53745.2022.00077
- FLoRA: NeurIPS 2024, vol 37, pages 22513 to 22533; Alpaca MMLU 29.85 vs 29.41; "marginal" and "at least 0.2"; 1 to 3 rounds, no seed replication; MMLU on 1,444 samples; 10 clients
- FFA-LoRA: ICLR 2024; MNLI-m 85.05 +/- 1.1 vs 82.03 +/- 10.7; QQP 84.35 +/- 0.6 vs 83.51 +/- 3.3; 20 runs; 3-client fixed proportions; no Dolly
- FedIT Dolly "synthetic shard" claim: cut (unverified)

## Next

1. Draft Introduction and Abstract
2. Phase M: SAI template, anonymization, V9 claims list, overlap check, typography
3. Destroy M3 after syncing what adapters exist; revoke the GitHub and HF tokens
4. Jerry: JCR impact factor; attorney questions; AI disclosure version choice
5. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Framing rules for the manuscript

- Condition the flip claim on effect size (paired SD 0.00282 tl, 0.00473 l3; near-tie needs 206 and 46 paired draws; separable pairs need 3)
- No partition main effect claim at 3B; the 3B story is the interaction (0.764)
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- MixedLM cross-check is partial; moment estimates primary
- Position the contribution against FFA-LoRA's across-run SDs: prior work reports run variance; this paper decomposes it into partition and training-seed components

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Two scales on RTX 4090, --workers 1; l3 holdout float16, tl float32
- freeze-v2 for the eval-only change; --max-retries 5 because of host instability
- Phase K literature audit dropped; motivate from cited published practice; no audit-derived counts
- Release statement covers results and metadata, not adapter weights
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Open items

- JCR impact factor; attorney questions (IJACSA weight, IEEE Early Access)
- AI disclosure: drafting support applies
- M3 still up; destroy and revoke tokens
- Overlap check (Phase M): OLD is the local folder federated-lora-experiments
- V9 claims list unfilled until manuscript numbers are final
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
