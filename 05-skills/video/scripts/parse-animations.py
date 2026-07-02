#!/usr/bin/env python3
"""
Parse animation-ideas.md (output of /associate-producer Gap 3) into
structured JSON.

For each `### <ID>. <Name>` block, extracts:
    id, name, anchor, offset_ms, duration_ms, spec (concatenated text),
    heuristic_class (remotion | ai-clip | manual)

The heuristic_class is a first-pass guess. The /video assets workflow
reviews each item and may override the class before generation.

Also merges `target_timestamp` from selects-manifest.json when an item's
id matches an entry there.

Usage:
    python3 parse-animations.py <animation-ideas.md> [<selects-manifest.json>]

Output: JSON on stdout.
"""
import json
import re
import sys
from pathlib import Path

# Lower-cased substring hints. Order matters: manual wins over ai-clip wins over remotion.
MANUAL_HINTS = (
    "real screenshot", "actual screenshot", "screenshot of",
    "github readme", "user's webcam", "live demo", "screen recording",
    "hand-drawn", "hand drawn", "real photo", "photo of the user",
    "in person", "production footage",
)
AI_CLIP_HINTS = (
    "b-roll", "broll", "b roll", "mood shot", "cinematic", "atmospheric",
    "stock footage", "abstract visual", "ambient footage",
    "establishing shot", "scene transition", "macro shot", "drone shot",
    "the feeling of", "generative",
)

HEADING_RE = re.compile(r"^###\s+([A-Z]+\d+)\.\s+`([^`]+)`")
FIELD_RE = re.compile(r"^\s*[-*]\s+\*\*([^*:]+):\*\*\s+(.+?)\s*$")
NUM_MS_RE = re.compile(r"(-?\d+)\s*ms")
# Timing Report row: | G1 `TwoBrains` | 00:00:00,004 | 00:00:03,004 | 3s | "anchor" |
TIMING_ROW_RE = re.compile(
    r"^\|\s*([A-Z]+\d+)\s+`[^`]+`\s*\|\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*\|"
)


def classify(spec_text_lower: str) -> str:
    for hint in MANUAL_HINTS:
        if hint in spec_text_lower:
            return "manual"
    for hint in AI_CLIP_HINTS:
        if hint in spec_text_lower:
            return "ai-clip"
    return "remotion"


def parse_timing_report(text: str) -> dict[str, str]:
    """Extract id -> final_cut_in from the Timing Report table at the top."""
    timings: dict[str, str] = {}
    for line in text.splitlines():
        m = TIMING_ROW_RE.match(line)
        if m:
            timings[m.group(1)] = m.group(2)
    return timings


def parse_items(text: str) -> list[dict]:
    items: list[dict] = []
    current: dict | None = None

    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if m:
            if current is not None:
                items.append(current)
            current = {
                "id": m.group(1).strip(),
                "name": m.group(2).strip(),
                "anchor": None,
                "offset_ms": 0,
                "duration_ms": None,
                "spec_lines": [],
            }
            continue

        if current is None:
            continue

        if line.startswith("##") and not line.startswith("###"):
            items.append(current)
            current = None
            continue

        fm = FIELD_RE.match(line)
        if fm:
            key = fm.group(1).strip().lower()
            val = fm.group(2).strip()
            if key == "anchor":
                current["anchor"] = val.strip("`").strip('"').strip()
            elif key == "offset":
                om = NUM_MS_RE.search(val)
                if om:
                    current["offset_ms"] = int(om.group(1))
            elif key == "duration":
                dm = NUM_MS_RE.search(val)
                if dm:
                    current["duration_ms"] = int(dm.group(1))
            else:
                current["spec_lines"].append(f"{key}: {val}")
            continue

        stripped = line.strip()
        if stripped and not stripped.startswith("|") and not stripped.startswith("---"):
            current["spec_lines"].append(stripped)

    if current is not None:
        items.append(current)

    for item in items:
        spec = " ".join(item.pop("spec_lines", [])).strip()
        item["spec"] = spec
        item["heuristic_class"] = classify(spec.lower())

    return items


def load_selects_timestamps(manifest_path: Path) -> dict[str, str]:
    """Return id -> target_timestamp from the selects manifest, if present."""
    if not manifest_path.is_file():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    timestamps: dict[str, str] = {}
    clips = data.get("clips") or data.get("selects") or []
    if isinstance(clips, list):
        for clip in clips:
            if not isinstance(clip, dict):
                continue
            clip_id = clip.get("id")
            target = (
                clip.get("target_timestamp")
                or clip.get("final_cut_in")
                or clip.get("timecode")
                or clip.get("start")
            )
            if clip_id and target:
                timestamps[str(clip_id)] = str(target)
    return timestamps


def main() -> int:
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(
            "Usage: parse-animations.py <animation-ideas.md> [<selects-manifest.json>]",
            file=sys.stderr,
        )
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"animation-ideas.md not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    items = parse_items(text)
    timing_report = parse_timing_report(text)

    selects_timestamps: dict[str, str] = {}
    if len(sys.argv) == 3:
        selects_timestamps = load_selects_timestamps(Path(sys.argv[2]))

    for item in items:
        item["target_timestamp"] = (
            timing_report.get(item["id"])
            or selects_timestamps.get(item["id"])
        )

    print(json.dumps(
        {"path": str(path), "count": len(items), "items": items},
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
