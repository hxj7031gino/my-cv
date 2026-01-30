#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$HOME/Desktop/github/my-cv}"
PROJ="$ROOT/works/projects/p-2023-001-east-london-socialist-value"
IMG="$PROJ/img"

HERO="$IMG/hero.jpg"
GRID_DIR="$IMG/grid-4x3"
FEATURE_DIR="$IMG/feature"
PORTRAIT_DIR="$IMG/portrait"

fail() { echo "❌ $*"; exit 1; }
warn() { echo "⚠️  $*"; }
ok() { echo "✅ $*"; }

echo "Project: $PROJ"

[[ -d "$PROJ" ]] || fail "Missing project folder: $PROJ"
[[ -d "$IMG" ]] || fail "Missing img folder: $IMG"

[[ -f "$HERO" ]] || fail "Missing hero: $HERO"
ok "Found hero.jpg"

[[ -d "$GRID_DIR" ]] || fail "Missing folder: $GRID_DIR"
[[ -d "$FEATURE_DIR" ]] || fail "Missing folder: $FEATURE_DIR"
[[ -d "$PORTRAIT_DIR" ]] || fail "Missing folder: $PORTRAIT_DIR"
ok "Found folders: grid-4x3, feature, portrait"

list_imgs() { find "$1" -maxdepth 1 -type f ! -name ".DS_Store" -print | sort; }

check_lower_jpg() {
  local dir="$1" label="$2" regex="$3" expected_count="${4:-}"

  local files
  files="$(list_imgs "$dir" || true)"
  [[ -n "$files" ]] || fail "$label: no files found in $dir"

  local bad_ext=0 bad_name=0
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    local base
    base="$(basename "$f")"
    if [[ ! "$base" =~ \.jpg$ ]]; then
      bad_ext=1
      echo "  - $label bad extension: $base"
    fi
    if [[ ! "$base" =~ $regex ]]; then
      bad_name=1
      echo "  - $label bad name: $base (expected pattern: $regex)"
    fi
  done <<< "$files"

  [[ $bad_ext -eq 0 ]] || fail "$label: found non-lowercase .jpg extension(s)"
  [[ $bad_name -eq 0 ]] || fail "$label: found filename(s) not matching expected pattern"

  local count
  count="$(echo "$files" | sed '/^$/d' | wc -l | tr -d ' ')"
  if [[ -n "${expected_count:-}" ]]; then
    [[ "$count" == "$expected_count" ]] || fail "$label: expected $expected_count files, found $count"
  fi
  ok "$label: $count file(s) OK"
}

check_lower_jpg "$GRID_DIR" "GRID" '^grid-(0[1-9]|1[0-2])\.jpg$' "12"
check_lower_jpg "$FEATURE_DIR" "FEATURE" '^feature-[0-9]{2}\.jpg$'
check_lower_jpg "$PORTRAIT_DIR" "PORTRAIT" '^portrait-[0-9]{2}\.jpg$'

UPPER="$(find "$IMG" -maxdepth 2 -type f \( -iname "*.JPG" -o -iname "*.PNG" -o -iname "*.JPEG" \) ! -name ".DS_Store" -print || true)"
if [[ -n "${UPPER:-}" ]]; then
  warn "Found non-lowercase / non-jpg files under img/ (may break on hosting):"
  echo "$UPPER"
else
  ok "No stray uppercase/non-jpg files under img/"
fi

echo "✅ Verification complete."
