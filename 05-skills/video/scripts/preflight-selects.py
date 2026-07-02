#!/usr/bin/env python3
"""
Pre-flight checks for `/video selects <slug>`.

Verifies the working folder and Obsidian meta folder are in a state
where the selects pipeline can run. Reports state as JSON on stdout
and exits 0 (ready), 1 (re-run prompt needed), or 2 (failed check).

Usage:
    python3 preflight-selects.py <slug>

Output (JSON on stdout):
    {
      "slug": "videoNN-slug",
      "docs_folder": "/abs/path/...",
      "obs_folder": "/abs/path/...",
      "raw_files": ["/abs/path/raw/a.mp4", ...],
      "missing_transcripts": ["/abs/path/raw/a.mp4", ...],
      "manifest_exists": true|false,
      "manifest_path": "/abs/path/...",
      "selects_dir": "/abs/path/...",
      "status": "ready" | "rerun_prompt" | "failed",
      "errors": ["..."]
    }
"""
import json
import sys
from pathlib import Path

DOCS_ROOT = Path("/Users/jashia/Documents/1_Projects/videos")
OBS_ROOT = Path(
    "/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects"
)

PLAN_FILES = ("task-list.md", "brief.md", "script.md")
RAW_EXTENSIONS = {".mp4", ".mov"}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: preflight-selects.py <slug>", file=sys.stderr)
        return 2

    slug = sys.argv[1]
    docs_folder = DOCS_ROOT / slug
    obs_folder = OBS_ROOT / slug
    raw_dir = docs_folder / "raw"
    transcripts_dir = docs_folder / "transcripts"
    producer_dir = obs_folder / "producer"
    manifest_path = producer_dir / "selects-manifest.json"
    selects_dir = docs_folder / "selects"

    errors: list[str] = []

    if not docs_folder.is_dir():
        errors.append(
            f"Working folder missing: {docs_folder}. "
            f"Create it or run /video new to bootstrap."
        )

    if not raw_dir.is_dir():
        errors.append(
            f"raw/ folder missing at {raw_dir}. "
            f"Drop .mp4 or .mov footage in there first."
        )
        raw_files: list[Path] = []
    else:
        raw_files = sorted(
            p for p in raw_dir.iterdir()
            if p.is_file() and p.suffix.lower() in RAW_EXTENSIONS
        )
        if not raw_files:
            errors.append(
                f"No .mp4 or .mov files in {raw_dir}. "
                f"Drop raw footage there before running /video selects."
            )

    if not obs_folder.is_dir():
        errors.append(
            f"Obsidian meta folder missing: {obs_folder}. "
            f"Run /video new to bootstrap both folder trees."
        )
        plan_file: Path | None = None
    else:
        plan_file = next(
            (obs_folder / name for name in PLAN_FILES if (obs_folder / name).is_file()),
            None,
        )
        if plan_file is None:
            errors.append(
                f"No planned content found in {obs_folder}. "
                f"Expected one of: {', '.join(PLAN_FILES)}. "
                f"Run /video new or /story-development first."
            )

    missing_transcripts: list[str] = []
    if raw_files:
        for raw in raw_files:
            t_path = transcripts_dir / f"{raw.stem}.json"
            if not t_path.is_file():
                missing_transcripts.append(str(raw))

    manifest_exists = manifest_path.is_file()

    if errors:
        status = "failed"
    elif manifest_exists:
        status = "rerun_prompt"
    else:
        status = "ready"

    payload = {
        "slug": slug,
        "docs_folder": str(docs_folder),
        "obs_folder": str(obs_folder),
        "raw_dir": str(raw_dir),
        "transcripts_dir": str(transcripts_dir),
        "producer_dir": str(producer_dir),
        "manifest_path": str(manifest_path),
        "selects_dir": str(selects_dir),
        "plan_file": str(plan_file) if plan_file else None,
        "raw_files": [str(p) for p in raw_files],
        "missing_transcripts": missing_transcripts,
        "manifest_exists": manifest_exists,
        "status": status,
        "errors": errors,
    }

    print(json.dumps(payload, indent=2))

    if status == "failed":
        return 2
    if status == "rerun_prompt":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
