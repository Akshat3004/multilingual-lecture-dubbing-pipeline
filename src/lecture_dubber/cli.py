"""CLI for an experimental multilingual lecture dubbing pipeline."""
from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from pathlib import Path
from lecture_dubber.pipeline import run_pipeline
from lecture_dubber.media import mux_video


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audio dubbing baseline, not visual lip sync")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Transcribe, translate, and synthesize a lecture")
    run.add_argument("video", type=Path)
    run.add_argument("--language", required=True, choices=("hi", "ta"))
    run.add_argument("--output-dir", required=True, type=Path)
    run.add_argument("--whisper-model", default="base")

    mux = commands.add_parser("mux", help="Replace soundtrack if durations match closely")
    mux.add_argument("video", type=Path)
    mux.add_argument("narration", type=Path)
    mux.add_argument("output", type=Path)
    mux.add_argument("--max-mismatch", type=float, default=0.05)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "run":
        result = asdict(run_pipeline(args.video, args.language, args.output_dir, args.whisper_model))
    else:
        result = mux_video(args.video, args.narration, args.output, args.max_mismatch)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
