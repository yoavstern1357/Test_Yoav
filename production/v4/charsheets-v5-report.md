# Character model sheets v5 (creator approval set): status report

## Status (2026-11-28, later): STAGE 1 DONE (run `charsheets-v5-s1-002`, about 9 min wall on the Kaggle T4), picks made, Stage 2 NOT started
- The retry job finished: 19 images (Boy 6 = 3 full + 3 bust, Uncle 7 = 4 full + 3 bust, Grandma 6 = 3 full + 3 bust; 1 image per concept-seed, 4 steps). Results in branch `gpu-results`, folder `charsheets-v5-s1-002/`. Local copy: `tools/episode_maker/out/charsheets-v5/stage1/` (git-ignored).
- QC (`qc_charsheets.py`, `out/charsheets-v5/qc.md`): all 19 have exactly 1 face and 1 person, no text, Uncle HAT? check clean on all 7 (bald top, no dark/straw crown), Boy 6/6 PASS (indigo 0.07-0.34, straw hat 0.10-0.15, orange sash), Uncle 7/7 PASS (brown jacket, orange sash, charcoal trousers). Grandma: 2 PASS (bust v1, v3), 4 WARN no_jade_jacket / SAGE?: the jacket is a pale sage green, not the deep jade of the plan.
- Eye check (all 19 looked at): the Boy's chin ribbon (two tails) is clearest in `boy_full__v2`; sandals not shoes everywhere. Uncle mustache: thin, long, curled tips in v2 (best), v3, v4; v1 is flatter. Grandma: ONLY `grandma_full__v1` and `grandma_bust__v1` have the two crossed wooden pins; v2 and v3 have pins sticking out like antennae.
- **PICKS** (`production/v4/charsheets-v5-picks.json`, same file in `out/charsheets-v5/picks.json` with absolute paths for the Stage 2 builder): **Boy `boy_full__v2`** (+ bust v2; alt v3), **Uncle `uncle_full__v2`** (+ bust v2; alt v4), **Grandma `grandma_full__v1`** (+ bust v1; alt bust v1 / full v3 for pose).
- Known fixes to carry into Stage 2 prompts: Uncle jacket reads khaki-olive, ask for "earth-brown (#7A5230) linen"; Grandma jacket: "deep jade green (#2F6B4F), not pale sage"; Boy pants are beige, which is fine (rolled hemp).
- Contact sheets (each < 5 MB, `tools/episode_maker/out/charsheets-v5/`): `concept_board.png` (picks large + all 19 small, 1.4 MB), `concept_boy.png`, `concept_uncle.png`, `concept_grandma.png` (0.6-0.8 MB each). Rebuild: `make_charsheets_v5_contact.py concept <images> <out>` and `... board <images> <picks.json> <out>`.
- Stage 2 (turnarounds, 12 expressions, poses, lineups, about 75 images, about 20 T4-min) is READY but NOT pushed: `python3 gpu/make_charsheets_v5_input.py --stage 2 --picks tools/episode_maker/out/charsheets-v5/picks.json`, then a `jobs/run.json` with a new run_id. Awaiting the creator's approval of the three picks and a free GPU slot.

## Ready to run (committed)
- `tools/episode_maker/gpu/make_charsheets_v5_input.py --stage 1` -> `inputs/charsheets-v5-s1/` (19 images, about 9 T4-min estimated; refs: Boy head crops of look-test-3, Uncle body crop of look-test-3 v4 without head, Grandma face-language ref); `--stage 2 --picks picks.json` builds the sheets (per lead: 4 turnaround views, 12 expressions, 2 poses; Uncle x2 variants; 2 lineups of 2 characters), about 75 images, about 20 T4-min estimated.
- `tools/episode_maker/qc_charsheets.py` (faces/persons/text via qc_stills, hat check for the Uncle, costume colour shares) and `tools/episode_maker/make_charsheets_v5_contact.py` (concept boards, per-character and combined sheets, each under 5 MB).
- Re-trigger: edit `tools/episode_maker/gpu/jobs/run.json` (new run_id, same input) and push to `claude/charming-euler-0laws8` once the Kaggle queue works.

## Not done (older note, superseded by the status above)
Stage 1 picks, Stage 2 sheets, scale lineups, contact sheets, `cand_` refs in `specs/refs/`: nothing was generated.
