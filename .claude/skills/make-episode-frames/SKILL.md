---
name: make-episode-frames
description: Generate the ~35 picture frames for an episode in Canva and download them at full 1080x1920 resolution into tools/episode_maker/specs/frames/. Use before rendering a new episode.
---

# Make episode frames (Canva -> PNG files)

Read `HANDOFF.md` section 4 for IDs and gotchas. Summary:
1. From the script, plan ~35 shots (a new frame every 3-4 s): wides, mediums, close-ups, inserts, fun-fact backgrounds. Name each frame (snake_case).
2. `generate-image` (Canva MCP) per frame. Always start the prompt with the character-reference sentence and pass reference IDs: Boy `MAHbzwNGxJo`, Uncle `MAHbzx4PTVI`, Grandma `MAHb0FNIPP4`. Style: soft children's picture-book 2D, very round shapes, bright pastels, vertical 9:16, "No text."
3. Reliability: send 3-4 at a time. The Boy alone often fails: use Boy + Uncle together, or a frame without faces (hands, objects, places). Retry failures; if still failing, use an existing frame with a different camera focus. Copy job IDs exactly when polling `get-generate-image-job`. Record each frame's media ID (`MAHb...`).
4. Put frames on pages: open design `DAHb0JF2jpw` with `read-design` (`open_transaction`), `add_page` 1080x1920 titled by frame name, read page IDs, then one `edit-design` call with many `insert_fill` (full bleed 1080x1920), then `finalize: commit`.
5. `export-design` png, pages [...], width 1080, height 1920, `export_quality: pro`; download each URL with curl to `tools/episode_maker/specs/frames/epNN/<name>.png` (host `export-download.canva.com` is already allowed).
6. Add the frame name -> media ID table to the episode script file. Do not wait with `sleep` in the foreground (blocked): use `run_in_background` or Monitor.
