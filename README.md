# Art Critique Dataset

Dataset workspace for the AI Art Critique Assistant.

This repository stores the labeling schema, annotation guidelines, scripts, notebooks, and small sample files used to build a critique-focused art dataset. The full raw datasets should be downloaded separately and kept out of git unless their license explicitly allows redistribution.

## Goal

Create a curated dataset that can train or evaluate critique models for:

- composition quality
- color harmony
- contrast
- lighting
- perspective
- emotion and critique notes

## Recommended Sources

- WikiArt: style, genre, artist, image metadata
- ArtELingo: emotion labels and art descriptions
- SemArt: artwork metadata and descriptions

Do not edit the original raw dataset files. Create curated label CSV files that reference the source artwork and add your critique labels.

## Repository Structure

```text
data/
  labels/
    critique_labels_v1.csv
  raw/
    .gitkeep
  processed/
    .gitkeep
  samples/
    .gitkeep
docs/
  label_guidelines.md
  schema.md
notebooks/
  01_prepare_wikiart_subset.ipynb
  02_label_review.ipynb
  03_dataset_stats.ipynb
scripts/
  validate_labels.py
```

## Label Values

Use fixed dropdown-style labels so the data stays model-friendly.

| Field | Allowed values |
| --- | --- |
| `composition` | `good`, `average`, `weak` |
| `color_harmony` | `good`, `average`, `weak` |
| `contrast` | `high`, `medium`, `low` |
| `lighting` | `good`, `flat`, `unclear` |
| `perspective` | `correct`, `slightly_wrong`, `wrong`, `not_applicable` |

## Workflow

1. Download source datasets into `data/raw/`.
2. Use `notebooks/01_prepare_wikiart_subset.ipynb` to select 300-500 images.
3. Create or update `data/labels/critique_labels_v1.csv`.
4. Label the selected artworks manually.
5. Run:

```powershell
python scripts/validate_labels.py data/labels/critique_labels_v1.csv
```

6. Use `notebooks/03_dataset_stats.ipynb` to inspect label balance before training.

## Notebook Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
jupyter notebook
```

## Connection to App Repo

The app repo should consume exported CSV files from this dataset repo. Keep the app code and dataset work separate:

- `Art_Critique`: product, backend, frontend, model integration
- `Art_Critique_Dataset`: labels, dataset preparation, notebooks, validation
