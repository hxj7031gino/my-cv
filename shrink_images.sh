#!/usr/bin/env bash
set -euo pipefail

MODE="dry-run"         # dry-run | apply
ROOT="works/projects/p-2022-001-columbarium-of-the-days/img"
MAX=1600               # max pixel (long edge)
QUALITY=80             # 0-100 (jpeg)
DO_BACKUP="yes"        # yes | no
BACKUP_DIR="_img_backup_$(date +%Y%m%d-%H%M%S)"

usage() {
  cat <<USAGE
Usage:
  bash ./shrink_images.sh [--apply] [--root PATH] [--max N] [--quality N] [--no-backup]

Examples:
  bash ./shrink_images.sh
  bash ./shrink_images.sh --apply
  bash ./shrink_images.sh --apply --max 1400 --quality 75
  bash ./shrink_images.sh --apply --root works/projects/p-2022-001-columbarium-of-the-days/img --no-backup
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) MODE="apply"; shift ;;
    --dry-run) MODE="dry-run"; shift ;;
    --root) ROOT="$2"; shift 2 ;;
    --max) MAX="$2"; shift 2 ;;
    --quality) QUALITY="$2"; shift 2 ;;
    --no-backup) DO_BACKUP="no"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ ! -d "$ROOT" ]]; then
  echo "ERROR: root folder not found: $ROOT"
  exit 1
fi

echo "Mode: $MODE"
echo "Root: $ROOT"
echo "Max : $MAX"
echo "Qual: $QUALITY"
echo "Backup: $DO_BACKUP"
echo

if [[ "$MODE" == "apply" && "$DO_BACKUP" == "yes" ]]; then
  mkdir -p "$BACKUP_DIR"
fi

# 用 find + while read，兼容 macOS bash 3.2（无 mapfile）
find "$ROOT" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) ! -name ".DS_Store" -print0 \
| while IFS= read -r -d '' f; do
    if [[ "$MODE" == "apply" && "$DO_BACKUP" == "yes" ]]; then
      mkdir -p "$BACKUP_DIR/$(dirname "$f")"
      cp -p "$f" "$BACKUP_DIR/$f"
    fi

    if [[ "$MODE" == "dry-run" ]]; then
      echo "[dry-run] sips -Z $MAX \"$f\" >/dev/null"
      echo "[dry-run] (if jpg) sips -s formatOptions $QUALITY \"$f\" >/dev/null"
      continue
    fi

    # Resize (long edge) - path/filename 不变
    sips -Z "$MAX" "$f" >/dev/null

    ext="${f##*.}"
    ext_lc="$(printf '%s' "$ext" | tr '[:upper:]' '[:lower:]')"
    if [[ "$ext_lc" == "jpg" || "$ext_lc" == "jpeg" ]]; then
      sips -s formatOptions "$QUALITY" "$f" >/dev/null
    fi
  done

echo
echo "Done."
if [[ "$MODE" == "apply" && "$DO_BACKUP" == "yes" ]]; then
  echo "Backup folder: $BACKUP_DIR"
fi
