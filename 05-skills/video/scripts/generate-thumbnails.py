#!/usr/bin/env python3
"""
Generate YouTube thumbnail variants from a final mp4 + a hook word.

Approach:
  1. Probe the video duration with ffprobe.
  2. Extract candidate face-cam frames at 25%, 50%, 75% (configurable).
  3. ffmpeg drawtext overlays the hook word in big bold text with a black stroke.
  4. Writes thumbnail-v1.png, thumbnail-v2.png, thumbnail-v3.png at 1280x720.

The composition is deliberately simple and deterministic. The user picks the
variant that has the most engaged face cam and uploads with that. The hook word
is the leftmost emphasis word from the title (passed via --hook).

Usage:
    python3 generate-thumbnails.py <video.mp4> --hook "BUILD" --out-dir <dir>
    python3 generate-thumbnails.py video.mp4 --hook "BUILD" --positions 0.20,0.50,0.80

Exit codes:
    0: wrote all variants
    1: ffmpeg/ffprobe missing or failed
    2: bad arguments (no video, no hook, etc.)
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_FONT = "/System/Library/Fonts/Supplemental/Impact.ttf"
FALLBACK_FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Verdana Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]
DEFAULT_POSITIONS = (0.25, 0.50, 0.75)
WIDTH, HEIGHT = 1280, 720


def pick_font() -> str:
    for f in [DEFAULT_FONT, *FALLBACK_FONTS]:
        if Path(f).is_file():
            return f
    raise RuntimeError("No usable bold font found on this system.")


def probe_duration(video: Path) -> float:
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                str(video),
            ],
            stderr=subprocess.STDOUT,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        raise RuntimeError(f"ffprobe failed: {e}") from e
    data = json.loads(out)
    dur = float(data["format"]["duration"])
    if dur <= 0:
        raise RuntimeError(f"Probed duration is non-positive: {dur}")
    return dur


def escape_drawtext(text: str) -> str:
    """Escape characters that ffmpeg's drawtext filter treats specially."""
    return (
        text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("%", "\\%")
    )


def build_filter(hook: str, font: str) -> str:
    safe_hook = escape_drawtext(hook.upper())
    # Pad/crop to a clean 16:9 1280x720, then draw the hook word with thick stroke
    return (
        f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},"
        f"drawtext=fontfile='{font}':"
        f"text='{safe_hook}':"
        f"fontsize=180:"
        f"fontcolor=white:"
        f"borderw=10:bordercolor=black:"
        f"x=(w-text_w)/2:"
        f"y=h-text_h-60"
    )


def extract_variant(video: Path, ts: float, out_path: Path, hook: str, font: str) -> None:
    vf = build_filter(hook, font)
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-ss", f"{ts:.3f}",
        "-i", str(video),
        "-frames:v", "1",
        "-vf", vf,
        "-y",
        str(out_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg failed at t={ts:.2f}s: {e.stderr}") from e


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("video", help="Path to the final mp4")
    parser.add_argument("--hook", required=True,
                        help="Short hook word(s) to overlay (e.g. 'BUILD', 'I QUIT')")
    parser.add_argument("--out-dir", required=True,
                        help="Directory to write thumbnail-v1.png, -v2.png, -v3.png")
    parser.add_argument("--positions", default=",".join(str(p) for p in DEFAULT_POSITIONS),
                        help="Comma-separated normalized timestamps (0.0-1.0)")
    parser.add_argument("--font", default=None,
                        help="Path to TTF/TTC font. Defaults to Impact.ttf or fallback")
    args = parser.parse_args()

    video = Path(args.video)
    if not video.is_file():
        print(f"Video not found: {video}", file=sys.stderr)
        return 2

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        print("ffmpeg and ffprobe must be on PATH.", file=sys.stderr)
        return 1

    try:
        positions = [float(p.strip()) for p in args.positions.split(",") if p.strip()]
    except ValueError:
        print("--positions must be a comma-separated list of floats.", file=sys.stderr)
        return 2
    if not positions:
        print("--positions produced no values.", file=sys.stderr)
        return 2
    for p in positions:
        if not (0.0 <= p <= 1.0):
            print(f"Position {p} out of [0.0, 1.0].", file=sys.stderr)
            return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        font = args.font or pick_font()
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    try:
        duration = probe_duration(video)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 1

    written: list[str] = []
    for i, pos in enumerate(positions, start=1):
        # Clamp a touch off the edges to avoid black frames at intro/outro
        ts = max(0.5, min(duration - 0.5, duration * pos))
        out_path = out_dir / f"thumbnail-v{i}.png"
        try:
            extract_variant(video, ts, out_path, args.hook, font)
        except RuntimeError as e:
            print(str(e), file=sys.stderr)
            return 1
        written.append(str(out_path))
        print(f"  v{i} @ {ts:.2f}s -> {out_path}", file=sys.stderr)

    print(json.dumps({"variants": written, "hook": args.hook, "duration_s": duration}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
