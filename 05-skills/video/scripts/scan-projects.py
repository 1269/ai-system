#!/usr/bin/env python3
"""Scan video project folders and report production phase.

Read-only. Walks both the Documents working-files tree and the Obsidian
meta-docs tree, infers each video's phase from which files exist, and prints
a markdown table.

Usage:
    scan-projects.py                # list all videos
    scan-projects.py <slug>         # detailed breakdown for one video
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

WORKING_ROOT = Path("/Users/jashia/Documents/1_Projects/videos")
META_ROOT = Path(
    "/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/"
    "2 Systems/content-production/projects"
)


@dataclass
class VideoState:
    slug: str
    working_dir: Path
    meta_dir: Path

    raw_files: list[Path]
    transcript_files: list[Path]
    rough_cut_files: list[Path]
    final_files: list[Path]

    has_script: bool
    has_task_list: bool
    has_brief: bool
    has_selects_manifest: bool
    has_retrospective: bool

    @property
    def has_intake_doc(self) -> bool:
        return self.has_script or self.has_task_list or self.has_brief

    @property
    def phase(self) -> tuple[str, str]:
        """Return (phase, next_action) by walking the pipeline backwards."""
        if self.has_retrospective:
            return ("done", "(none)")
        if self.final_files:
            return ("ready for upload", "/video upload")
        if self.rough_cut_files:
            return ("in finishing", "open in DaVinci")
        if self.has_selects_manifest:
            return ("ready for polish", "/video polish")
        if self.transcript_files:
            return ("ready for selects", "/associate-producer")
        if self.raw_files:
            return ("needs transcript", "run transcribe")
        if self.has_intake_doc:
            return ("pre-production", "record")
        return ("orphaned", "bootstrap or archive")


def list_files(dir_path: Path) -> list[Path]:
    if not dir_path.is_dir():
        return []
    return sorted(
        p for p in dir_path.iterdir()
        if p.is_file() and not p.name.startswith(".")
    )


def load_state(slug: str) -> VideoState:
    working_dir = WORKING_ROOT / slug
    meta_dir = META_ROOT / slug
    producer_dir = meta_dir / "producer"

    return VideoState(
        slug=slug,
        working_dir=working_dir,
        meta_dir=meta_dir,
        raw_files=list_files(working_dir / "raw"),
        transcript_files=list_files(working_dir / "transcripts"),
        rough_cut_files=list_files(working_dir / "rough-cuts"),
        final_files=list_files(working_dir / "finals"),
        has_script=(meta_dir / "script.md").is_file(),
        has_task_list=(meta_dir / "task-list.md").is_file(),
        has_brief=(meta_dir / "brief.md").is_file(),
        has_selects_manifest=(producer_dir / "selects-manifest.json").is_file(),
        has_retrospective=(meta_dir / "retrospective.md").is_file(),
    )


def discover_slugs() -> list[str]:
    slugs: set[str] = set()
    for root in (WORKING_ROOT, META_ROOT):
        if not root.is_dir():
            continue
        for entry in root.iterdir():
            if entry.is_dir() and entry.name.startswith("video"):
                slugs.add(entry.name)
    return sorted(slugs)


def render_table(states: list[VideoState]) -> str:
    rows = ["| Slug | Phase | Next action |", "|------|-------|-------------|"]
    for s in states:
        phase, next_action = s.phase
        rows.append(f"| {s.slug} | {phase} | {next_action} |")
    return "\n".join(rows)


def render_detail(state: VideoState) -> str:
    phase, next_action = state.phase

    def check(label: str, present: bool, detail: str = "") -> str:
        mark = "x" if present else " "
        suffix = f" — {detail}" if detail and present else ""
        return f"- [{mark}] {label}{suffix}"

    def file_summary(files: list[Path]) -> str:
        if not files:
            return ""
        if len(files) <= 3:
            return ", ".join(f.name for f in files)
        return f"{len(files)} files (e.g. {files[0].name})"

    lines = [
        f"# {state.slug}",
        "",
        f"**Phase:** {phase}",
        f"**Next action:** {next_action}",
        "",
        f"**Working dir:** `{state.working_dir}`",
        f"**Meta dir:** `{state.meta_dir}`",
        "",
        "## Meta docs (Obsidian)",
        check("script.md", state.has_script),
        check("task-list.md", state.has_task_list),
        check("brief.md", state.has_brief),
        check("producer/selects-manifest.json", state.has_selects_manifest),
        check("retrospective.md", state.has_retrospective),
        "",
        "## Working files (Documents)",
        check("raw/", bool(state.raw_files), file_summary(state.raw_files)),
        check(
            "transcripts/",
            bool(state.transcript_files),
            file_summary(state.transcript_files),
        ),
        check(
            "rough-cuts/",
            bool(state.rough_cut_files),
            file_summary(state.rough_cut_files),
        ),
        check("finals/", bool(state.final_files), file_summary(state.final_files)),
    ]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        slug = argv[1]
        if not (WORKING_ROOT / slug).is_dir() and not (META_ROOT / slug).is_dir():
            print(f"No project folder found for slug '{slug}'.")
            print(f"Searched:\n  {WORKING_ROOT / slug}\n  {META_ROOT / slug}")
            return 1
        print(render_detail(load_state(slug)))
        return 0

    slugs = discover_slugs()
    if not slugs:
        print("No video project folders found.")
        return 0
    states = [load_state(s) for s in slugs]
    print(render_table(states))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
