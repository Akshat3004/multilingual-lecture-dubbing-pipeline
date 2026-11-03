# Multilingual Lecture Dubbing — Speech Translation Pipeline

**Python · Whisper ASR · Machine Translation · gTTS · FFmpeg · English → Hindi/Tamil**

A reproducible, independently rewritten **dubbing baseline** based on an archived course/team prototype shared privately for portfolio review. It extracts lecture audio, transcribes English speech, translates text into Hindi or Tamil, synthesizes translated narration, and reports the timing difference before any video remuxing.

> **Current scope is dubbed narration, not visual lip synchronization.** The archived source does **not** contain a lip-sync network, phoneme alignment, voice cloning, or evaluation benchmark. This repository does not claim to implement those features.

**Original private team source:** \`prokan468/LipSync\` (link accessible only to authorized collaborators). The original code/media have **not** been republished here. This repository is a *new reference implementation*, with different structure, a command-line interface, validation and tests. See [project provenance](CONTRIBUTORS.md) and [source audit](docs/SOURCE_AUDIT.md).

## Features

- **Audio extraction:** FFmpeg converts the input lecture's soundtrack to 16 kHz mono WAV for automatic speech recognition.
- **Transcription:** local OpenAI Whisper model (\`base\` by default) outputs an English transcript.
- **Translation:** word-boundary-aware text chunking via \`deep-translator\` and Google Translate (third-party network service) to **Hindi (\`hi\`)** or **Tamil (\`ta\`)**.
- **Speech synthesis:** \`gTTS\` produces an **MP3** narration file (not an MP3 incorrectly named \`.wav\`).
- **Quality gate:** compares original video and generated speech durations and writes a JSON report. The optional video mux step refuses large mismatches.
- **Tests:** offline unit tests for chunk integrity, input validation, and timing safeguards.

### Architecture

~~~mermaid
flowchart LR
  A[Input lecture MP4] --> B[FFmpeg audio extraction]
  B --> C[Whisper English ASR]
  C --> D[Chunked translation: Hindi / Tamil]
  D --> E[gTTS translated MP3]
  A --> F[Duration comparison]
  E --> F
  F --> G{Lengths close?}
  G -->|Yes, explicit mux command| H[Replace soundtrack; original frames unchanged]
  G -->|No| I[Timing alignment required]
~~~

**Audio replacement is not lip sync**: the video's mouth movements are not modified. A genuine lip-sync stage would require a separately licensed video-generation model, aligned speech timings, consent, and quality evaluation.

## Setup

Requires Python 3.10+, installed FFmpeg and FFprobe on your PATH, disk space for the local Whisper model, and an internet connection for the translation and text-to-speech services. Package installation downloads ML dependencies and model weights.

~~~bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
ffmpeg -version
ffprobe -version
~~~

On Windows, activate \`.venv\Scripts\activate\` instead. The package's optional external integrations use service terms and may have usage limits.

## Run

Using a video you own or have permission to process:

~~~bash
lecture-dubber run /path/to/lecture.mp4 --language hi --output-dir outputs/hindi
# or Tamil
lecture-dubber run /path/to/lecture.mp4 --language ta --output-dir outputs/tamil
~~~

Outputs include:

~~~text
outputs/hindi/
├── source_audio.wav
├── transcript.en.txt
├── translation.hi.txt
├── narration.hi.mp3
└── report.json
~~~

The \`report.json\` file contains duration measurements and a warning when the translated narration does not match the source runtime.

After reviewing timing, **only when the durations are sufficiently close**, create a video with the new soundtrack:

~~~bash
lecture-dubber mux /path/to/lecture.mp4 outputs/hindi/narration.hi.mp3 outputs/hindi/dubbed.mp4
~~~

The mux step rejects a difference larger than **5%** by default; it does not fix sync. Even if it succeeds, it may truncate or leave silent moments, because there is no sentence-level timing alignment. Do **not** describe its output as lip-synchronized.

### Test without external services

~~~bash
PYTHONPATH=src python -m unittest discover -s tests -v
~~~

## Why timing alignment matters

The supplied private archive includes an **88.2-second** example lecture and **134.2-second** generated narration (\`output2.wav\` was MP3-encoded despite its filename). This is approximately a **52% runtime increase**, so blindly replacing the original audio is not a valid synchronization solution.

A stronger next iteration would align sentences to timestamps, control narration speed or pause structure, evaluate dubbed-word accuracy, and *then* integrate an actual face/lip editing model where appropriate consent and licensing exist.

## Results and limitations

| Item | Status |
|---|---|
| English speech transcription | Implemented as a Whisper integration; not benchmarked here |
| Hindi/Tamil text translation | Supported by new baseline through a third-party translation provider; not benchmarked |
| Synthesized Hindi/Tamil voice | Generic gTTS voice, **not cloning** |
| Audio replacement in a video | Optional with duration gate; **not lip synchronization** |
| Real lip movement generation | **Not implemented** |
| Claimed 200+ minutes / 92% ASR / +15% comprehension | **Not established by the supplied archive** |

No original sample lecture, personal videos, voice recordings, model weights, API keys or other private assets are included. Translation/TTS services may send text to third parties; never process sensitive material without appropriate permission. This project is for research and education, not biometric impersonation.

## Credits

- The original *private* \`prokan468/LipSync\` team project supplied the conceptual research context and an early four-script prototype.
- The CLI implementation, validation, tests and documentation in this package are newly written, not copied from the private original.
- Whisper, gTTS, deep-translator and FFmpeg are independent third-party projects subject to their respective licenses and terms.

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for the provenance statement and [docs/SOURCE_AUDIT.md](docs/SOURCE_AUDIT.md) for a script-by-script summary of the supplied archive.
