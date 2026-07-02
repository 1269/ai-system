#!/usr/bin/env python3
"""
Lay MMSS-named motion-graphics assets onto a base edit timeline by generating a
full-stack FCP7 (xmeml) timeline that DaVinci Resolve can import.

The base timeline (the `/video remap` output, or the `/video selects` rough cut)
stays on V1 verbatim. Overlays and cards are appended on tracks above it, each
placed at the in-point encoded in its filename.

Naming contract: every asset filename starts with its in-point as MMSS (minutes
then seconds), e.g. `1216_punch_kung-fu.mov` -> 12:16. Start frame on the
timeline = round((mm*60 + ss) * fps), where fps is read from the base timeline.

Asset roles (by subfolder under --assets-dir):
  overlays/   alpha clips (ProRes 4444 .mov) -> packed onto overlay tracks above
              the face cam; a second/third track opens only when two overlap in
              time (otherwise they share one track).
  cards/      opaque full-frame cutaways (.mp4) -> placed on the top track(s).

Why import-XML instead of the scripting API: the free version of DaVinci Resolve
does not expose the scripting API (it is Studio-only), but every edition imports
timeline XML. See reference: DaVinci Resolve scripting is Studio-only.

Usage:
    python3 lay-in-graphics.py --base <base.xml> --assets-dir <assets/> --output <out.xml>
    python3 lay-in-graphics.py --base <base.xml> --assets-dir <assets/> --output <out.xml> --plan
        --plan prints the placement table and exits without writing the file.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(2)


def read_base_fps(root):
    """Read (timebase, ntsc, fps_exact) from the sequence rate of a parsed xmeml."""
    seq = root.find("sequence")
    if seq is None:
        die("base xml has no <sequence>")
    rate = seq.find("rate")
    if rate is None:
        rate = seq.find("media/video/format/samplecharacteristics/rate")
    if rate is None:
        die("could not find the sequence frame rate in the base xml")
    timebase = int(rate.findtext("timebase"))
    ntsc = (rate.findtext("ntsc") or "FALSE").strip().upper() == "TRUE"
    fps_exact = timebase * (1000.0 / 1001.0) if ntsc else float(timebase)
    return timebase, ntsc, fps_exact


def ffprobe_frames(ffprobe, path, fps_exact):
    """Return (frame_count, source_fps). Frame count prefers nb_frames, falls
    back to duration*fps."""
    out = subprocess.run(
        [ffprobe, "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate,nb_frames,duration",
         "-of", "json", path],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        die(f"ffprobe failed on {path}: {out.stderr.strip()}")
    st = (json.loads(out.stdout).get("streams") or [{}])[0]
    num, den = (st.get("r_frame_rate") or "0/1").split("/")
    src_fps = (float(num) / float(den)) if float(den) else 0.0
    nb = st.get("nb_frames")
    if nb and nb != "N/A":
        frames = int(nb)
    else:
        dur = float(st.get("duration") or 0)
        frames = round(dur * fps_exact)
    return frames, src_fps


def mmss_start_frame(name, fps_exact):
    """First 4 chars of the filename are MMSS -> start frame on the timeline."""
    mm, ss = int(name[0:2]), int(name[2:4])
    return round((mm * 60 + ss) * fps_exact)


def collect_assets(assets_dir):
    """Return [(role, name, path)] for overlays/ (.mov) and cards/ (.mp4/.mov)."""
    found = []
    for role, sub, exts in (("overlay", "overlays", (".mov",)),
                            ("card", "cards", (".mp4", ".mov"))):
        d = os.path.join(assets_dir, sub)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if fn.startswith(".") or not fn[:4].isdigit():
                continue
            if os.path.splitext(fn)[1].lower() in exts:
                found.append((role, fn, os.path.join(d, fn)))
    return found


def pack_tracks(clips):
    """Greedy interval packing: clips sorted by start, each placed on the lowest
    track whose previous clip has ended. Minimises track count; opens a new track
    only on genuine time-overlap."""
    tracks = []
    for c in sorted(clips, key=lambda x: x["start"]):
        for t in tracks:
            if t[-1]["end"] <= c["start"]:
                t.append(c)
                break
        else:
            tracks.append([c])
    return tracks


def rate_el(parent, timebase, ntsc):
    r = ET.SubElement(parent, "rate")
    ET.SubElement(r, "timebase").text = str(timebase)
    ET.SubElement(r, "ntsc").text = "TRUE" if ntsc else "FALSE"


def make_clipitem(cid, fid, clip, timebase, ntsc):
    ci = ET.Element("clipitem", id=cid)
    ET.SubElement(ci, "name").text = clip["name"]
    ET.SubElement(ci, "enabled").text = "TRUE"
    ET.SubElement(ci, "duration").text = str(clip["frames"])
    rate_el(ci, timebase, ntsc)
    ET.SubElement(ci, "start").text = str(clip["start"])
    ET.SubElement(ci, "end").text = str(clip["end"])
    ET.SubElement(ci, "in").text = "0"
    ET.SubElement(ci, "out").text = str(clip["frames"])
    f = ET.SubElement(ci, "file", id=fid)
    ET.SubElement(f, "name").text = clip["name"]
    ET.SubElement(f, "pathurl").text = "file://" + urllib.parse.quote(clip["path"])
    rate_el(f, timebase, ntsc)
    ET.SubElement(f, "duration").text = str(clip["frames"])
    media = ET.SubElement(f, "media")
    vid = ET.SubElement(media, "video")
    sc = ET.SubElement(vid, "samplecharacteristics")
    ET.SubElement(sc, "width").text = "1920"
    ET.SubElement(sc, "height").text = "1080"
    rate_el(sc, timebase, ntsc)
    return ci


def fmt_tc(frame, fps_int):
    s, ff = divmod(int(frame), fps_int)
    mm, ss = divmod(s, 60)
    return f"{mm:02d}:{ss:02d}:{ff:02d}"


def main():
    ap = argparse.ArgumentParser(description="Lay MMSS graphics onto a base edit timeline (xmeml).")
    ap.add_argument("--base", required=True, help="Base timeline xml (remap or selects output).")
    ap.add_argument("--assets-dir", required=True, help="assets/ folder with overlays/ and cards/.")
    ap.add_argument("--output", required=True, help="Path to write the full-stack xml.")
    ap.add_argument("--plan", action="store_true", help="Print the placement table without writing.")
    args = ap.parse_args()

    if not os.path.isfile(args.base):
        die(f"base xml not found: {args.base}")
    if not os.path.isdir(args.assets_dir):
        die(f"assets dir not found: {args.assets_dir}")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        die("ffprobe not on PATH (brew install ffmpeg)")

    tree = ET.parse(args.base)
    root = tree.getroot()
    timebase, ntsc, fps_exact = read_base_fps(root)
    fps_int = int(round(fps_exact))

    assets = collect_assets(args.assets_dir)
    if not assets:
        die(f"no MMSS-named assets under {args.assets_dir}/overlays or /cards")

    overlays, cards, warnings = [], [], []
    for role, name, path in assets:
        frames, src_fps = ffprobe_frames(ffprobe, path, fps_exact)
        if abs(src_fps - fps_exact) > 0.05:
            warnings.append(f"{name}: source {src_fps:g}fps != timeline {fps_exact:g}fps")
        start = mmss_start_frame(name, fps_exact)
        clip = {"role": role, "name": name, "path": path,
                "frames": frames, "start": start, "end": start + frames}
        (overlays if role == "overlay" else cards).append(clip)

    overlay_tracks = pack_tracks(overlays)   # lowest tracks, above face cam
    card_tracks = pack_tracks(cards)         # on top
    new_tracks = overlay_tracks + card_tracks

    # Report ----------------------------------------------------------------
    video = root.find("sequence/media/video")
    base_track_count = len(video.findall("track")) if video is not None else 1
    print(f"Base timeline : {args.base}")
    print(f"FPS           : {fps_exact:g} ({'NDF' if not ntsc else 'DF/NTSC'}); base video tracks: {base_track_count}")
    print(f"Assets        : {len(overlays)} overlays, {len(cards)} cards")
    total_new = len(overlay_tracks) + len(card_tracks)
    print(f"New tracks    : {len(overlay_tracks)} overlay + {len(card_tracks)} card "
          f"-> V{base_track_count+1}..V{base_track_count+total_new}")
    for i, trk in enumerate(new_tracks):
        vidx = base_track_count + 1 + i
        kind = "overlay" if trk[0]["role"] == "overlay" else "card"
        print(f"\n  V{vidx} ({kind}):")
        for c in sorted(trk, key=lambda x: x["start"]):
            print(f"    {fmt_tc(c['start'], fps_int):>9}  {c['name']:<44} "
                  f"{c['frames']:>4}f  end {fmt_tc(c['end'], fps_int)}")
    if warnings:
        print("\nFPS warnings (placement length may drift):")
        for w in warnings:
            print(f"  - {w}")

    if args.plan:
        print("\n--plan: nothing written.")
        return 0

    # Build + write ---------------------------------------------------------
    if video is None:
        die("base xml has no sequence/media/video to append tracks to")
    n = 0
    for trk in new_tracks:
        track_el = ET.SubElement(video, "track")
        for c in sorted(trk, key=lambda x: x["start"]):
            n += 1
            track_el.append(make_clipitem(f"clip-g{n:02d}", f"file-g{n:02d}", c, timebase, ntsc))
    tree.write(args.output, encoding="utf-8", xml_declaration=True)

    # Validate the file we wrote -------------------------------------------
    chk = ET.parse(args.output).find("sequence/media/video")
    tracks = chk.findall("track")
    total_clips = sum(len(t.findall("clipitem")) for t in tracks)
    placed = total_clips - sum(len(t.findall("clipitem")) for t in tracks[:base_track_count])
    print(f"\nWrote {args.output}")
    print(f"  video tracks: {len(tracks)} (base {base_track_count} + {len(new_tracks)} added)")
    print(f"  graphics placed: {placed}/{len(assets)}   total clipitems: {total_clips}")
    return 0 if placed == len(assets) else 1


if __name__ == "__main__":
    sys.exit(main())
