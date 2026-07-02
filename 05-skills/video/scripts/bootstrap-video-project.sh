#!/usr/bin/env bash
# bootstrap-video-project.sh
#
# Shared video-project bootstrap. Resolves the next videoNN slug and creates both
# folder trees (Documents working files + Obsidian meta docs). Called by /video new
# and by /story-development (script mode) so numbering and the folder layout live in
# exactly one place instead of being duplicated in two skills.
#
# Usage:
#   bootstrap-video-project.sh "<kebab-topic>"          # compute next NN, create folders
#   bootstrap-video-project.sh "video07-my-topic"        # explicit slug (user override)
#   bootstrap-video-project.sh "<topic>" --dry-run       # print the slug it WOULD create, make nothing
#   bootstrap-video-project.sh "<topic>" --json          # machine-readable output
#
# Typical flow for a caller: run with --dry-run first to get the resolved slug, show it
# to the user for confirmation, then run for real (or with the user's adjusted slug).
#
# Exit codes: 0 ok, 2 usage error, 3 slug collision (a folder for that slug already exists).

set -euo pipefail

DOCS_ROOT="/Users/jashia/Documents/1_Projects/videos"
META_ROOT="/Users/jashia/Documents/3_Resources/Obsidian/Second Brain/2 Systems/content-production/projects"

ARG=""
DRY_RUN=0
JSON=0

for a in "$@"; do
  case "$a" in
    --dry-run) DRY_RUN=1 ;;
    --json) JSON=1 ;;
    --*) echo "unknown flag: $a" >&2; exit 2 ;;
    *) if [ -z "$ARG" ]; then ARG="$a"; else echo "unexpected extra argument: $a" >&2; exit 2; fi ;;
  esac
done

if [ -z "$ARG" ]; then
  echo "usage: bootstrap-video-project.sh \"<kebab-topic or full slug>\" [--dry-run] [--json]" >&2
  exit 2
fi

# Lowercase, spaces/underscores to dashes, strip non [a-z0-9-], collapse and trim dashes.
slugify() {
  echo "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | tr ' _' '--' \
    | sed -E 's/[^a-z0-9-]//g; s/-+/-/g; s/^-+//; s/-+$//'
}

# Highest existing videoNN across BOTH trees, plus one, zero-padded. Scanning both trees
# prevents a collision when a project exists in only one of them.
next_nn() {
  local max=0 n d root
  for root in "$DOCS_ROOT" "$META_ROOT"; do
    [ -d "$root" ] || continue
    for d in "$root"/video[0-9][0-9]-*; do
      [ -e "$d" ] || continue
      n=$(basename "$d" | sed -E 's/^video([0-9]{2})-.*/\1/')
      n=$((10#$n))
      [ "$n" -gt "$max" ] && max=$n
    done
  done
  printf "%02d" $((max + 1))
}

if [[ "$ARG" =~ ^video[0-9]{2}- ]]; then
  SLUG="$ARG"
else
  KEBAB=$(slugify "$ARG")
  if [ -z "$KEBAB" ]; then
    echo "could not derive a slug from: $ARG" >&2
    exit 2
  fi
  SLUG="video$(next_nn)-$KEBAB"
fi

DOCS_DIR="$DOCS_ROOT/$SLUG"
META_DIR="$META_ROOT/$SLUG"

emit() {
  local created="$1"
  if [ "$JSON" -eq 1 ]; then
    printf '{"slug":"%s","docs_dir":"%s","meta_dir":"%s","created":%s}\n' \
      "$SLUG" "$DOCS_DIR" "$META_DIR" "$created"
  else
    echo "slug:     $SLUG"
    echo "docs_dir: $DOCS_DIR"
    echo "meta_dir: $META_DIR"
    if [ "$created" = "true" ]; then
      echo "status:   created"
    else
      echo "status:   dry-run (nothing created)"
    fi
  fi
}

if [ "$DRY_RUN" -eq 1 ]; then
  emit false
  exit 0
fi

# Refuse to clobber an existing project.
if [ -d "$DOCS_DIR" ] || [ -d "$META_DIR" ]; then
  echo "slug collision: $SLUG already exists (docs_dir or meta_dir present). Pick a different slug or work the existing project." >&2
  exit 3
fi

mkdir -p \
  "$DOCS_DIR/raw" \
  "$DOCS_DIR/transcripts" \
  "$DOCS_DIR/rough-cuts" \
  "$DOCS_DIR/finals" \
  "$META_DIR/producer" \
  "$META_DIR/recording-aids"

emit true
