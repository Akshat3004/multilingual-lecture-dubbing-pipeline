"""FFmpeg/FFprobe media I/O and duration validation (no lip movement editing)."""
from __future__ import annotations
import json
import shutil
import subprocess
from pathlib import Path


def require_binary(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise RuntimeError(f"{name} was not found. Install FFmpeg and add it to PATH.")
    return found


def extract_audio(video_path: Path, wav_path: Path) -> None:
    if not video_path.is_file():
        raise FileNotFoundError(f"Input lecture not found: {video_path}")
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        require_binary("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(video_path), "-vn", "-ac", "1", "-ar", "16000",
        "-c:a", "pcm_s16le", str(wav_path),
    ], check=True)


def duration_seconds(path: Path) -> float:
    if not path.is_file():
        raise FileNotFoundError(path)
    completed = subprocess.run([
        require_binary("ffprobe"), "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], check=True, capture_output=True, text=True)
    try:
        seconds = float(completed.stdout.strip())
    except ValueError as exc:
        raise RuntimeError(f"Cannot read media duration: {path}") from exc
    if not (0 < seconds < float("inf")):
        raise RuntimeError(f"Invalid media duration: {path}")
    return seconds


def mismatch_ratio(original_seconds: float, dubbed_seconds: float) -> float:
    if original_seconds <= 0 or dubbed_seconds <= 0:
        raise ValueError("Both durations must be positive")
    return abs(dubbed_seconds - original_seconds) / original_seconds


def mux_video(video_path: Path, narration_path: Path, output_path: Path,
              max_mismatch: float = 0.05) -> dict[str, float]:
    """Replace audio only when durations are close. This does NOT sync lips."""
    if not (0 <= max_mismatch < 1):
        raise ValueError("max_mismatch must be between 0 and 1")
    if output_path.resolve() in (video_path.resolve(), narration_path.resolve()):
        raise ValueError("Output path must be distinct from both input files")
    source_duration = duration_seconds(video_path)
    narration_duration = duration_seconds(narration_path)
    ratio = mismatch_ratio(source_duration, narration_duration)
    if ratio > max_mismatch:
        raise ValueError(
            f"Cannot mux: audio length differs by {ratio:.1%} (maximum {max_mismatch:.1%}). "
            "Perform sentence-level timing alignment first; muxing is not lip-sync."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        require_binary("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(video_path), "-i", str(narration_path),
        "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
        "-movflags", "+faststart", "-shortest", str(output_path),
    ], check=True)
    return {"source_seconds": source_duration, "narration_seconds": narration_duration,
            "duration_mismatch_ratio": ratio}
