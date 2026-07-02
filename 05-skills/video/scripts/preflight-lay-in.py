#!/usr/bin/env python3
"""
Pre-flight checks for `/video lay-in <slug>`.

Verifies the inputs the graphics lay-in needs are present: a base edit timeline
under rough-cuts/ that references the raw footage (the `/video remap` output, or
the `/video selects` rough cut), MMSS-named assets under assets/overlays and/or
assets/cards, and ffprobe on PATH. Reports state as JSON on stdout and exits
0 (ready), 1 (re-run prompt needed), or 2 (failed check).

Usage:
    python3 preflight-lay-in.py <slug>

Output (JSON on stdout):
    {
      "slug": "videoNN-slug",
      "docs_folder": "/abs/path/...",
      "rough_cuts_dir": "/abs/.../rough-cuts",
      "assets_dir": "/abs/.../assets",
      "base_xml": "/abs/.../rough-cuts/...remapped-to-raw.xml" | null,  # null if 0 or >1 candidates
      "base_candidates": ["/abs/...xml", ...],   # raw-referencing timelines under rough-cuts/
      "overlay_count": 18,
      "card_count": 11,
      "assets_total": 29,
      "ffprobe": "/abs/ffprobe" | null,
      "output_path": "/abs/.../rough-cuts/<base-stem>-with-graphics.xml" | null,
      "output_exists": true|false,
      "layin_script": "/abs/.../scripts/lay-in-graphics.py",
      "status": "ready" | "rerun_prompt" | "failed",
      "errors": ["..."]
    }
"""
import json
import shutil
import sys
from pathlib import Path

DOCS_ROOT = Path("/Users/jashia/Documents/1_Projects/videos")
LAYIN_SCRIPT = Path(
    "/Users/jashia/Documents/1_Projects/ai-system/.claude/skills/video/scripts/lay-in-graphics.py"
)
OUTPUT_SUFFIX = "-with-graphics.xml"
DESCRIPT_MARKER = "Exported by Descript"


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"status": "failed", "errors": ["usage: preflight-lay-in.py <slug>"]}))
        return 2

    slug = sys.argv[1]
    docs = DOCS_ROOT / slug
    rough = docs / "rough-cuts"
    assets = docs / "assets"
    errors = []

    if not docs.is_dir():
        errors.append(f"working folder not found: {docs}")

    # --- base timeline candidates: raw-referencing xmeml under rough-cuts/ ---
    base_candidates = []
    raw_token = f"/{slug}/raw/"
    if rough.is_dir():
        for xml in sorted(rough.rglob("*.xml")):
            if xml.name.lower().endswith(OUTPUT_SUFFIX):
                continue  # never feed our own output back in (case-insensitive)
            try:
                text = xml.read_text(errors="ignore")
            except OSError:
                continue
            if DESCRIPT_MARKER in text:
                continue  # Descript export references the render, not raw
            if raw_token in text or "/raw/" in text:
                base_candidates.append(str(xml))
    else:
        errors.append(f"rough-cuts/ not found: {rough} (run /video selects or /video remap first)")

    base_xml = None
    if len(base_candidates) == 1:
        base_xml = base_candidates[0]
    elif len(base_candidates) > 1:
        remapish = [c for c in base_candidates if "remap" in Path(c).name.lower()]
        if len(remapish) == 1:
            base_xml = remapish[0]
    if not base_candidates:
        errors.append(
            f"no raw-referencing base timeline under {rough} "
            "(expected the /video remap output or the /video selects rough cut)"
        )

    # --- assets: MMSS-named overlays/.mov and cards/.mp4|.mov ---------------
    def mmss_files(folder, exts):
        if not folder.is_dir():
            return []
        return sorted(
            str(p) for p in folder.iterdir()
            if p.suffix.lower() in exts and p.name[:4].isdigit() and not p.name.startswith(".")
        )

    overlays = mmss_files(assets / "overlays", {".mov"})
    cards = mmss_files(assets / "cards", {".mp4", ".mov"})
    assets_total = len(overlays) + len(cards)
    if assets_total == 0:
        errors.append(
            f"no MMSS-named assets under {assets}/overlays or {assets}/cards "
            "(run /video assets or render your graphics first)"
        )

    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        errors.append("ffprobe not on PATH (brew install ffmpeg)")

    if not LAYIN_SCRIPT.is_file():
        errors.append(f"lay-in script missing: {LAYIN_SCRIPT}")

    # --- output path + existence ------------------------------------------
    output_path = None
    output_exists = False
    if base_xml:
        stem = Path(base_xml).name[: -len(".xml")]
        output_path = str(rough / f"{stem}{OUTPUT_SUFFIX}")
        output_exists = Path(output_path).is_file()

    if errors:
        status = "failed"
    elif output_exists:
        status = "rerun_prompt"
    else:
        status = "ready"

    print(json.dumps({
        "slug": slug,
        "docs_folder": str(docs),
        "rough_cuts_dir": str(rough),
        "assets_dir": str(assets),
        "base_xml": base_xml,
        "base_candidates": base_candidates,
        "overlay_count": len(overlays),
        "card_count": len(cards),
        "assets_total": assets_total,
        "ffprobe": ffprobe,
        "output_path": output_path,
        "output_exists": output_exists,
        "layin_script": str(LAYIN_SCRIPT),
        "status": status,
        "errors": errors,
    }, indent=2))

    return {"failed": 2, "rerun_prompt": 1, "ready": 0}[status]


if __name__ == "__main__":
    sys.exit(main())
