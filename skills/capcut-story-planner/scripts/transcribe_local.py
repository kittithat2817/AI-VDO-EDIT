"""Prepare or run the shared, local CapCut transcription workflow."""

import argparse
import hashlib
import json
import math
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict
from importlib import import_module
from importlib.metadata import version
from pathlib import Path


MLX = ("mlx-whisper", "mlx-community/whisper-large-v3-mlx",
       "49e6aa286ad60c14352c404340ded53710378a11", ["config.json", "weights.npz"])
CPU = ("faster-whisper", "Systran/faster-whisper-large-v3",
       "edaa852ec7e145841d8ffdb056a99866b5f0a478",
       ["config.json", "model.bin", "preprocessor_config.json", "tokenizer.json", "vocabulary.json"])


def fingerprint(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def transcribe(audio, model_path, engine, language):
    options = dict(language=language, word_timestamps=True, condition_on_previous_text=False)
    if engine == "mlx-whisper":
        import mlx_whisper

        result = mlx_whisper.transcribe(audio, path_or_hf_repo=model_path,
                                        temperature=0.0, verbose=None, **options)
        return result["language"], result["segments"]

    from faster_whisper import WhisperModel

    model = WhisperModel(model_path, device="cpu", compute_type="int8", local_files_only=True)
    segments, info = model.transcribe(audio, beam_size=5, vad_filter=False, **options)
    return info.language, [
        {"start": segment.start, "end": segment.end, "text": segment.text,
         "words": [asdict(word) for word in (segment.words or [])]}
        for segment in segments
    ]


def validate_timing(segments, duration):
    for segment in segments:
        for item in (segment, *segment.get("words", [])):
            start, end = item["start"], item["end"]
            if not (math.isfinite(start) and math.isfinite(end)
                    and 0 <= start <= end <= duration + 0.05):
                raise ValueError(f"Invalid ASR timestamp {start}–{end} for {duration:.3f}s of audio")
        if segment["text"].strip() and not segment.get("words"):
            raise ValueError("ASR returned speech without word timestamps. Review this audio before editing.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpu", action="store_true", help="Explicitly use the approved CPU route")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare", help="Download the pinned model to the local cache")
    commands.add_parser("check", help="Check local prerequisites without downloading")
    run = commands.add_parser("run", help="Transcribe a complete local media file")
    run.add_argument("source", type=Path)
    run.add_argument("output", type=Path)
    run.add_argument("--language", help="Known language code such as th. Default is auto-detection.")
    run.add_argument("--audio-stream", type=int, default=0, help="Zero-based audio stream index")
    args = parser.parse_args()
    apple_silicon = platform.system() == "Darwin" and platform.machine() == "arm64"
    engine, model_id, revision, files = MLX if apple_silicon and not args.cpu else CPU
    try:
        engine_version = version(engine)
        from huggingface_hub import snapshot_download

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise ValueError("FFmpeg is missing from PATH. See references/local-transcription.md.")
        model_path = snapshot_download(
            repo_id=model_id, revision=revision, allow_patterns=files,
            local_files_only=args.command != "prepare",
        )
        if any(not (Path(model_path) / name).is_file() for name in files):
            raise ValueError("Model cache is incomplete. Run prepare with this same route.")
        if args.command == "check":
            import_module(engine.replace("-", "_"))
        if args.command != "run":
            print(f"{engine} {engine_version} | {model_id}@{revision} | {ffmpeg}")
            return 0

        import numpy as np

        source = args.source.resolve(strict=True)
        if args.audio_stream < 0 or not source.is_file():
            raise ValueError("Use a local media file and a nonnegative audio stream index.")
        if args.output.exists():
            raise ValueError("Output already exists. Choose a new transcript path.")
        source_hash = fingerprint(source)
        pcm = subprocess.run(
            [ffmpeg, "-v", "error", "-nostdin", "-i", str(source), "-map",
             f"0:a:{args.audio_stream}", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
            check=True, capture_output=True,
        ).stdout
        if not pcm:
            raise ValueError("The selected audio stream is empty.")
        audio = np.frombuffer(pcm, dtype="<f4").copy()
        duration = len(audio) / 16000
        language, segments = transcribe(audio, model_path, engine, args.language)
        validate_timing(segments, duration)
        if fingerprint(source) != source_hash:
            raise ValueError("Source changed during transcription. Rerun against the current file.")
        payload = {
            "schema_version": 1, "engine": engine, "engine_version": engine_version,
            "model": model_id, "model_revision": revision, "language": language,
            "source": str(source), "source_sha256": source_hash,
            "audio_stream": args.audio_stream, "duration_seconds": duration,
            "time_basis": "seconds_from_selected_audio_stream_start",
            "segments": segments,
        }
        serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized + "\n")
        print(args.output)
        return 0
    except Exception as error:
        detail = error.stderr.decode(errors="replace").strip() if isinstance(error, subprocess.CalledProcessError) else str(error)
        print(f"{engine} / {model_id}: {detail}", file=sys.stderr)
        print("Check the required package, FFmpeg and pinned cache. See references/local-transcription.md.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
