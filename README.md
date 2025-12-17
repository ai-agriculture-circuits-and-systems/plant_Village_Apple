# Plant Village Apple

[![DOI](https://img.shields.io/badge/DOI-pending-lightgrey)](#citation)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-blue.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](#changelog)

Apple leaf disease classification dataset from Plant Village. Contains images of apple leaves labeled for disease classification (healthy, scab, black rot, cedar apple rust). This dataset follows the standardized layout specification.

- Project page: `https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset`
- Issue tracker: use this repo

## TL;DR
- Task: classification (five classes: `healthy`, `scab`, `black_rot`, `cedar_apple_rust`, `background_without_leaves`)
- Modality: RGB
- Platform: handheld/field
- Real/Synthetic: real
- Images: 8,628 (see counts below)
- Classes: 5
- Resolution: 256×256 pixels
- Annotations: COCO JSON (object detection with bounding boxes)
- License: CC BY 4.0 (see License)
- Citation: see below

## Table of contents
- [Download](#download)
- [Dataset structure](#dataset-structure)
- [Sample images](#sample-images)
- [Annotation schema](#annotation-schema)
- [Stats and splits](#stats-and-splits)
- [Quick start](#quick-start)
- [Evaluation and baselines](#evaluation-and-baselines)
- [Datasheet (data card)](#datasheet-data-card)
- [Known issues and caveats](#known-issues-and-caveats)
- [License](#license)
- [Citation](#citation)
- [Changelog](#changelog)
- [Contact](#contact)

## Download
- Original dataset: `https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset`
- This repo hosts structure and conversion scripts only; place the downloaded folders under this directory.
- Local license file: see `LICENSE` (Creative Commons Attribution 4.0).

## Dataset structure

This dataset follows the standardized dataset structure specification with subcategory organization:

```
Plant_Village_Apple/
├── apples/
│   ├── healthy/              # Healthy apple images
│   │   ├── color/            # Color variant
│   │   │   ├── csv/          # CSV annotations per image
│   │   │   ├── json/         # Original JSON annotations
│   │   │   ├── images/       # Color images
│   │   │   └── sets/         # Dataset splits for this variant
│   │   ├── grayscale/        # Grayscale variant
│   │   │   ├── csv/
│   │   │   ├── json/
│   │   │   ├── images/
│   │   │   └── sets/
│   │   ├── segmented/        # Segmented variant
│   │   │   ├── csv/
│   │   │   ├── json/
│   │   │   ├── images/
│   │   │   └── sets/
│   │   ├── with_augmentation/  # Augmented variant
│   │   │   ├── csv/
│   │   │   ├── json/
│   │   │   ├── images/
│   │   │   └── sets/
│   │   └── without_augmentation/  # Original variant
│   │       ├── csv/
│   │       ├── json/
│   │       ├── images/
│   │       └── sets/
│   ├── scab/                 # Apple scab images (same structure as healthy)
│   ├── black_rot/            # Black rot images (same structure as healthy)
│   ├── cedar_apple_rust/     # Cedar apple rust images (same structure as healthy)
│   ├── background_without_leaves/  # Background images (same structure, fewer variants)
│   └── labelmap.json        # Label mapping (healthy=1, scab=2, black_rot=3, cedar_apple_rust=4, background_without_leaves=5)
├── data/
│   └── origin/               # Original data (preserved for reference)
│       ├── Apple___Apple_scab/
│       │   ├── color/              # Color images (used in standardized structure)
│       │   ├── without_augmentation/  # Original images with JSON annotations
│       │   ├── grayscale/          # Grayscale variant
│       │   ├── segmented/          # Segmented variant
│       │   └── with_augmentation/  # Augmented variant
│       ├── Apple___healthy/        # Same structure as above
│       ├── Apple___Black_rot/      # Same structure as above
│       ├── Apple___Cedar_apple_rust/  # Same structure as above
│       ├── Background_without_leaves/
│       ├── all/                    # Original split files
│       └── leaf_groups.json        # Original metadata
├── annotations/              # COCO format JSON (generated)
│   ├── apples_instances_train.json
│   ├── apples_instances_val.json
│   ├── apples_instances_test.json
│   └── combined_instances_*.json
├── scripts/
│   ├── organize_dataset.py   # Dataset organization script
│   └── convert_to_coco.py   # COCO conversion script
├── LICENSE
├── README.md
└── requirements.txt
```

- Splits: Each subcategory and each variant has its own `sets/` directory. `apples/{subcategory}/{variant}/sets/train.txt`, `apples/{subcategory}/{variant}/sets/val.txt`, `apples/{subcategory}/{variant}/sets/test.txt` list image basenames (no extension). If missing, all images are used.

**Image Variants**: The dataset contains 5 image variants for each subcategory, all organized in the standardized structure:
- `color/`: Color images (RGB color images)
- `grayscale/`: Grayscale variant (grayscale converted images)
- `segmented/`: Segmented variant (segmentation mask images)
- `with_augmentation/`: Augmented variant (data augmentation applied)
- `without_augmentation/`: Original variant (original images without augmentation)

Each variant has its own complete directory structure with `csv/`, `json/`, `images/`, and `sets/` subdirectories. JSON annotations are primarily sourced from `without_augmentation/` and shared across variants where applicable.

## Sample images

Below are example images for each category in this dataset. Paths are relative to this README location.

<table>
  <tr>
    <th>Category</th>
    <th>Sample</th>
  </tr>
  <tr>
    <td><strong>Healthy</strong></td>
    <td>
      <img src="apples/healthy/images/89f6b546-2692-4ea9-aaac-66ef1b8a7bdd___RS_HL 7250_1.JPG" alt="Healthy example" width="260"/>
      <div align="center"><code>apples/healthy/images/89f6b546-2692-4ea9-aaac-66ef1b8a7bdd___RS_HL 7250_1.JPG</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>Scab</strong></td>
    <td>
      <img src="apples/scab/images/1f98b949-4df2-45cf-8572-3b4a753be21a___FREC_Scab 2907.JPG" alt="Scab example" width="260"/>
      <div align="center"><code>apples/scab/images/1f98b949-4df2-45cf-8572-3b4a753be21a___FREC_Scab 2907.JPG</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>Black Rot</strong></td>
    <td>
      <img src="apples/black_rot/images/0a0b0c0d-0e0f-0g0h-0i0j-0k0l0m0n0o0p.JPG" alt="Black rot example" width="260"/>
      <div align="center"><code>apples/black_rot/images/...</code></div>
    </td>
  </tr>
  <tr>
    <td><strong>Cedar Apple Rust</strong></td>
    <td>
      <img src="apples/cedar_apple_rust/images/0p0q0r0s-0t0u-0v0w-0x0y-0z0a0b0c0d0e.JPG" alt="Cedar apple rust example" width="260"/>
      <div align="center"><code>apples/cedar_apple_rust/images/...</code></div>
    </td>
  </tr>
</table>

## Annotation schema
- CSV per-image schemas (stored under each subcategory's `csv/` folder):
  - Object detection task: columns include `item, x, y, width, height, label` (bounding boxes for detected objects/leaves).
- COCO-style (generated):
```json
{
  "info": {"year": 2025, "version": "1.0.0", "description": "Plant Village Apple apples train split", "url": "https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset"},
  "images": [{"id": 1, "file_name": "apples/healthy/images/xxx.JPG", "width": 256, "height": 256}],
  "categories": [
    {"id": 1, "name": "healthy", "supercategory": "apple"},
    {"id": 2, "name": "scab", "supercategory": "apple"},
    {"id": 3, "name": "black_rot", "supercategory": "apple"},
    {"id": 4, "name": "cedar_apple_rust", "supercategory": "apple"},
    {"id": 5, "name": "background_without_leaves", "supercategory": "apple"}
  ],
  "annotations": [{"id": 1, "image_id": 1, "category_id": 1, "bbox": [0, 13, 235, 235], "area": 55225, "iscrowd": 0}]
}
```

- Label maps: `apples/labelmap.json` defines the category mapping; the provided converter normalizes to 5 categories (healthy=1, scab=2, black_rot=3, cedar_apple_rust=4, background_without_leaves=5).

## Stats and splits
- **Total images (all variants)**: ~39,230 images across 5 variants
  - **Healthy**: 16,450 images (3,290 per variant × 5 variants)
  - **Scab**: 7,040 images (1,260 per variant × 4 variants + 2,000 augmented)
  - **Black Rot**: 6,968 images (1,242 per variant × 4 variants + 2,000 augmented)
  - **Cedar Apple Rust**: 4,200 images (550 per variant × 4 variants + 2,000 augmented)
  - **Background without leaves**: 4,572 images (2,286 per variant × 2 variants)
- **Per variant (color variant as example)**:
  - Healthy: 3,290 images
  - Scab: 1,260 images
  - Black Rot: 1,242 images
  - Cedar Apple Rust: 550 images
  - Background without leaves: 0 images (color variant not available)
- **Training set** (color variant): 425 images (2,001 annotations) (from disease categories only)
- **Validation set** (color variant): 127 images (571 annotations) (from disease categories only)
- **Test set** (color variant): 521 images (2,437 annotations) (from disease categories only)
- **Classes**: 5 (healthy=1, scab=2, black_rot=3, cedar_apple_rust=4, background_without_leaves=5)
- **Splits**: Provided via `apples/{subcategory}/{variant}/sets/*.txt`. Each subcategory and each variant has its own split files. You may define your own splits by editing those files.

## Quick start
Python (COCO):
```python
from pycocotools.coco import COCO
coco = COCO("annotations/combined_instances_train.json")
img_ids = coco.getImgIds()
img = coco.loadImgs(img_ids[0])[0]
ann_ids = coco.getAnnIds(imgIds=img['id'])
anns = coco.loadAnns(ann_ids)
```

Convert CSV to COCO JSON:
```bash
# Convert color variant (default)
python scripts/convert_to_coco.py --root . --out annotations --category apples --splits train val test --combined --variant color

# Convert other variants
python scripts/convert_to_coco.py --root . --out annotations --category apples --splits train val test --combined --variant grayscale
python scripts/convert_to_coco.py --root . --out annotations --category apples --splits train val test --combined --variant segmented
python scripts/convert_to_coco.py --root . --out annotations --category apples --splits train val test --combined --variant with_augmentation
python scripts/convert_to_coco.py --root . --out annotations --category apples --splits train val test --combined --variant without_augmentation
```

Dependencies:
```bash
python -m pip install pillow
# Optional: for COCO API
# python -m pip install pycocotools
```

## Evaluation and baselines
- Primary metric: mAP@[.50:.95] for object detection
- Classification accuracy for image-level classification tasks
- Baseline results: pending

## Datasheet (data card)

### Motivation
The Plant Village dataset was created to provide a comprehensive collection of plant disease images for machine learning research. The apple subset focuses on common apple leaf diseases for classification and detection tasks.

### Composition
- **Image types**: RGB images of apple leaves
- **Categories**: 4 classes (healthy, scab, black rot, cedar apple rust)
- **Image resolution**: 256×256 pixels
- **Annotation format**: Bounding boxes for detected objects/leaves

### Collection process
Images were collected from various sources and standardized to 256×256 pixels. Annotations include bounding boxes for detected objects within each image.

### Preprocessing
- Images resized to 256×256 pixels
- Annotations converted from JSON to CSV format
- Dataset organized into standardized structure with subcategory directories
- **Image variants**: All 5 variants (color, grayscale, segmented, with_augmentation, without_augmentation) are organized in the standardized structure. Each variant maintains its own complete directory structure with images, annotations, and splits.

### Distribution
- Original dataset available on Kaggle
- This repository provides standardized structure and conversion scripts

### Maintenance
- Maintained by the dataset contributors
- Issues and updates tracked in this repository

## Known issues and caveats
- Some images may have multiple annotations (multiple leaves/objects per image)
- Image filenames contain spaces and special characters (preserved from original dataset)
- Original dataset structure has been reorganized to follow standard specification
- JSON annotations contain additional metadata (pvc_filename, leaf_info) that may be useful for reference
- **Image variants**: All 5 variants (color, grayscale, segmented, with_augmentation, without_augmentation) are organized in the standardized structure. Each variant has its own complete directory structure. Note that `segmented` variant may not have JSON annotations as it contains segmentation masks rather than detection annotations.

## License
This dataset is released under the Creative Commons Attribution 4.0 International License (CC BY 4.0). See `LICENSE` file for details.

Check the original dataset terms and cite appropriately.

## Citation
If you use this dataset, please cite:

```bibtex
@misc{plantvillage2015,
  title={Plant Village Dataset},
  author={Hughes, David and Salathé, Marcel},
  year={2015},
  howpublished={\url{https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset}}
}
```

Original paper:
```bibtex
@article{hughes2015open,
  title={An open access repository of images on plant health to enable the development of mobile disease diagnostics},
  author={Hughes, David P and Salath{\'e}, Marcel},
  journal={arXiv preprint arXiv:1511.08060},
  year={2015}
}
```

## Changelog
- **V1.0.0** (2025-12-14): Initial standardized structure and COCO conversion utility

## Contact
- **Maintainers**: Dataset maintainers
- **Original authors**: David Hughes, Marcel Salathé
- **Source**: `https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset`
