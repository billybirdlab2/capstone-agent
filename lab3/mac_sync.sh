#!/usr/bin/env bash
# Run on your MAC (the only machine with git). Moves files to and from Helios with scp.
#
#   bash lab3/mac_sync.sh send  <helios-host> [path/to/ME295_Lab3_Three_Demo_Options.zip]
#   bash lab3/mac_sync.sh fetch <helios-host>
#
# <helios-host> is whatever you normally type after `ssh` (e.g. user@helios.example.edu,
# or an alias from ~/.ssh/config).
#   send : copies lab3/ (scripts + prompt) and the zip to ~/lab3_transfer/ on Helios.
#   fetch: copies ~/lab3_bundle.tar.gz back and unpacks it into reports/lab3/ here.
set -euo pipefail

STEP="${1:-}"; HOST="${2:-}"
[ -n "$STEP" ] && [ -n "$HOST" ] || { sed -n '2,12p' "$0"; exit 1; }
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "$STEP" in
send)
  ZIP="${3:-$HOME/Downloads/ME295_Lab3_Three_Demo_Options.zip}"
  [ -f "$ZIP" ] || { echo "zip not found: $ZIP" >&2; exit 1; }
  git -C "$REPO" rev-parse HEAD > "$REPO/lab3/REPO_COMMIT.txt"
  ssh "$HOST" 'mkdir -p ~/lab3_transfer'
  scp "$REPO"/lab3/helios_option_a.sh "$REPO"/lab3/HELIOS_AGENT_PROMPT.md \
      "$REPO"/lab3/REPORT_STEPS.md "$REPO"/lab3/REPO_COMMIT.txt "$ZIP" "$HOST":~/lab3_transfer/
  rm -f "$REPO/lab3/REPO_COMMIT.txt"
  echo "Sent. On Helios:  cd ~/lab3_transfer && claude   (then paste the prompt)"
  ;;
fetch)
  STAMP=$(date -u +%Y%m%dT%H%M%SZ)
  LOCAL="$REPO/reports/lab3/.incoming_$STAMP.tar.gz"
  mkdir -p "$REPO/reports/lab3"
  scp "$HOST":~/lab3_bundle.tar.gz "$LOCAL"
  echo "sha256: $(shasum -a 256 "$LOCAL" | cut -d' ' -f1)  (compare with the value Helios printed)"
  tar -tzf "$LOCAL"
  tar -xzf "$LOCAL" -C "$REPO/reports/lab3"
  rm -f "$LOCAL"
  echo; git -C "$REPO" status --short reports/lab3
  ;;
*) sed -n '2,12p' "$0"; exit 1 ;;
esac
