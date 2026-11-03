# Roadmap toward actual video lip synchronization

This repository currently handles audio transcription, English-to-Hindi/Tamil translation, generic speech synthesis, and guarded audio replacement only.

1. Assemble a permitted evaluation dataset with reference transcripts and translations.
2. Retain word and sentence timestamps instead of flattening transcripts.
3. Translate and synthesize per segment, matching pause structure and timing.
4. Measure ASR word error rate, translation quality, narration intelligibility and duration mismatch.
5. If authorized, add a licensed lip-sync model to modify visual mouth movements, and benchmark it separately.
6. Document recording/voice permissions, model licenses, runtime, human review and known artifacts.
7. Add an end-to-end reproducibility test with redistributable media.

These are future steps, not completed capabilities or measured results.
