#!/usr/bin/env python3
"""
Pre-flight checks for `/video remap <slug>`.

Verifies the inputs the Descript-to-raw remap needs are present:
a selects-manifest.json (the render-to-raw map), the raw source it
references, and a Descript-exported xmeml somewhere under the project's
rough-cuts/ tree. Reports state as JSON on stdout and exits 0 (ready),
1 (re-run prompt needed), or 2 (failed check).

Usage:
    python3 preflight-remap.py <slug>

Output (JSON on stdout):
    {
      "slug": "videoNN-slug",
      "docs_folder": "/abs/path/...",
      "obs_folder": "/abs/path/...",
      "manifest_path": "/abs/path/.../producer/selects-manifest.json",
      "rough_cuts_dir": "/abs/path/.../rough-cuts",
      "raw_path": "/abs/raw.mp4" | null,         # null if the manifest names more than one source
      "raw_candidates": ["/abs/raw-a.mp4", ...],   # all sources from the manifest
      "descript_xml": "/abs/descript-export.xml" | null,  # null if 0 or >1 candidates
      "descript_candidates": ["/abs/...xml", ...], # every xmeml carrying the Descript marker
      "output_path": "/abs/.../rough-cuts/<slug>_descript-remapped-to-raw.xml",
      "remap_script": "/abs/.../connectors/buttercut-export/remap-descript-to-raw.py",
      "output_exists": true|false,
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
REMAP_SCRIPT = Path(
    "/Users/jashia/Documents/1_Projects/ai-system/connectors/buttercut-export/remap-descript-to-raw.py"
)
# Descript stamps this comment near the top of every xmeml it exports. It is
# the reliable way to tell a Descript export apart from the Buttercut rough-cut
# xml and from a previous remap output, all of which live under rough-cuts/.
DESCRIPT_MARKER = "Exported by Descript"


def is_descript_export(xml_path: Path) -> bool:
    try:
        with xml_path.open("r", encoding="utf-8", errors="ignore") as fh:
            head = fh.read(4096)
    except OSError:
        return False
    return DESCRIPT_MARKER in head


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: preflight-remap.py <slug>", file=sys.stderr)
        return 2

    slug = sys.argv[1]
    docs_folder = DOCS_ROOT / slug
    obs_folder = OBS_ROOT / slug
    manifest_path = obs_folder / "producer" / "selects-manifest.json"
    rough_cuts_dir = docs_folder / "rough-cuts"
    output_path = rough_cuts_dir / f"{slug}_descript-remapped-to-raw.xml"

    errors: list[str] = []
    raw_candidates: list[str] = []
    raw_path: str | None = None
    descript_candidates: list[str] = []
    descript_xml: str | None = None

    # 1. Manifest is the render-to-raw map. Without it there is nothing to remap against.
    if not manifest_path.is_file():
        errors.append(
            f"selects-manifest.json missing at {manifest_path}. "
            f"Run /video selects <slug> first to produce it."
        )
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            manifest = None
            errors.append(f"Could not read manifest {manifest_path}: {exc}")

        if manifest is not None:
            sources = manifest.get("sources") or {}
            raw_candidates = [str(v) for v in sources.values()]
            if not raw_candidates:
                errors.append(
                    f"Manifest {manifest_path} has no 'sources'. "
                    f"Cannot determine the raw file to remap onto."
                )
            elif len(raw_candidates) == 1:
                raw_path = raw_candidates[0]
                if not Path(raw_path).is_file():
                    errors.append(
                        f"Raw source from manifest not found on disk: {raw_path}."
                    )
            # len > 1 (multi-cam): leave raw_path null; the skill picks/asks.

    # 2. Locate the Descript export under rough-cuts/ (it may sit in a subfolder).
    if not REMAP_SCRIPT.is_file():
        errors.append(
            f"Remap script missing at {REMAP_SCRIPT}. "
            f"Expected connectors/buttercut-export/remap-descript-to-raw.py."
        )

    if not rough_cuts_dir.is_dir():
        errors.append(
            f"rough-cuts/ folder missing at {rough_cuts_dir}. "
            f"Export the Descript timeline as DaVinci Resolve XML into here first."
        )
    else:
        for xml in sorted(rough_cuts_dir.rglob("*.xml")):
            if xml.resolve() == output_path.resolve():
                continue  # skip a prior remap output
            if is_descript_export(xml):
                descript_candidates.append(str(xml))
        if not descript_candidates:
            errors.append(
                f"No Descript-exported xml found under {rough_cuts_dir}. "
                f"Export the polished timeline from Descript as DaVinci Resolve XML "
                f"into the rough-cuts/ folder, then re-run."
            )
        elif len(descript_candidates) == 1:
            descript_xml = descript_candidates[0]
        # len > 1: leave descript_xml null; the skill asks which one.

    output_exists = output_path.is_file()

    if errors:
        status = "failed"
    elif output_exists:
        status = "rerun_prompt"
    else:
        status = "ready"

    payload = {
        "slug": slug,
        "docs_folder": str(docs_folder),
        "obs_folder": str(obs_folder),
        "manifest_path": str(manifest_path),
        "rough_cuts_dir": str(rough_cuts_dir),
        "raw_path": raw_path,
        "raw_candidates": raw_candidates,
        "descript_xml": descript_xml,
        "descript_candidates": descript_candidates,
        "output_path": str(output_path),
        "remap_script": str(REMAP_SCRIPT),
        "output_exists": output_exists,
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
