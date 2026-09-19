# data/kaggle_raw/

Manually download the Kaggle dataset **"Bone Fracture Multi-Region X-ray Data"**
(https://www.kaggle.com/datasets/bmadushanirodrigo/fracture-multi-region-x-ray-data),
unzip it, and place its contents directly inside this folder (keeping the
`train/`, `val/`, `test/` structure with `Fractured` / `Not Fractured`
subfolders that the dataset ships with).

Then run:

```bash
uv run scripts/import_kaggle_xrays.py
```

This classifies the fractured images by anatomical region (when the folder/file
name allows it to be inferred) and copies them, organized, into
`data/xray_images/`, ready to be used as a real X-ray instead of the synthetic
placeholder.

**Important — not committed to git**: this folder (`data/kaggle_raw/`) and the
generated `data/xray_images/` folder are both in `.gitignore`. The Kaggle images
have their own license and must not be redistributed inside this repository;
anyone working on the project should download them independently by following
these steps.
