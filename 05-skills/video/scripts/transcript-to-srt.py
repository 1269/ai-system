#!/usr/bin/env python3
"""
Convert a word-level Whisper transcript JSON to standard SRT captions.

Groups words into cues that target ~7 seconds each, breaking earlier when a
sentence-ending word is reached. Falls back to soft caps if no punctuation
shows up in time.

Input shape (from connectors/speech-to-text/transcribe_video.py):
    {
      "captions": [
        {"text": "Hello", "startMs": 0, "endMs": 320, ...},
        ...
      ],
      "segments": [...]   # used as a fallback if captions is empty
    }

Usage:
    python3 transcript-to-srt.py <transcript.json> -o <output.srt>
    python3 transcript-to-srt.py <transcript.json>          # writes alongside JSON

Exit codes:
    0: wrote SRT
    1: input file missing or unreadable
    2: transcript has neither captions nor segments
"""
import argparse
import json
import sys
from pathlib import Path

TARGET_SECONDS = 7.0
HARD_CAP_SECONDS = 10.0
MAX_CHARS_PER_CUE = 84  # ~2 lines of 42 chars
SENTENCE_END = (".", "!", "?")
SOFT_BREAK = (",", ";", ":")


def fmt_srt_time(ms: int) -> str:
    """Format milliseconds as SRT timestamp `HH:MM:SS,mmm`."""
    if ms < 0:
        ms = 0
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def words_from_captions(captions: list[dict]) -> list[dict]:
    """Coerce the flat captions list into uniform {text, startMs, endMs} dicts."""
    out = []
    for w in captions:
        text = (w.get("text") or "").strip()
        if not text:
            continue
        start = int(w.get("startMs", 0))
        end = int(w.get("endMs", start))
        if end < start:
            end = start
        out.append({"text": text, "startMs": start, "endMs": end})
    return out


def words_from_segments(segments: list[dict]) -> list[dict]:
    """Fallback word extraction from segments[].words when top-level captions is empty."""
    out = []
    for seg in segments:
        for w in seg.get("words", []) or []:
            text = (w.get("text") or w.get("word") or "").strip()
            if not text:
                continue
            start = int(w.get("startMs", 0))
            end = int(w.get("endMs", start))
            out.append({"text": text, "startMs": start, "endMs": end})
    return out


def should_break(current_text: str, word_text: str, cue_duration_s: float) -> bool:
    """Decide whether to flush the current cue before appending word_text."""
    if not current_text:
        return False
    if cue_duration_s >= HARD_CAP_SECONDS:
        return True
    # Prefer sentence-end breaks once we've hit the target window
    if cue_duration_s >= TARGET_SECONDS and current_text.rstrip().endswith(SENTENCE_END):
        return True
    # Soft-break at a comma if we're past target and the next chunk would push us long
    if cue_duration_s >= TARGET_SECONDS and current_text.rstrip().endswith(SOFT_BREAK):
        return True
    # Char-length guard: keep cues readable on screen
    if len(current_text) + 1 + len(word_text) > MAX_CHARS_PER_CUE and cue_duration_s >= TARGET_SECONDS * 0.6:
        return True
    return False


def group_into_cues(words: list[dict]) -> list[dict]:
    """Group words into SRT cues."""
    cues: list[dict] = []
    if not words:
        return cues

    cur_text = ""
    cur_start = words[0]["startMs"]
    cur_end = words[0]["endMs"]

    for w in words:
        duration_s = (cur_end - cur_start) / 1000.0
        if should_break(cur_text, w["text"], duration_s):
            cues.append({"startMs": cur_start, "endMs": cur_end, "text": cur_text.strip()})
            cur_text = w["text"]
            cur_start = w["startMs"]
            cur_end = w["endMs"]
        else:
            cur_text = (cur_text + " " + w["text"]).strip() if cur_text else w["text"]
            cur_end = max(cur_end, w["endMs"])

    if cur_text:
        cues.append({"startMs": cur_start, "endMs": cur_end, "text": cur_text.strip()})

    # Guarantee monotonic, non-overlapping cues
    for i in range(1, len(cues)):
        if cues[i]["startMs"] < cues[i - 1]["endMs"]:
            cues[i]["startMs"] = cues[i - 1]["endMs"]
        if cues[i]["endMs"] <= cues[i]["startMs"]:
            cues[i]["endMs"] = cues[i]["startMs"] + 500

    return cues


def render_srt(cues: list[dict]) -> str:
    lines: list[str] = []
    for i, cue in enumerate(cues, start=1):
        lines.append(str(i))
        lines.append(f"{fmt_srt_time(cue['startMs'])} --> {fmt_srt_time(cue['endMs'])}")
        lines.append(cue["text"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", help="Path to Whisper transcript JSON")
    parser.add_argument("-o", "--output", help="Output SRT path. Defaults to <input>.srt")
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.is_file():
        print(f"Transcript not found: {in_path}", file=sys.stderr)
        return 1

    try:
        data = json.loads(in_path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"Could not read transcript JSON: {e}", file=sys.stderr)
        return 1

    words = words_from_captions(data.get("captions") or [])
    if not words:
        words = words_from_segments(data.get("segments") or [])
    if not words:
        print("Transcript has no word-level data (captions/segments).", file=sys.stderr)
        return 2

    cues = group_into_cues(words)
    srt = render_srt(cues)

    out_path = Path(args.output) if args.output else in_path.with_suffix(".srt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(srt)

    print(f"Wrote {out_path} ({len(cues)} cues)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
