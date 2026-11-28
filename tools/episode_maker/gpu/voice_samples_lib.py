"""Shared definitions of the voice-sample set (same 4 lines for every model/voice, so the creator can compare by ear).

Used by make_voice_samples_input.py (GPU input), run_cpu_samples.py (CPU engines) and build_compilations.py.
Audio ids look like  <model>__<character>__<n>  where n is the candidate number inside that model and character.
"""
CHARS = ["boy", "uncle", "grandma", "narrator", "host"]
CHAR_NAMES = {"boy": "The Boy", "uncle": "The Uncle", "grandma": "Grandma", "narrator": "The Scroll Narrator",
              "host": "Boy voice-over host"}

# 4 lines per character: [id, text, delivery style key (see generate_tts.STYLES), note]
LINES = {
    "boy": [
        ("l1", "Wait, the soup is inside the dumpling? How?", "neutral", "curious"),
        ("l2", "Uncle, no! That is MY dumpling!", "excited", "comic outburst"),
        ("l3", "I think Dad stood right here, a long time ago.", "tender", "soft, emotional"),
        ("l4", "Hello! I am the Dumpling Boy, and today we taste a legend.", "host", "bright intro"),
    ],
    "uncle": [
        ("l1", "For dumpling research!", "laugh", "comic outburst"),
        ("l2", "There was soup inside.", "tiny", "stunned, quiet"),
        ("l3", "I smell... destiny. And a little bit of ginger.", "dreamy", "dreamy"),
        ("l4", "Little one, a good meal is a good friend. Come, sit.", "tender", "soft, warm"),
    ],
    "grandma": [
        ("l1", "Everybody asks. We never pour it in. First we turn it into jelly.", "neutral", "calm, precise"),
        ("l2", "Hah! Too hot? I did tell you, my dear.", "laugh", "teasing"),
        ("l3", "Your father sat right there. He was very patient.", "tender", "soft, emotional"),
        ("l4", "Eight folds, no more, no less. Watch my fingers.", "neutral", "precise"),
    ],
    "narrator": [
        ("l1", "Legend says, in a small shop, one very large bun.", "solemn", "royal, slow"),
        ("l2", "Many people believe it was the best bun in all the land.", "solemn", "amused"),
        ("l3", "And so the hungry traveler walked on, toward the next town.", "tender", "soft, slow"),
        ("l4", "Behold! The Great Bun of Nanxiang!", "excited", "grand outburst"),
    ],
    "host": [
        ("l1", "Welcome back to the Silk Road. Today, one dumpling, one big question.", "host", "warm host"),
        ("l2", "Wait for it... here comes the steam!", "excited", "excited"),
        ("l3", "Dad was right. The best part is always the part you wait for.", "tender", "soft, emotional"),
        ("l4", "Let's go find out!", "host", "energetic"),
    ],
}
# Orpheus inline emotion tags (only the Orpheus engine reads these)
ORPHEUS_TEXT = {("uncle", "l1"): "For dumpling research! <laugh>", ("grandma", "l2"): "<chuckle> Hah! Too hot? I did tell you, my dear.",
                ("boy", "l2"): "<gasp> Uncle, no! That is MY dumpling!", ("narrator", "l4"): "Behold! The Great Bun of Nanxiang!"}

# Qwen3-TTS VoiceDesign prompts: d0 = the current default (production/v4), d1-d4 = new designs
QWEN_DESIGNS = {
    "boy": [
        "A 7-year-old boy with a bright, clear child's voice, quick and dry, a cheeky little deadpan, never shouting unless the note says so, like a witty kid host.",
        "A seven-year-old boy with a soft, warm, slightly shy child's voice, high and gentle, curious, a little breathy when amazed.",
        "A small, sweet-voiced young boy around six or seven, bright and clear, earnest and full of wonder, speaks quickly when excited and trails off when unsure.",
        "A young child, about seven years old, a boy with a light, innocent voice, cheerful and a bit hesitant, wide-eyed with wonder, like a gentle storybook hero.",
        "A seven-year-old boy with a slightly raspy, cheeky little voice, playful and quick, giggles easily, but quiet and sincere when moved.",
    ],
    "uncle": [
        "A huge, warm, middle-aged man with a deep, rich, theatrical voice, a little husky, operatic and over the top when grand, tiny and wheezy when defeated, quiet and sincere when moved.",
        "A big, warm bear of a man in his forties, deep rich baritone, jolly and generous, bursts into booming enthusiasm, then turns quiet and tender.",
        "A very deep, gravelly, large man's voice, slow and dignified like a retired opera singer, who sometimes erupts into manic, squeaky comic shouting.",
        "A middle-aged man with a deep, warm, chesty voice, a hungry food lover, dramatic and theatrical, gasping with delight, soft and kind when serious.",
        "A hearty, rumbling bass voice, a gentle giant, dignified but easily excitable, speaks with a smile and a laugh in the throat.",
    ],
    "grandma": [
        "An elderly woman, a village cook, flat, dry and unimpressed, a little raspy, brisk, kind underneath, never raising her voice.",
        "An elderly woman, calm and precise, a warm raspy alto, teasing with a smile in her voice, unhurried.",
        "A wise old grandmother with a soft, thin, slightly trembling voice, gentle and patient, very clear diction, dry humour.",
        "A brisk, sharp-witted elderly cook, low scratchy voice, matter-of-fact with a hint of amusement, pronounces every word exactly.",
        "An elderly woman with a warm, mellow, storytelling voice, slow and kind, a little playful teasing, like a beloved village grandmother.",
    ],
    "narrator": [
        "A huge, booming, epic anime-trailer narrator voice, deep and thunderous and theatrical, with slow dramatic pauses.",
        "A deep, regal male voice, slow and measured, like an ancient king reading a scroll aloud, with a hint of amusement.",
        "A rich, resonant bass voice, a royal storyteller, grand and unhurried, a smile beneath the solemnity, with long dramatic pauses.",
        "A mature, velvety, smooth baritone, an old court chronicler with dry wit, slow, warm and wise.",
        "A deep, mystical, almost whispery storyteller voice, slow and hypnotic, amused, as if a legend were coming to life.",
    ],
    "host": [
        "A 7-year-old boy with a bright, clear child's voice, quick and dry, a cheeky little deadpan, never shouting unless the note says so, like a witty kid host.",
        "A warm, friendly young child host, about eight years old, clear and cheerful, speaking straight to the audience like a kids' documentary presenter.",
        "A gentle, curious young boy narrator, soft and thoughtful, reading from a storybook, calm pace, smiling.",
        "A bright, energetic boy host around ten years old, enthusiastic and upbeat, crisp pronunciation, kids' TV show style.",
        "A warm young teenage boy's voice, calm, friendly and clear, a storyteller in a nature documentary, with a little wonder.",
    ],
}
# Kokoro voices (voice, pitch ratio) used as the SYNTHETIC reference clips of Chatterbox (never a real person)
CB_REFS = {
    "boy": [("am_puck", 1.12), ("am_liam", 1.2)],
    "uncle": [("am_michael", 0.9), ("am_onyx", 0.92)],
    "grandma": [("af_sarah", 0.96), ("bf_emma", 0.9)],
    "narrator": [("bm_george", 0.9), ("bm_fable", 0.86)],
    "host": [("am_puck", 1.05), ("am_echo", 1.08)],
}
# Orpheus built-in voices tried per character (Orpheus has no child voices)
ORPHEUS_CAST = {"uncle": ["dan"], "narrator": ["zac"], "grandma": ["tara"], "host": ["leo"], "boy": ["leo"]}
QWEN_STYLE = {"neutral": "Natural, relaxed and conversational.", "host": "Warm, friendly and curious, with a smile in the voice.",
              "excited": "Excited and delighted, fast and lively, with big expressive ups and downs in pitch.",
              "tender": "Soft, gentle and sincere, slightly slower.", "dreamy": "Dreamy and wondering, slow, savouring each word.",
              "tiny": "Small, quiet and stunned, a short pause at the start.", "solemn": "Slow, solemn and mysterious, a storyteller telling an ancient legend.",
              "laugh": "Laughing, joyful, playful and over the top."}
