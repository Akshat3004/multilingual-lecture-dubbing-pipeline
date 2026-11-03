"""Speech recognition → chunked translation → generic synthetic speech."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from pathlib import Path
import json
from lecture_dubber.media import duration_seconds, extract_audio, mismatch_ratio
from lecture_dubber.text import require_language, translate_text


@dataclass(frozen=True)
class Report:
    video_seconds: float
    narration_seconds: float
    duration_mismatch_ratio: float
    duration_review_required: bool
    target_language: str
    whisper_model: str
    visual_lip_sync: bool = False
    voice_cloning: bool = False


def recognize_english(wav_file: Path, model_name: str) -> str:
    import whisper  # Optional expensive dependency imported only when used
    model = whisper.load_model(model_name)
    result = model.transcribe(str(wav_file), language="en", fp16=False)
    transcript = result.get("text", "").strip()
    if not transcript:
        raise RuntimeError("Whisper returned an empty transcript")
    return transcript


def translate_from_english(transcript: str, language: str) -> str:
    from deep_translator import GoogleTranslator  # External network service
    require_language(language)
    translator = GoogleTranslator(source="en", target=language)
    return translate_text(transcript, translator.translate)


def synthesize_generic_voice(translated_text: str, language: str, out_mp3: Path) -> None:
    from gtts import gTTS  # Third-party network service
    require_language(language)
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    gTTS(text=translated_text, lang=language, slow=False).save(str(out_mp3))


def run_pipeline(video: Path, language: str, output_dir: Path, model_name: str = "base") -> Report:
    require_language(language)
    if not video.is_file():
        raise FileNotFoundError(video)
    output_dir.mkdir(parents=True, exist_ok=True)
    wav = output_dir / "source_audio.wav"
    extract_audio(video, wav)

    transcript = recognize_english(wav, model_name)
    (output_dir / "transcript.en.txt").write_text(transcript + "\n", encoding="utf-8")
    translated = translate_from_english(transcript, language)
    (output_dir / f"translation.{language}.txt").write_text(translated + "\n", encoding="utf-8")

    narration = output_dir / f"narration.{language}.mp3"
    synthesize_generic_voice(translated, language, narration)
    video_seconds = duration_seconds(video)
    narration_seconds = duration_seconds(narration)
    ratio = mismatch_ratio(video_seconds, narration_seconds)
    report = Report(video_seconds=round(video_seconds, 3),
                    narration_seconds=round(narration_seconds, 3),
                    duration_mismatch_ratio=round(ratio, 5),
                    duration_review_required=ratio > 0.05,
                    target_language=language, whisper_model=model_name)
    (output_dir / "report.json").write_text(json.dumps(asdict(report), indent=2) + "\n", encoding="utf-8")
    return report
