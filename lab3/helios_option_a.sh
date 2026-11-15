#!/usr/bin/env bash
# Lab Report 3 — Option A (agent chooses a grounding pipeline), run on Helios.
# Helios has NO git access: this script needs no repository. Your Mac sends this
# folder + the zip over (lab3/mac_sync.sh send), Helios runs the steps below, and
# the Mac pulls the finished bundle back (lab3/mac_sync.sh fetch) and commits it.
#
# Steps (run separately so a human/agent can stop between them):
#   bash helios_option_a.sh prep    ~/lab3_transfer/ME295_Lab3_Three_Demo_Options.zip
#   bash helios_option_a.sh inspect           # python3 route.py inspect R04
#   bash helios_option_a.sh run               # python3 run_demo.py route (live Claude decisions)
#                                             #   refuses to start unless $OUT/PROTOCOL.md exists
#   bash helios_option_a.sh collect           # copy evidence + logs into $OUT/option_a_run_<stamp>
#   bash helios_option_a.sh bundle            # tar $OUT into ~/lab3_bundle.tar.gz for the Mac
#
# Environment overrides:
#   LAB3_WORK  extraction directory   (default: $HOME/ME295_Lab3_Work)
#   LAB3_OUT   files headed for repo  (default: $HOME/lab3_out; mirrors reports/lab3/ in the repo)
#   CASE       case to inspect        (default: R04)
set -euo pipefail

STEP="${1:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK="${LAB3_WORK:-$HOME/ME295_Lab3_Work}"
OUT="${LAB3_OUT:-$HOME/lab3_out}"
PKG="$WORK/lab3_demo"
LOGS="$WORK/helios_logs"
CASE="${CASE:-R04}"
BUNDLE="$HOME/lab3_bundle.tar.gz"
mkdir -p "$LOGS" "$OUT"

die() { echo "ERROR: $*" >&2; exit 1; }
need_pkg() { [ -f "$PKG/route.py" ] && [ -f "$PKG/run_demo.py" ] || die "package not extracted at $PKG (run the prep step first)"; }
sha() { if command -v sha256sum >/dev/null; then sha256sum "$@"; else shasum -a 256 "$@"; fi; }
utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }

case "$STEP" in
prep)
  ZIP="${2:-}"; [ -f "$ZIP" ] || die "give the path to ME295_Lab3_Three_Demo_Options.zip"
  command -v unzip >/dev/null || die "unzip not installed (alternative: python3 -m zipfile -e ZIP $WORK)"
  python3 -c 'import sys; assert sys.version_info >= (3, 9), sys.version' || die "Python >= 3.9 required"
  command -v claude >/dev/null || die "claude CLI not on PATH (log in to Claude Code on Helios first)"
  mkdir -p "$WORK"
  unzip -n "$ZIP" -d "$WORK" >/dev/null   # -n: never overwrite an existing extraction
  need_pkg
  {
    echo "date_utc: $(utc)"
    echo "host: $(hostname)"
    echo "zip: $(basename "$ZIP")"
    echo "zip_sha256: $(sha "$ZIP" | cut -d' ' -f1)"
    echo "python: $(python3 --version 2>&1)"
    echo "claude: $(claude --version 2>&1)"
    [ -f "$HERE/REPO_COMMIT.txt" ] && echo "repo_commit_on_mac: $(cat "$HERE/REPO_COMMIT.txt")"
  } | tee "$LOGS/provenance_prep.txt"
  echo; echo "Package files:"; (cd "$PKG" && find . -maxdepth 2 -type f | sort | head -100)
  (cd "$PKG" && find . -type f \( -name '*.py' -o -name '*.json' -o -name '*.html' -o -name '*.csv' \) \
     | sort | while read -r f; do sha "$f"; done) > "$LOGS/package_file_hashes.sha256"
  echo
  echo "NEXT: read route.py, run_demo.py and START_HERE.html BEFORE running 'inspect' and 'run'."
  ;;

inspect)
  need_pkg
  (cd "$PKG" && python3 route.py inspect "$CASE") 2>&1 | tee "$LOGS/inspect_${CASE}.txt"
  ;;

run)
  need_pkg
  [ -s "$OUT/PROTOCOL.md" ] || die "write $OUT/PROTOCOL.md (the frozen protocol) before the live run"
  if [ -e "$PKG/evidence/route" ]; then
    PREV="$LOGS/previous_route_$(date -u +%Y%m%dT%H%M%SZ)"
    echo "NOTE: archiving earlier $PKG/evidence/route to $PREV so it cannot be confused with this run."
    mv "$PKG/evidence/route" "$PREV"
  fi
  {
    echo "protocol_sha256: $(sha "$OUT/PROTOCOL.md" | cut -d' ' -f1)"
    echo "protocol_mtime_utc: $(date -u -r "$OUT/PROTOCOL.md" +%Y-%m-%dT%H:%M:%SZ)"
    echo "run_started_utc: $(utc)"
    echo "claude: $(claude --version 2>&1)"
  } > "$LOGS/provenance_run.txt"
  (cd "$PKG" && python3 run_demo.py route) 2>&1 | tee "$LOGS/run_route_console.txt"
  echo "run_ended_utc: $(utc)" >> "$LOGS/provenance_run.txt"
  ls -la "$PKG/evidence/route" | tee -a "$LOGS/provenance_run.txt"
  ;;

collect)
  need_pkg
  [ -d "$PKG/evidence/route" ] || die "no $PKG/evidence/route — run the 'run' step first"
  DEST="$OUT/option_a_run_$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "$DEST/evidence"
  cp -R "$PKG/evidence/route/." "$DEST/evidence/"
  cp "$LOGS"/*.txt "$LOGS"/*.sha256 "$DEST/" 2>/dev/null || true
  (cd "$DEST" && find . -type f ! -name MANIFEST.sha256 | sort | while read -r f; do sha "$f"; done > MANIFEST.sha256)
  echo "Collected into $DEST:"; (cd "$DEST" && find . -type f | sort)
  ;;

bundle)
  ls "$OUT"/option_a_run_* >/dev/null 2>&1 || die "nothing collected yet in $OUT"
  # Refuse to ship the package zip, Gold annotations or images by accident.
  BAD=$(find "$OUT" -type f \( -iname '*.zip' -o -iname '*gold*' -o -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) | head -20)
  if [ -n "$BAD" ] && [ "${ALLOW_MEDIA:-0}" != 1 ]; then
    echo "These files look like data you may not be allowed to commit:"; echo "$BAD"
    die "remove them, or re-run with ALLOW_MEDIA=1 if you have confirmed they may be shared"
  fi
  tar -czf "$BUNDLE" -C "$OUT" .
  echo "bundle: $BUNDLE  sha256: $(sha "$BUNDLE" | cut -d' ' -f1)"
  tar -tzf "$BUNDLE"
  ;;

*)
  sed -n '2,20p' "$0"; exit 1 ;;
esac
