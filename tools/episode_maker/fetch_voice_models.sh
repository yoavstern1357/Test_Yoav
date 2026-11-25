#!/bin/sh
# Downloads the optional CPU voice models into tools/episode_maker/tts/ (git-ignored). Needs only github.com.
# Kokoro (default engine):  see README.md.   Optional engines (pip install sherpa-onnx):
#   supertonic  Supertonic-2 int8 ONNX, 10 built-in synthetic voices, weights OpenRAIL-M (commercial use allowed)
#   pocket      Kyutai Pocket TTS int8 ONNX, weights CC-BY-4.0 (credit "Kyutai Pocket TTS" in the video description)
set -e
cd "$(dirname "$0")/tts"
B=https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models
[ -d supertonic ] || { curl -L -o /tmp/st.tar.bz2 $B/sherpa-onnx-supertonic-tts-int8-2026-03-06.tar.bz2 && mkdir supertonic && tar xjf /tmp/st.tar.bz2 -C supertonic --strip-components=1; }
[ -d pocket ] || { curl -L -o /tmp/pk.tar.bz2 $B/sherpa-onnx-pocket-tts-int8-2026-01-26.tar.bz2 && mkdir pocket && tar xjf /tmp/pk.tar.bz2 -C pocket --strip-components=1 && rm -rf pocket/test_wavs; }
ls supertonic pocket
