#!/usr/bin/env bash
# Lab Report 3 — Option A (agent chooses a grounding pipeline) on Helios.
#
# Wraps the course-prep package ME295_Lab3_Three_Demo_Options.zip. The package itself
# is NOT committed to this repository; only the run evidence and provenance are.
#
# Usage (run from anywhere; each step is separate so a human/agent can stop between them):
#   bash lab3/helios_option_a.sh prep    /path/to/ME295_Lab3_Three_Demo_Options.zip
#   bash lab3/helios_option_a.sh inspect          # python3 route.py inspect R04
#   bash lab3/helios_option_a.sh run              # python3 run_demo.py route  (live Claude decisions)
#   bash lab3/helios_option_a.sh collect          # copy evidence + provenance into reports/lab3/
#
# Environment overrides:
#   LAB3_WORK  extraction directory (default: $HOME/ME295_Lab3_Work)
#   CASE       case to inspect      (default: R04)
set -euo pipefail

STEP="${1:-}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${LAB3_WORK:-$HOME/ME295_Lab3_Work}"
PKG="$WORK/lab3_demo"
LOGS="$WORK/helios_logs"
CASE="${CASE:-R04}"
mkdir -p "$LOGS"

die() { echo "ERROR: $*" >&2; exit 1; }
need_pkg() { [ -f "$PKG/route.py" ] && [ -f "$PKG/run_demo.py" ] || die "package not extracted at $PKG (run the prep step first)"; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi; }

case "$STEP" in
prep)
  ZIP="${2:-}"; [ -f "$ZIP" ] || die "give the path to ME295_Lab3_Three_Demo_Options.zip"
  command -v unzip >/dev/null || die "unzip not installed"
  python3 - <<'PY' || die "Python >= 3.9 required"
import sys; assert sys.version_info >= (3, 9), sys.version
PY
  command -v claude >/dev/null || die "claude CLI not on PATH (log in to Claude Code on Helios first)"
  mkdir -p "$WORK"
  unzip -n "$ZIP" -d "$WORK" >/dev/null   # -n: never overwrite an existing extraction
  need_pkg
  {
    echo "date_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "host: $(hostname)"
    echo "zip: $(basename "$ZIP")"
    echo "zip_sha256: $(sha "$ZIP" | cut -d' ' -f1)"
    echo "python: $(python3 --version 2>&1)"
    echo "claude: $(claude --version 2>&1)"
    echo "repo_commit: $(git -C "$REPO" rev-parse HEAD)"
  } | tee "$LOGS/provenance_prep.txt"
  echo; echo "Package files:"; (cd "$PKG" && find . -maxdepth 2 -type f | sort | head -100)
  (cd "$PKG" && find . -type f \( -name '*.py' -o -name '*.json' -o -name '*.html' -o -name '*.csv' \) -print0 \
     | sort -z | xargs -0 sha256sum 2>/dev/null || true) > "$LOGS/package_file_hashes.sha256"
  echo
  echo "NEXT: read route.py, run_demo.py and START_HERE.html (what is sent to Claude, where Gold lives,"
  echo "      what the checker computes) BEFORE running the 'inspect' and 'run' steps."
  ;;

inspect)
  need_pkg
  (cd "$PKG" && python3 route.py inspect "$CASE") 2>&1 | tee "$LOGS/inspect_${CASE}.txt"
  ;;

run)
  need_pkg
  [ ! -e "$PKG/evidence/route/comparison.json" ] || {
    echo "NOTE: $PKG/evidence/route already has a comparison.json from an earlier run."
    echo "      Archiving it to $LOGS/previous_route_$(date -u +%Y%m%dT%H%M%SZ) so the new run cannot be confused with it."
    mv "$PKG/evidence/route" "$LOGS/previous_route_$(date -u +%Y%m%dT%H%M%SZ)"
  }
  START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  (cd "$PKG" && python3 run_demo.py route) 2>&1 | tee "$LOGS/run_route_console.txt"
  echo "run_started_utc: $START"  >  "$LOGS/provenance_run.txt"
  echo "run_ended_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LOGS/provenance_run.txt"
  echo "claude: $(claude --version 2>&1)" >> "$LOGS/provenance_run.txt"
  ls -la "$PKG/evidence/route" | tee -a "$LOGS/provenance_run.txt"
  ;;

collect)
  need_pkg
  [ -d "$PKG/evidence/route" ] || die "no $PKG/evidence/route — run the 'run' step first"
  STAMP=$(date -u +%Y%m%dT%H%M%SZ)
  DEST="$REPO/reports/lab3/option_a_run_$STAMP"
  mkdir -p "$DEST"
  cp -R "$PKG/evidence/route/." "$DEST/evidence/"
  cp "$LOGS"/*.txt "$LOGS"/*.sha256 "$DEST/" 2>/dev/null || true
  (cd "$DEST" && find . -type f ! -name MANIFEST.sha256 -print0 | sort -z | xargs -0 sha256sum > MANIFEST.sha256)
  echo "Collected into ${DEST#$REPO/}:"; (cd "$DEST" && find . -type f | sort)
  echo
  echo "Before committing: confirm these files may go in the (private) course repo — they contain"
  echo "Dylan development-frame results. Do not commit the zip, the Gold annotations, or images you"
  echo "are not permitted to share."
  ;;

*)
  sed -n '2,16p' "$0"; exit 1 ;;
esac
