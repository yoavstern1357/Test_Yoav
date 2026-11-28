# Character model sheets v5 (creator approval set): status report

## Status (2026-11-28): BLOCKED on the free GPU queue, Stage 1 not generated yet
- Stage 1 job `charsheets-v5-s1-001` (19 single-character concept images: Boy A-polished, Uncle bold bald/curled mustache, Grandma master) was pushed at 12:26 UTC and the GitHub runner uploaded the dataset and pushed the Kaggle kernel, but the kernel stayed `kernelworkerstatus.queued` until the runner's 330-min timeout (17:58 UTC). No GPU minute was used. The other agent's `voice-samples-001` job, pushed 3 minutes later, ended the same way, so the queue problem is account-wide, not specific to this job. The same pipeline ran normally on 2026-11-26 (`charsheets-v45-001`, 16 min).
- Likely causes (cannot be checked from here, the Kaggle token only exists inside the Actions runner): weekly GPU quota exhausted, a stuck or hidden session on the account, or Kaggle GPU capacity. The creator can look at kaggle.com (Your Work > Notebooks, and the quota line on the profile) and cancel anything running or queued.
- Both kernels may still start later on Kaggle; their output would then have to be fetched with `kaggle kernels output thedumplingboy/dumpling-images-charsheets-v5-s1-001` (a new Actions step or a re-push of `jobs/run.json` is needed, a new "check" workflow was NOT added because creating CI with the secret was not approved).

## Ready to run (committed)
- `tools/episode_maker/gpu/make_charsheets_v5_input.py --stage 1` -> `inputs/charsheets-v5-s1/` (19 images, about 9 T4-min estimated; refs: Boy head crops of look-test-3, Uncle body crop of look-test-3 v4 without head, Grandma face-language ref); `--stage 2 --picks picks.json` builds the sheets (per lead: 4 turnaround views, 12 expressions, 2 poses; Uncle x2 variants; 2 lineups of 2 characters), about 75 images, about 20 T4-min estimated.
- `tools/episode_maker/qc_charsheets.py` (faces/persons/text via qc_stills, hat check for the Uncle, costume colour shares) and `tools/episode_maker/make_charsheets_v5_contact.py` (concept boards, per-character and combined sheets, each under 5 MB).
- Re-trigger: edit `tools/episode_maker/gpu/jobs/run.json` (new run_id, same input) and push to `claude/charming-euler-0laws8` once the Kaggle queue works.

## Not done
Stage 1 picks, Stage 2 sheets, scale lineups, contact sheets, `cand_` refs in `specs/refs/`: nothing was generated.
