#!/usr/bin/env python3
"""
Convert Plant Village Apple dataset annotations to COCO JSON format.
Supports multi-class classification (healthy=1, scab=2, black_rot=3, cedar_apple_rust=4).
Structure: apples/{subcategory}/ subdirectories.
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image

# Subcategory mapping
SUBCATEGORIES = ['healthy', 'scab', 'black_rot', 'cedar_apple_rust', 'background_without_leaves']
CATEGORY_ID_MAPPING = {
    'healthy': 1,
    'scab': 2,
    'black_rot': 3,
    'cedar_apple_rust': 4,
    'background_without_leaves': 5,
}


def read_split_list(split_file: Path) -> List[str]:
    """Read image base names (without extension) from a split file."""
    if not split_file.exists():
        return []
    lines = [line.strip() for line in split_file.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line]


def image_size(image_path: Path) -> Tuple[int, int]:
    """Return (width, height) for an image path using PIL."""
    with Image.open(image_path) as img:
        return img.width, img.height


def parse_csv_boxes(csv_path: Path) -> List[Dict]:
    """Parse a single CSV file and return bounding boxes with category IDs."""
    if not csv_path.exists():
        return []
    
    boxes = []
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                x = float(row.get('x', 0))
                y = float(row.get('y', 0))
                width = float(row.get('width', 0))
                height = float(row.get('height', 0))
                label = int(row.get('label', 1))
                
                if width > 0 and height > 0:
                    boxes.append({
                        'bbox': [x, y, width, height],
                        'area': width * height,
                        'category_id': label
                    })
            except (ValueError, KeyError):
                continue
    
    return boxes


def collect_annotations_for_split(
    category_root: Path,
    split: str,
    subcategories: List[str],
    variant: str = 'color',
) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """Collect COCO dictionaries for images, annotations, and categories.
    Supports multiple subcategories: healthy, scab, black_rot, cedar_apple_rust.
    Supports image variants: color, grayscale, segmented, with_augmentation, without_augmentation.
    """
    # Try to read from variant-specific sets file
    image_stems = set()
    for subcat in subcategories:
        variant_dir = category_root / subcat / variant
        sets_dir = variant_dir / "sets"
        split_file = sets_dir / f"{split}.txt"
        if split_file.exists():
            image_stems.update(read_split_list(split_file))
    
    if not image_stems:
        # Fall back to all images from all subcategories and variant
        image_stems = set()
        for subcat in subcategories:
            variant_dir = category_root / subcat / variant
            images_dir = variant_dir / "images"
            if images_dir.exists():
                for ext in ['.png', '.jpg', '.JPG', '.PNG', '.jpeg', '.JPEG']:
                    image_stems.update({p.stem for p in images_dir.glob(f"*{ext}")})
    
    images: List[Dict] = []
    anns: List[Dict] = []
    categories: List[Dict] = [
        {"id": 1, "name": "healthy", "supercategory": "apple"},
        {"id": 2, "name": "scab", "supercategory": "apple"},
        {"id": 3, "name": "black_rot", "supercategory": "apple"},
        {"id": 4, "name": "cedar_apple_rust", "supercategory": "apple"},
        {"id": 5, "name": "background_without_leaves", "supercategory": "apple"},
    ]
    
    image_id_counter = 1
    ann_id_counter = 1
    
    # Search through all subcategories and variant
    for stem in sorted(image_stems):
        img_path = None
        subcategory = None
        csv_path = None
        
        # Try each subcategory and variant
        for subcat in subcategories:
            variant_dir = category_root / subcat / variant
            for ext in ['.png', '.jpg', '.JPG', '.PNG', '.jpeg', '.JPEG']:
                test_path = variant_dir / 'images' / f"{stem}{ext}"
                if test_path.exists():
                    img_path = test_path
                    subcategory = subcat
                    csv_path = variant_dir / 'csv' / f"{stem}.csv"
                    break
            if img_path:
                break
        
        if not img_path:
            continue
        
        width, height = image_size(img_path)
        images.append({
            "id": image_id_counter,
            "file_name": f"apples/{subcategory}/{variant}/images/{img_path.name}",
            "width": width,
            "height": height,
        })
        
        if csv_path and csv_path.exists():
            for box in parse_csv_boxes(csv_path):
                anns.append({
                    "id": ann_id_counter,
                    "image_id": image_id_counter,
                    "category_id": box['category_id'],
                    "bbox": box['bbox'],
                    "area": box['area'],
                    "iscrowd": 0,
                })
                ann_id_counter += 1
        
        image_id_counter += 1
    
    return images, anns, categories


def build_coco_dict(
    images: List[Dict],
    anns: List[Dict],
    categories: List[Dict],
    description: str,
) -> Dict:
    """Build a complete COCO dict from components."""
    return {
        "info": {
            "year": 2025,
            "version": "1.0.0",
            "description": description,
            "url": "https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset",
        },
        "images": images,
        "annotations": anns,
        "categories": categories,
        "licenses": [],
    }


def convert(
    root: Path,
    out_dir: Path,
    category: str,
    splits: List[str],
    subcategories: List[str],
    variant: str = 'color',
) -> None:
    """Convert selected category and splits to COCO JSON files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    
    category_root = root / category
    
    for split in splits:
        images, anns, categories = collect_annotations_for_split(
            category_root, split, subcategories, variant
        )
        desc = f"Plant Village Apple {category} {variant} {split} split"
        coco = build_coco_dict(images, anns, categories, desc)
        out_path = out_dir / f"{category}_{variant}_instances_{split}.json"
        out_path.write_text(json.dumps(coco, indent=2), encoding="utf-8")
        print(f"Generated: {out_path} ({len(images)} images, {len(anns)} annotations)")


def convert_combined(
    root: Path,
    out_dir: Path,
    category: str,
    splits: List[str],
    subcategories: List[str],
    variant: str = 'color',
) -> None:
    """Convert all subcategories combined into single COCO JSON files."""
    out_dir.mkdir(parents=True, exist_ok=True)
    
    category_root = root / category
    
    for split in splits:
        images, anns, categories = collect_annotations_for_split(
            category_root, split, subcategories, variant
        )
        desc = f"Plant Village Apple {category} {variant} combined {split} split"
        coco = build_coco_dict(images, anns, categories, desc)
        out_path = out_dir / f"combined_{variant}_instances_{split}.json"
        out_path.write_text(json.dumps(coco, indent=2), encoding="utf-8")
        print(f"Generated: {out_path} ({len(images)} images, {len(anns)} annotations)")


def main():
    parser = argparse.ArgumentParser(description="Convert Plant Village Apple annotations to COCO JSON")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Dataset root directory",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory for COCO JSON files (default: <root>/annotations)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="apples",
        help="Category name (default: apples)",
    )
    parser.add_argument(
        "--subcategories",
        nargs="+",
        default=SUBCATEGORIES,
        choices=SUBCATEGORIES,
        help=f"Subcategories to include (default: {' '.join(SUBCATEGORIES)})",
    )
    parser.add_argument(
        "--splits",
        nargs="+",
        default=["train", "val", "test"],
        choices=["train", "val", "test"],
        help="Dataset splits to generate (default: train val test)",
    )
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Generate combined COCO JSON files for all subcategories",
    )
    parser.add_argument(
        "--variant",
        type=str,
        default="color",
        choices=["color", "grayscale", "segmented", "with_augmentation", "without_augmentation"],
        help="Image variant to convert (default: color)",
    )
    
    args = parser.parse_args()
    
    if args.out is None:
        args.out = args.root / "annotations"
    
    if args.combined:
        convert_combined(
            root=args.root,
            out_dir=args.out,
            category=args.category,
            splits=args.splits,
            subcategories=args.subcategories,
            variant=args.variant,
        )
    else:
        convert(
            root=args.root,
            out_dir=args.out,
            category=args.category,
            splits=args.splits,
            subcategories=args.subcategories,
            variant=args.variant,
        )


if __name__ == "__main__":
    main()
