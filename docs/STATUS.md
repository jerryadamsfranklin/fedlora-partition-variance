# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase M on phase-m, paused after step 3 (assembly + V9 + verifier). Awaiting review before anonymization / typography / overlap.

## Done

- phase-l fast-forwarded into main (8031a74); Phase M continues on phase-m
- Abstract finalized (3B interaction share; Dolly category partition; IEEEkeywords)
- manuscript/main.tex assembled in SAI IEEEtran template (from thesai.org ZipFileHandler); Sections 1-6; Figs 1-3; Tabs 1-3; refs.bib
- Conclusion drafted (~120 words) from existing claims only
- V9 CLAIMS populated (25 entries: analysis-checked + external-verified); verify_varpart.py exits 0

## Next

1. Review page count / V9 / verifier report
2. Phase M step 4: anonymize review copy
3. Step 5: typography + overlap check (OLD=federated-lora-experiments)
4. Step 6: re-verify every reference against primary sources
5. Jerry: AI disclosure version (b); attorney on IJACSA; destroy M3; revoke tokens
6. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Framing rules for the manuscript

- Condition the flip claim on effect size (paired SD 0.00282 tl, 0.00473 l3; near-tie needs 206 and 46 paired draws; separable pairs need 3)
- No partition main effect claim at 3B; the 3B story is the interaction (0.764)
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- MixedLM cross-check partial; moment estimates primary
- Position against FFA-LoRA's across-run SDs
- Cross-scale comparisons are confounded (instruction-tuned versus base; float32 versus float16)
- Where the interaction dominates, pairing on partitions buys little
- No prevalence claims about the literature

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Cite arXiv:2609.13512 in third person where measured-payload byte accounting is used
- Phase K literature audit dropped; no audit-derived counts
- Release statement covers results and metadata, not adapter weights
- Do not pay the IJACSA APC until the attorney confirms the venue counts

## Open items

- AI disclosure: version (b) (drafting support)
- Attorney: whether IJACSA counts before APC
- M3 still up; destroy and revoke tokens
- Anonymization, typography, overlap (Phase M steps 4-5)
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
