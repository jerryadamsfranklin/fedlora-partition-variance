# STATUS

Last updated: 18 Sep 2026

Replace this file in the Claude Project whenever the state changes. Keep only one copy.

## Current phase

Phase M on phase-m, paused after step 5. Seven review fixes applied; review copy anonymized; typography and overlap clean. Step 6 (final reference verification) next.

## Done

- Phases B to L on main; Phase M assembly (7 pages, V9, verifier exit 0)
- Seven review fixes: prevalence claims scoped; FedIT ten-shard detail; byte-accounting cite without author name; Conclusion opening; Fig 1/2/3 fixes
- Step 4 anonymization: Anonymous Author; empty pdfauthor/pdftitle; code availability release-upon-acceptance; Generative AI declaration version (b); figure PDFs clean of home paths
- Step 5: typography OK; overlap max 0.082% shared 8-grams vs OJ-CS body/supplemental

## Next

1. Step 6 final reference verification against primary sources
2. Destroy M3; revoke the GitHub and HF tokens
3. Jerry: attorney answer on IJACSA weight before paying the APC; real email for the submission form; JCR impact factor figure
4. Mon 21 Sep go/no-go; target submission Tue 22 Sep

## Blocking before submission

- Attorney confirmation that IJACSA counts, before the GBP 800 APC
- Real author email on the submission form and camera-ready

## Framing rules for the manuscript

- Condition the flip claim on effect size (paired SD 0.00282 tl, 0.00473 l3; near-tie needs 206 and 46 paired draws; separable pairs need 3)
- No partition main effect claim at 3B; the 3B story is the interaction (0.764)
- IID floor at 3B descriptive only (2 df per method)
- The l3 flip rise from k = 1 to k = 3 is a small-sample artifact
- RQ4 exploratory, uncorrected, not replicated at 3B
- Communication as measured, within method; no efficiency ranking
- No method recommendation
- MixedLM cross-check partial; moment estimates primary
- Cross-scale comparisons confounded (instruction-tuned versus base; float32 versus float16 base weights)
- Where the interaction dominates, pairing on partitions buys little
- No prevalence claims about the literature: cite specific papers, never "usually", "rarely", or "most papers"

## Decisions made

- Venue: IJACSA October cycle, target submission Tue 22 Sep; November fallback if go/no-go fails 21 Sep
- Generative AI declaration version (b)
- Byte accounting cites arXiv:2609.13512 in the third person without naming the author in prose
- Phase K literature audit dropped; no audit-derived counts
- Release statement covers results and metadata, not adapter weights

## Open items

- JCR impact factor; attorney questions (IJACSA weight, IEEE Early Access)
- M3 still up; destroy and revoke tokens
- Local tooling: use .venv/bin/python

## Run progress

| Grid | Complete | Failed | Total |
|---|---|---|---|
| tl | 75 | 0 | 75 |
| l3 | 45 | 0 | 45 |
