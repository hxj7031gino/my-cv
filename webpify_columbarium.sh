set -euo pipefail

MODE="dry-run"
ROOT="works/projects/p-2022-001-columbarium-of-the-days/img"
QUALITY="80"
MAX="1600"
DO_BACKUP="yes"
BACKUP_DIR="_img_backup_$(date +%Y%m%d-%H%M%S)"

while [ $# -gt 0 ]; do
  case "$1" in
    --apply) MODE="apply"; shift ;;
    --root) ROOT="${2:-}"; shift 2 ;;
    --quality) QUALITY="${2:-}"; shift 2 ;;
    --max) MAX="${2:-}"; shift 2 ;;
    --no-backup) DO_BACKUP="no"; shift ;;
    *) echo "Unknown arg: $1"; exit 2 ;;
  esac
done

command -v cwebp >/dev/null 2>&1 || { echo "Missing: cwebp"; echo "Install: brew install webp"; exit 1; }

printf 'Mode: %s\nRoot: %s\nQual: %s\nMax : %s\nBackup: %s\n' "$MODE" "$ROOT" "$QUALITY" "$MAX" "$DO_BACKUP"

find "$ROOT" -type f \( -iname '*.jpg' -o -iname '*.jpeg' \) -print0 | while IFS= read -r -d '' f; do
  out="${f%.*}.webp"

  if [ "$MODE" = "apply" ] && [ "$DO_BACKUP" = "yes" ]; then
    mkdir -p "$BACKUP_DIR/$(dirname "$f")"
    cp -p "$f" "$BACKUP_DIR/$f"
  fi

  w="$(sips -g pixelWidth "$f" 2>/dev/null | awk '/pixelWidth/ {print $2}')"
  h="$(sips -g pixelHeight "$f" 2>/dev/null | awk '/pixelHeight/ {print $2}')"
  if [ -z "${w:-}" ] || [ -z "${h:-}" ]; then
    echo "Skip (cannot read size): $f"
    continue
  fi

  new_w="$w"
  new_h="$h"
  if [ "$w" -ge "$h" ]; then
    if [ "$w" -gt "$MAX" ]; then
      new_w="$MAX"
      new_h=$(( h * MAX / w ))
      [ "$new_h" -lt 1 ] && new_h=1
    fi
  else
    if [ "$h" -gt "$MAX" ]; then
      new_h="$MAX"
      new_w=$(( w * MAX / h ))
      [ "$new_w" -lt 1 ] && new_w=1
    fi
  fi

  if [ "$MODE" = "dry-run" ]; then
    echo "[dry-run] cwebp -q $QUALITY -m 6 -resize $new_w $new_h \"$f\" -o \"$out\""
  else
    cwebp -q "$QUALITY" -m 6 -resize "$new_w" "$new_h" "$f" -o "$out" >/dev/null
  fi
done

echo "Done."
if [ "$MODE" = "apply" ] && [ "$DO_BACKUP" = "yes" ]; then
  echo "Backup folder: $BACKUP_DIR"
fi
