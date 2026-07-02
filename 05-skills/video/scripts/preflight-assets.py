#!/usr/bin/env python3
"""
Pre-flight checks for `/video assets <slug>`.

Verifies the working folder, Obsidian meta folder, animation-ideas.md,
selects-manifest.json, a plan doc, and the Replicate connector are in
shape for asset generation. Emits JSON on stdout and uses exit code as
a signal:

    0 = ready              (proceed)
    1 = rerun_prompt       (assets/ already has files; ask the user)
    2 = failed             (inputs missing; surface the errors and stop)

Usage:
    python3 preflight-assets.py <slug>
"""
import json
import sys
from pathlib import Path

DOCS_ROOT = Path("/Users/jashia/Documents/1_Projects/videos")
OBS_ROOT = Path(
    "/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/"
    "2 Systems/content-production/projects"
)
REPLICATE_CONNECTOR = Path(
    "/Users/jashia/Documents/1_Projects/ai-system/connectors/ai-video/replicate.py"
)
PLAN_FILES = ("script.md", "task-list.md", "brief.md")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: preflight-assets.py <slug>", file=sys.stderr)
        return 2

    slug = sys.argv[1]
    docs_folder = DOCS_ROOT / slug
    obs_folder = OBS_ROOT / slug
    producer_dir = obs_folder / "producer"
    animation_ideas = producer_dir / "animation-ideas.md"
    selects_manifest = producer_dir / "selects-manifest.json"
    assets_dir = docs_folder / "assets"
    overlays_dir = assets_dir / "overlays"
    broll_dir = assets_dir / "broll"
    manual_dir = assets_dir / "manual"
    manifest_path = assets_dir / "MANIFEST.md"
    plan_path = assets_dir / "plan.json"
    remotion_dir = docs_folder / "remotion"

    errors: list[str] = []

    if not docs_folder.is_dir():
        errors.append(
            f"Working folder missing: {docs_folder}. "
            f"Run /video new (or check the slug)."
        )

    if not obs_folder.is_dir():
        errors.append(
            f"Obsidian meta folder missing: {obs_folder}. "
            f"Run /video new to bootstrap both folder trees."
        )

    plan_file: Path | None = None
    if obs_folder.is_dir():
        plan_file = next(
            (obs_folder / name for name in PLAN_FILES if (obs_folder / name).is_file()),
            None,
        )
        if plan_file is None:
            errors.append(
                f"No plan doc found in {obs_folder}. "
                f"Expected one of: {', '.join(PLAN_FILES)}. "
                f"Run /video new or /story-development first."
            )

    if not animation_ideas.is_file():
        errors.append(
            f"animation-ideas.md missing at {animation_ideas}. "
            f"Run /associate-producer first; it writes this file."
        )

    if not selects_manifest.is_file():
        errors.append(
            f"selects-manifest.json missing at {selects_manifest}. "
            f"Run /video selects (or /associate-producer) first."
        )

    if not REPLICATE_CONNECTOR.is_file():
        errors.append(
            f"Replicate connector missing at {REPLICATE_CONNECTOR}. "
            f"The /video assets action depends on it."
        )

    assets_populated = (
        assets_dir.is_dir()
        and any(
            p for p in assets_dir.rglob("*")
            if p.is_file() and p.name not in {"plan.json", "MANIFEST.md", "README.md"}
        )
    )

    if errors:
        status = "failed"
    elif assets_populated:
        status = "rerun_prompt"
    else:
        status = "ready"

    payload = {
        "slug": slug,
        "docs_folder": str(docs_folder),
        "obs_folder": str(obs_folder),
        "producer_dir": str(producer_dir),
        "animation_ideas_path": str(animation_ideas),
        "selects_manifest_path": str(selects_manifest),
        "plan_file": str(plan_file) if plan_file else None,
        "assets_dir": str(assets_dir),
        "overlays_dir": str(overlays_dir),
        "broll_dir": str(broll_dir),
        "manual_dir": str(manual_dir),
        "manifest_path": str(manifest_path),
        "plan_path": str(plan_path),
        "remotion_dir": str(remotion_dir),
        "remotion_exists": remotion_dir.is_dir(),
        "replicate_connector": str(REPLICATE_CONNECTOR),
        "assets_already_populated": assets_populated,
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
