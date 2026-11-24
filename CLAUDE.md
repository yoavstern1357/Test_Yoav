# The Dumpling Boy: project rules for Claude

Animated family YouTube series: a boy in a Vietnamese conical hat and his big, always-hungry uncle follow Dad's dumpling journal along the Silk Road, one dumpling per ~2-minute vertical episode. Read `HANDOFF.md` first for current status and the next step.

## Hard rules
1. **Full anonymity.** The creator's personal name, personal email and personal accounts must never appear in any file, page, video, commit message body, or description. Public identity only: channel **The Dumpling Boy** (`@TheDumplingBoy.studio`), page https://thedumplingboy.netlify.app, Ko-fi https://ko-fi.com/thedumplingboy, business email thedumplingboy.studio@gmail.com. Before committing: `grep -rniE "<personal name>" .` must be empty.
2. **All deliverables in English** (scripts, captions, voice, titles, descriptions). The creator talks to Claude in Hebrew; reply to them in Hebrew.
3. **Never upload to YouTube, send external email, or post publicly** without the creator's explicit approval. The creator only approves results: do the work end to end, then show the result.
4. **Never put secrets in files.** The Netlify token lives in the cloud environment (proxy-injected); use `Authorization: Bearer proxy-injected`.
5. **Kid-safe, respectful, accurate.** Jokes are only on the Uncle, never on a country or people. History uses "Legend says / Many people believe" unless firmly established; every episode lists real sources. Recipes keep grown-up-step badges, doneness temps (71 C / 160 F pork, 74 C / 165 F chicken) and allergy lines.
6. Commit with the attribution lines from the session reminder; push to the branch the session names.

## Where things are
- `production/v2-direction.md`: CURRENT DIRECTION (semi-realistic anime-style look, fast pace, living animation). Read before making any new frames or episode.
- `HANDOFF.md`: status, how to run everything, IDs, gotchas, next step.
- `scripts/`: episode scripts (m:ss timed beats, dialogue, upload text, sources). Ep 1-9 written; `archive/` holds superseded drafts.
- `production/series-format.md`: format (one dumpling per episode, 3-episode country arcs, recipe + recap every 3rd, Dad's journal storyline).
- `production/season-map.md`: 39-episode Silk Road plan (Season 1 sea route, Season 2 land route, finale Venice).
- `production/character-bible.md`: character prompts and Canva reference image IDs.
- `production/growth-plan.md`, `media-kit.md`, `fact-check-report.md`, `first-upload-checklist.md`, `ko-fi-page.md`.
- `tools/episode_maker/`: local video pipeline (see its README).
- `.claude/skills/`: project skills (write-episode-script, make-episode-frames, render-episode, deploy-site).
- Site files (`index.html`, `app.js`, `config.js`, `style.css`, `avatar.svg`, `og-image.png`) deployed to Netlify.

## Style constants
Look: soft children's picture-book 2D cartoon, round shapes, bright pastels. Palette: leaf yellow `#ECC66A`, cream `#FFFAF0`, orange `#D9480F`, peach `#FFE3B8`, brown `#3B2A1A`. Boy: conical leaf hat with orange chin ribbon + white kimono with orange belt. Uncle: bald, thin mustache, white kimono with wide orange belt, catchphrase "For science!". Dad: only a sepia silhouette from behind, never his face. Ending line of every episode: "Dad was right..."
