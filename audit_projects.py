#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import csv
import re
from datetime import datetime

ROOT = Path(".").resolve()
PROJECTS_DIR = ROOT / "works" / "projects"
CSV_PATH = ROOT / "projects.csv"
REPORT_PATH = ROOT / "inbox" / "project_audit_report.txt"

IGNORE_DIRS = {"_template-project"}  # 模板不算项目

def read_csv_slugs(csv_path: Path) -> set[str]:
    slugs = set()
    if not csv_path.exists():
        return slugs
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = (row.get("project_slug") or "").strip()
            if slug:
                slugs.add(slug)
    return slugs

def list_project_folders(projects_dir: Path) -> list[Path]:
    if not projects_dir.exists():
        return []
    folders = []
    for p in sorted(projects_dir.iterdir()):
        if p.is_dir() and p.name not in IGNORE_DIRS and not p.name.startswith("."):
            folders.append(p)
    return folders

def slug_ok(slug: str) -> bool:
    # p-YYYY-NNN-slug
    return bool(re.fullmatch(r"p-\d{4}-\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*", slug))

def find_case_insensitive(path: Path, name: str) -> Path | None:
    """Return a file path under 'path' matching name case-insensitively, if any."""
    if not path.exists():
        return None
    target_lower = name.lower()
    for p in path.iterdir():
        if p.is_file() and p.name.lower() == target_lower:
            return p
    return None

def audit_one(project_dir: Path) -> dict:
    slug = project_dir.name
    img_dir = project_dir / "img"

    # Required files (case-sensitive expectation)
    index_html = project_dir / "index.html"
    thumb = img_dir / "thumb.jpg"
    hero = img_dir / "hero.jpg"

    # Case-insensitive matches (to catch Thumb.JPG etc.)
    thumb_ci = find_case_insensitive(img_dir, "thumb.jpg")
    hero_ci = find_case_insensitive(img_dir, "hero.jpg")
    hero_jpg_jpg = find_case_insensitive(img_dir, "hero.jpg.jpg")

    issues = []
    warnings = []

    if not slug_ok(slug):
        warnings.append(f"Slug not matching recommended pattern p-YYYY-NNN-slug: {slug}")

    if not index_html.exists():
        issues.append("Missing project page: index.html (expected works/projects/<slug>/index.html)")

    if not img_dir.exists():
        issues.append("Missing img/ folder")
    else:
        if thumb.exists():
            pass
        elif thumb_ci:
            warnings.append(f"thumb.jpg exists but with different casing: {thumb_ci.name} (recommend rename to thumb.jpg)")
        else:
            issues.append("Missing img/thumb.jpg")

        if hero.exists():
            pass
        elif hero_ci:
            warnings.append(f"hero.jpg exists but with different casing: {hero_ci.name} (recommend rename to hero.jpg)")
        else:
            # Special common mistake
            if hero_jpg_jpg:
                issues.append(f"Found {hero_jpg_jpg.name} but missing hero.jpg (rename hero.jpg.jpg -> hero.jpg)")
            else:
                issues.append("Missing img/hero.jpg")

        # Quick count of gallery images (01.jpg, 02.jpg... any extension)
        gallery = []
        if img_dir.exists():
            for p in img_dir.iterdir():
                if p.is_file() and re.fullmatch(r"\d{2,3}\.(jpg|jpeg|png|webp|JPG|JPEG|PNG|WEBP)", p.name):
                    gallery.append(p.name)
        gallery.sort()

        if len(gallery) == 0:
            warnings.append("No gallery images like 01.jpg/02.jpg found (optional but recommended)")
        else:
            # Check mixed numbering styles (e.g., 01 + 010)
            has_two = any(re.fullmatch(r"\d{2}\..+", n) for n in gallery)
            has_three = any(re.fullmatch(r"\d{3}\..+", n) for n in gallery)
            if has_two and has_three:
                warnings.append("Gallery numbering mixes 2-digit and 3-digit (e.g., 01.jpg and 010.jpg). Recommend unify.")

    return {
        "slug": slug,
        "issues": issues,
        "warnings": warnings,
    }

def main():
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"Project Audit Report - {ts}")
    lines.append(f"Root: {ROOT}")
    lines.append("")

    if not PROJECTS_DIR.exists():
        print("❌ works/projects not found.")
        return

    csv_slugs = read_csv_slugs(CSV_PATH)
    folders = list_project_folders(PROJECTS_DIR)
    folder_slugs = {p.name for p in folders}

    # CSV vs folder mismatch
    if CSV_PATH.exists():
        missing_folders = sorted(csv_slugs - folder_slugs)
        extra_folders = sorted(folder_slugs - csv_slugs)
        lines.append("CSV vs Folder Consistency")
        lines.append(f"- projects.csv slugs: {len(csv_slugs)}")
        lines.append(f"- folder slugs:     {len(folder_slugs)}")
        if missing_folders:
            lines.append(f"❌ In CSV but folder missing ({len(missing_folders)}):")
            for s in missing_folders:
                lines.append(f"  - {s}")
        else:
            lines.append("✅ All CSV slugs have folders.")
        if extra_folders:
            lines.append(f"⚠️ Folder exists but not in CSV ({len(extra_folders)}):")
            for s in extra_folders:
                lines.append(f"  - {s}")
        else:
            lines.append("✅ No extra folders outside CSV.")
        lines.append("")
    else:
        lines.append("⚠️ projects.csv not found (skipping CSV consistency check).")
        lines.append("")

    # Per-project checks
    total = 0
    bad = 0
    warn_count = 0

    lines.append("Per-project Checks")
    for p in folders:
        total += 1
        result = audit_one(p)
        issues = result["issues"]
        warnings = result["warnings"]

        status = "✅ OK"
        if issues:
            status = "❌ FAIL"
            bad += 1
        elif warnings:
            status = "⚠️ WARN"
            warn_count += 1

        lines.append(f"{status}  {result['slug']}")
        if issues:
            for it in issues:
                lines.append(f"   - ISSUE: {it}")
        if warnings:
            for wt in warnings:
                lines.append(f"   - WARN:  {wt}")
        lines.append("")

    lines.append("Summary")
    lines.append(f"- Total projects checked: {total}")
    lines.append(f"- FAIL (must fix):        {bad}")
    lines.append(f"- WARN (recommended):     {warn_count}")
    lines.append("")

    # Write report
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ Audit complete. Report saved to:\n{REPORT_PATH}")
    print("\nQuick summary:")
    print(f"Total: {total} | FAIL: {bad} | WARN: {warn_count}")

if __name__ == "__main__":
    main()
