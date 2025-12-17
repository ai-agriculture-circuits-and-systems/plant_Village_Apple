#!/usr/bin/env python3
"""
Organize Plant Village Apple dataset to standard structure.
Supports 5 image variants: color, grayscale, segmented, with_augmentation, without_augmentation.
"""

import os
import json
import shutil
from pathlib import Path
from collections import defaultdict

# Mapping from old subcategory names to new standardized names
SUBCATEGORY_MAPPING = {
    'Apple___Apple_scab': 'scab',
    'Apple___healthy': 'healthy',
    'Apple___Black_rot': 'black_rot',
    'Apple___Cedar_apple_rust': 'cedar_apple_rust',
    'Background_without_leaves': 'background_without_leaves',
}

# Category ID mapping (from labelmap.json)
CATEGORY_ID_MAPPING = {
    'healthy': 1,
    'scab': 2,
    'black_rot': 3,
    'cedar_apple_rust': 4,
    'background_without_leaves': 5,
}

# Image variants to process
IMAGE_VARIANTS = ['color', 'grayscale', 'segmented', 'with_augmentation', 'without_augmentation']


def json_to_csv(json_file, csv_file, category_id):
    """Convert JSON annotation to CSV format."""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    csv_lines = ['#item,x,y,width,height,label']
    
    for ann in data.get('annotations', []):
        bbox = ann['bbox']  # [x, y, width, height]
        csv_lines.append(f"{ann['id']},{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]},{category_id}")
    
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(csv_lines) + '\n')


def organize_variant(root_dir, old_subcat, new_subcat, variant):
    """Organize files for one variant of a subcategory."""
    # Check if data is in data/origin/ or root directory
    old_dir = Path(root_dir) / 'data' / 'origin' / old_subcat
    if not old_dir.exists():
        old_dir = Path(root_dir) / old_subcat
    if not old_dir.exists():
        return 0, 0, 0
    
    variant_dir = old_dir / variant
    if not variant_dir.exists():
        return 0, 0, 0
    
    new_variant_dir = Path(root_dir) / 'apples' / new_subcat / variant
    
    # Create directory structure first
    (new_variant_dir / 'images').mkdir(parents=True, exist_ok=True)
    (new_variant_dir / 'json').mkdir(parents=True, exist_ok=True)
    (new_variant_dir / 'csv').mkdir(parents=True, exist_ok=True)
    
    # Collect all image files from this variant
    image_files = {}
    for ext in ['.JPG', '.jpg', '.png', '.PNG', '.jpeg', '.JPEG']:
        for img_file in variant_dir.glob(f'*{ext}'):
            stem = img_file.stem
            image_files[stem] = img_file
    
    # For without_augmentation, also collect JSON files
    json_files_by_pvc = {}
    json_files_by_stem = {}
    
    # Always check without_augmentation for JSON files (they contain the annotations)
    json_source_dir = old_dir / 'without_augmentation'
    if json_source_dir.exists():
        for json_file in json_source_dir.glob('*.json'):
            stem = json_file.stem
            json_files_by_stem[stem] = json_file
            
            # Try to read pvc_filename from JSON
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('images') and len(data['images']) > 0:
                        pvc_filename = data['images'][0].get('pvc_filename')
                        if pvc_filename:
                            pvc_stem = Path(pvc_filename).stem
                            json_files_by_pvc[pvc_stem] = json_file
            except Exception as e:
                pass
    
    # Also check the variant directory itself for JSON files (for without_augmentation)
    if variant == 'without_augmentation' and variant_dir.exists():
        for json_file in variant_dir.glob('*.json'):
            stem = json_file.stem
            json_files_by_stem[stem] = json_file
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('images') and len(data['images']) > 0:
                        pvc_filename = data['images'][0].get('pvc_filename')
                        if pvc_filename:
                            pvc_stem = Path(pvc_filename).stem
                            json_files_by_pvc[pvc_stem] = json_file
            except Exception as e:
                pass
    
    if not image_files:
        return 0, 0, 0
    
    category_id = CATEGORY_ID_MAPPING[new_subcat]
    copied_images = 0
    copied_json = 0
    generated_csv = 0
    
    for stem, img_file in image_files.items():
        # Copy image
        dst_img = new_variant_dir / 'images' / img_file.name
        shutil.copy2(img_file, dst_img)
        copied_images += 1
        
        # Find matching JSON file (try pvc_filename first, then stem)
        json_file = None
        if stem in json_files_by_pvc:
            json_file = json_files_by_pvc[stem]
        elif stem in json_files_by_stem:
            json_file = json_files_by_stem[stem]
        
        if json_file:
            # Copy JSON with image stem as name
            dst_json = new_variant_dir / 'json' / f"{stem}.json"
            shutil.copy2(json_file, dst_json)
            copied_json += 1
            
            # Generate CSV
            csv_file = new_variant_dir / 'csv' / f"{stem}.csv"
            json_to_csv(json_file, csv_file, category_id)
            generated_csv += 1
        else:
            # Create empty CSV for images without annotations
            csv_file = new_variant_dir / 'csv' / f"{stem}.csv"
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('#item,x,y,width,height,label\n')
    
    return copied_images, copied_json, generated_csv


def organize_subcategory(root_dir, old_subcat, new_subcat):
    """Organize files for one subcategory, processing all variants."""
    print(f"Organizing {old_subcat} -> {new_subcat}...")
    
    total_images = 0
    total_json = 0
    total_csv = 0
    
    for variant in IMAGE_VARIANTS:
        images, json_files, csv_files = organize_variant(root_dir, old_subcat, new_subcat, variant)
        if images > 0:
            print(f"  {variant}: {images} images, {json_files} JSON files, {csv_files} CSV files")
            total_images += images
            total_json += json_files
            total_csv += csv_files
    
    print(f"  Total: {total_images} images, {total_json} JSON files, {total_csv} CSV files")


def create_splits(root_dir):
    """Create dataset split files from existing all/ directory."""
    print("Creating dataset splits...")
    
    # Check if all/ is in data/origin/ or root directory
    all_dir = Path(root_dir) / 'data' / 'origin' / 'all'
    if not all_dir.exists():
        all_dir = Path(root_dir) / 'all'
    if not all_dir.exists():
        print("  Warning: all/ directory does not exist, skipping splits creation")
        return
    
    # Read existing split files
    splits = {}
    for split_name in ['train', 'val', 'test']:
        split_file = all_dir / f"{split_name}.txt"
        if split_file.exists():
            with open(split_file, 'r', encoding='utf-8') as f:
                splits[split_name] = [line.strip() for line in f if line.strip()]
            print(f"  Read {len(splits[split_name])} files from {split_name}.txt")
    
    # Map filenames to subcategories (using color variant as reference)
    filename_to_subcat = {}
    for old_subcat, new_subcat in SUBCATEGORY_MAPPING.items():
        # Try color variant first
        images_dir = Path(root_dir) / 'apples' / new_subcat / 'color' / 'images'
        if not images_dir.exists():
            # Fallback to without_augmentation for background
            images_dir = Path(root_dir) / 'apples' / new_subcat / 'without_augmentation' / 'images'
        
        if images_dir.exists():
            for img_file in images_dir.iterdir():
                if img_file.is_file():
                    stem = img_file.stem
                    filename_to_subcat[stem] = new_subcat
    
    # Create split files for each subcategory and each variant
    for new_subcat in SUBCATEGORY_MAPPING.values():
        subcat_splits = defaultdict(list)
        
        for split_name, filenames in splits.items():
            for filename in filenames:
                stem = Path(filename).stem
                if stem in filename_to_subcat and filename_to_subcat[stem] == new_subcat:
                    subcat_splits[split_name].append(stem)
        
        # Create split files for each variant
        for variant in IMAGE_VARIANTS:
            variant_dir = Path(root_dir) / 'apples' / new_subcat / variant
            if not variant_dir.exists():
                continue
            
            sets_dir = variant_dir / 'sets'
            sets_dir.mkdir(parents=True, exist_ok=True)
            
            # Get all image stems in this variant (actual file stems)
            variant_image_stems = set()
            stem_mapping = {}  # Map base stem to actual stem(s) for segmented variant
            images_dir = variant_dir / 'images'
            if images_dir.exists():
                for img_file in images_dir.iterdir():
                    if img_file.is_file():
                        stem = img_file.stem
                        variant_image_stems.add(stem)
                        
                        # For segmented variant, create mapping from base name to actual name
                        if variant == 'segmented':
                            if stem.endswith('_final_masked_1'):
                                base_stem = stem[:-15]  # Remove '_final_masked_1'
                                if base_stem not in stem_mapping:
                                    stem_mapping[base_stem] = []
                                stem_mapping[base_stem].append(stem)
                            elif stem.endswith('_final_masked'):
                                base_stem = stem[:-13]  # Remove '_final_masked'
                                if base_stem not in stem_mapping:
                                    stem_mapping[base_stem] = []
                                stem_mapping[base_stem].append(stem)
            
            # For segmented and other variants, create splits based on actual images
            if variant_image_stems:
                # Try to match with color variant splits first
                matched_splits = defaultdict(list)
                for split_name, filenames in subcat_splits.items():
                    for filename in filenames:
                        # Check direct match
                        if filename in variant_image_stems:
                            matched_splits[split_name].append(filename)
                        # For segmented, check mapping and add all matching variants
                        elif variant == 'segmented' and filename in stem_mapping:
                            # Add all variants (with and without _1 suffix)
                            matched_splits[split_name].extend(stem_mapping[filename])
                
                # If no matches found or variant has different naming, create splits based on variant's own images
                if not any(matched_splits.values()) or variant == 'with_augmentation':
                    # Create splits proportionally based on variant's images
                    all_variant_stems = sorted(variant_image_stems)
                    total = len(all_variant_stems)
                    if total > 0:
                        # Use same proportions as color variant
                        color_total = len(subcat_splits.get('all', []))
                        if color_total > 0:
                            train_ratio = len(subcat_splits.get('train', [])) / color_total
                            val_ratio = len(subcat_splits.get('val', [])) / color_total
                        else:
                            train_ratio = 0.7
                            val_ratio = 0.15
                        
                        train_size = int(total * train_ratio)
                        val_size = int(total * val_ratio)
                        test_size = total - train_size - val_size
                        
                        matched_splits['train'] = all_variant_stems[:train_size]
                        matched_splits['val'] = all_variant_stems[train_size:train_size+val_size]
                        matched_splits['test'] = all_variant_stems[train_size+val_size:]
                
                # Write split files
                for split_name, filenames in matched_splits.items():
                    if filenames:
                        split_file = sets_dir / f"{split_name}.txt"
                        with open(split_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(sorted(filenames)) + '\n')
                        print(f"  Created {split_file} with {len(filenames)} files")
                
                # Create all.txt for this variant (use actual stems, remove duplicates from mapping)
                # For segmented, all.txt should contain actual file stems
                all_file = sets_dir / 'all.txt'
                with open(all_file, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(sorted(variant_image_stems)) + '\n')
                print(f"  Created {all_file} with {len(variant_image_stems)} files")


def main():
    root_dir = Path(__file__).parent.parent
    
    print("Organizing Plant Village Apple dataset...")
    print(f"Root directory: {root_dir}\n")
    
    # Organize each subcategory (all variants)
    for old_subcat, new_subcat in SUBCATEGORY_MAPPING.items():
        organize_subcategory(root_dir, old_subcat, new_subcat)
        print()
    
    # Create dataset splits
    create_splits(root_dir)
    
    print("\nDone!")


if __name__ == '__main__':
    main()
