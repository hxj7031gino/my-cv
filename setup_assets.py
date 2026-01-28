#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import zipfile
from pathlib import Path
import shutil

MAC_GARBAGE_NAMES = {".DS_Store"}
MAC_GARBAGE_PREFIXES = ("._",)

def unzip_images(zip_path: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    # Many zips contain a top-level "images/" folder
    # Return the folder that actually contains image files
    if (out_dir / "images").exists():
        return out_dir / "images"
    return out_dir

def clean_macos_artifacts(root: Path) -> None:
    # Remove __MACOSX folder entirely
    macosx = root.parent / "__MACOSX"
    if macosx.exists():
        shutil.rmtree(macosx, ignore_errors=True)

    # Remove .DS_Store and AppleDouble "._" files anywhere under root
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if p.name in MAC_GARBAGE_NAMES or p.name.startswith(MAC_GARBAGE_PREFIXES):
            try:
                p.unlink()
            except Exception:
                pass

def write_inventory(images_dir: Path, inventory_csv: Path) -> None:
    exts = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".tif", ".tiff", ".bmp", ".heic", ".JPG", ".JPEG", ".PNG"}
    files = [p for p in images_dir.rglob("*") if p.is_file() and p.suffix in exts]
    files.sort(key=lambda x: x.name.lower())

    inventory_csv.parent.mkdir(parents=True, exist_ok=True)
    with inventory_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["filename", "relative_path", "ext", "bytes"])
        for p in files:
            rel = p.relative_to(images_dir)
            w.writerow([p.name, str(rel).replace("\\", "/"), p.suffix, p.stat().st_size])

def ensure_base_structure(project_root: Path) -> None:
    # Keep site-wide images here (logo, favicon, etc.)
    (project_root / "images" / "site").mkdir(parents=True, exist_ok=True)
    # Projects live under works/projects/
    (project_root / "works" / "projects").mkdir(parents=True, exist_ok=True)

def create_projects_csv_if_missing(project_root: Path, csv_path: Path) -> None:
    if csv_path.exists():
        return

    # Default template includes your current 3 projects; you can edit freely later.
    rows = [
        {"project_slug": "p-2024-001-work-one", "title": "Work One", "year": "2024"},
        {"project_slug": "p-2023-001-work-two", "title": "Work Two", "year": "2023"},
        {"project_slug": "p-2022-001-work-three", "title": "Work Three", "year": "2022"},
    ]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["project_slug", "title", "year"])
        w.writeheader()
        for r in rows:
            w.writerow(r)

def ensure_project_folders(project_root: Path, csv_path: Path) -> None:
    projects_root = project_root / "works" / "projects"
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            slug = (row.get("project_slug") or "").strip()
            if not slug:
                continue
            proj_dir = projects_root / slug
            # This is the folder you will move images into:
            (proj_dir / "img").mkdir(parents=True, exist_ok=True)
            # Optional: keep series cover/thumbs here if you want
            (proj_dir / "assets").mkdir(parents=True, exist_ok=True)

def main():
    ap = argparse.ArgumentParser(description="Prepare folder structure for projects + unpack image inbox.")
    ap.add_argument("--zip", default="images.zip", help="Path to images.zip (default: images.zip in project root)")
    ap.add_argument("--project-root", default=".", help="Project root directory (default: current dir)")
    ap.add_argument("--inbox", default="inbox/images_raw", help="Where to extract images into (default: inbox/images_raw)")
    args = ap.parse_args()

    project_root = Path(args.project_root).resolve()
    zip_path = (project_root / args.zip).resolve()
    inbox_root = (project_root / args.inbox).resolve()

    ensure_base_structure(project_root)

    if zip_path.exists():
        extracted_images_dir = unzip_images(zip_path, inbox_root)
        clean_macos_artifacts(extracted_images_dir)
        write_inventory(extracted_images_dir, project_root / "inbox" / "image_inventory.csv")
        print(f"✅ Unzipped to: {extracted_images_dir}")
        print(f"✅ Inventory CSV: {project_root / 'inbox' / 'image_inventory.csv'}")
    else:
        print(f"⚠️ Zip not found: {zip_path} (skip unzip)")

    projects_csv = project_root / "projects.csv"
    create_projects_csv_if_missing(project_root, projects_csv)
    ensure_project_folders(project_root, projects_csv)
    print(f"✅ Project template: {projects_csv}")
    print(f"✅ Project folders created under: {project_root / 'works' / 'projects'}")
    print("\nNext:")
    print("1) Edit projects.csv (add all your future projects)")
    print("2) Move images from inbox/images_raw into each works/projects/<project_slug>/img/")
    print("   Suggested filenames inside each project: thumb.jpg, hero.jpg, 01.jpg, 02.jpg ...")

if __name__ == "__main__":
    main()
