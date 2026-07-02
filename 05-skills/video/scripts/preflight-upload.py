#!/usr/bin/env python3
"""
Pre-flight checks for `/video upload <slug>`.

Verifies the video is in a state where it can be packaged and pushed to YouTube.
Reports state as JSON on stdout and exits 0 (ready), 1 (rerun_prompt), or
2 (failed check). Same exit-code contract as preflight-selects.py.

Checks:
  1. Working folder + finals/ exist.
  2. finals/ contains EXACTLY ONE .mp4 (the polished final). 0 = fail, 2+ =
     fail with a list of candidates so the wrapper can ask which.
  3. Obsidian meta folder exists and has script.md or task-list.md.
  4. A final transcript exists. Looks for:
       - transcripts/<final-stem>.json
       - transcripts/final.json
       - any single .json under transcripts/
     in that order of preference.
  5. YouTube OAuth token cached at ~/.youtube_cli/token.json (set by
     connectors/youtube/auth.py). If missing, fail with the auth command.
  6. If upload-metadata.md already exists in producer/, set status=rerun_prompt
     so the wrapper can confirm before overwriting.

Usage:
    python3 preflight-upload.py <slug>
"""
import json
import sys
from pathlib import Path

DOCS_ROOT = Path("/Users/jashia/Documents/1_Projects/videos")
OBS_ROOT = Path(
    "/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects"
)
PLAN_FILES = ("script.md", "task-list.md", "brief.md")
TOKEN_PATH = Path.home() / ".youtube_cli" / "token.json"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: preflight-upload.py <slug>", file=sys.stderr)
        return 2

    slug = sys.argv[1]
    docs_folder = DOCS_ROOT / slug
    obs_folder = OBS_ROOT / slug
    finals_dir = docs_folder / "finals"
    transcripts_dir = docs_folder / "transcripts"
    producer_dir = obs_folder / "producer"
    metadata_path = producer_dir / "upload-metadata.md"
    retrospective_path = obs_folder / "retrospective.md"

    errors: list[str] = []

    # 1. Working folder
    if not docs_folder.is_dir():
        errors.append(
            f"Working folder missing: {docs_folder}. "
            f"Run /video new or check the slug spelling."
        )

    # 2. finals/ + exactly one mp4
    final_mp4: Path | None = None
    final_candidates: list[str] = []
    if not finals_dir.is_dir():
        errors.append(
            f"finals/ folder missing at {finals_dir}. "
            f"Export the polished final from DaVinci first."
        )
    else:
        mp4s = sorted(p for p in finals_dir.iterdir() if p.is_file() and p.suffix.lower() == ".mp4")
        final_candidates = [str(p) for p in mp4s]
        if len(mp4s) == 0:
            errors.append(
                f"No .mp4 in {finals_dir}. Drop the polished final there before /video upload."
            )
        elif len(mp4s) == 1:
            final_mp4 = mp4s[0]
        else:
            errors.append(
                f"Found {len(mp4s)} .mp4 files in {finals_dir}. "
                f"There should be exactly one. Pick which is the publish target."
            )

    # 3. Obsidian meta folder + a plan file
    plan_file: Path | None = None
    if not obs_folder.is_dir():
        errors.append(
            f"Obsidian meta folder missing: {obs_folder}."
        )
    else:
        plan_file = next(
            (obs_folder / name for name in PLAN_FILES if (obs_folder / name).is_file()),
            None,
        )
        if plan_file is None:
            errors.append(
                f"No script.md, task-list.md, or brief.md in {obs_folder}. "
                f"The AI metadata draft needs source content to read from."
            )

    # 4. Final transcript
    transcript_path: Path | None = None
    if final_mp4 and transcripts_dir.is_dir():
        candidates = [
            transcripts_dir / f"{final_mp4.stem}.json",
            transcripts_dir / "final.json",
        ]
        for c in candidates:
            if c.is_file():
                transcript_path = c
                break
        if transcript_path is None:
            json_files = sorted(p for p in transcripts_dir.iterdir() if p.suffix.lower() == ".json")
            if len(json_files) == 1:
                transcript_path = json_files[0]
            elif len(json_files) > 1:
                errors.append(
                    f"Multiple transcripts in {transcripts_dir} and none match the final stem "
                    f"'{final_mp4.stem}.json' or 'final.json'. Rename the intended one."
                )
            else:
                errors.append(
                    f"No transcript JSON in {transcripts_dir}. "
                    f"Transcribe the final first: /Users/jashia/Documents/1_Projects/ai-system/connectors/speech-to-text/venv/bin/python3 /Users/jashia/Documents/1_Projects/ai-system/connectors/speech-to-text/transcribe_video.py {final_mp4}"
                )
    elif final_mp4 and not transcripts_dir.is_dir():
        errors.append(
            f"transcripts/ missing at {transcripts_dir}. "
            f"Transcribe the final mp4 first."
        )

    # 5. OAuth token
    if not TOKEN_PATH.is_file():
        errors.append(
            f"YouTube OAuth token not found at {TOKEN_PATH}. "
            f"Run: uv run /Users/jashia/Documents/1_Projects/ai-system/connectors/youtube/youtube_client.py auth"
        )

    # Status
    metadata_exists = metadata_path.is_file()
    if errors:
        status = "failed"
    elif metadata_exists:
        status = "rerun_prompt"
    else:
        status = "ready"

    payload = {
        "slug": slug,
        "docs_folder": str(docs_folder),
        "obs_folder": str(obs_folder),
        "finals_dir": str(finals_dir),
        "transcripts_dir": str(transcripts_dir),
        "producer_dir": str(producer_dir),
        "final_mp4": str(final_mp4) if final_mp4 else None,
        "final_candidates": final_candidates,
        "plan_file": str(plan_file) if plan_file else None,
        "transcript_path": str(transcript_path) if transcript_path else None,
        "metadata_path": str(metadata_path),
        "metadata_exists": metadata_exists,
        "retrospective_path": str(retrospective_path),
        "token_path": str(TOKEN_PATH),
        "token_exists": TOKEN_PATH.is_file(),
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
