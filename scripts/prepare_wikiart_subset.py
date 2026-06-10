from __future__ import annotations

import argparse
import re
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


LABEL_COLUMNS = [
    "id",
    "source",
    "source_id",
    "image_path",
    "image_url",
    "artist",
    "style",
    "genre",
    "emotion",
    "description",
    "composition",
    "color_harmony",
    "contrast",
    "lighting",
    "perspective",
    "critique_notes",
    "split",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a WikiArt subset for manual critique labeling.")
    parser.add_argument("--archive", required=True, help="Path to WikiArt archive.zip")
    parser.add_argument("--target-size", type=int, default=500, help="Number of artworks to select")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--extract-images", action="store_true", help="Extract selected images to data/processed")
    parser.add_argument("--output-name", default="critique_labels_wikiart_unlabeled.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    archive_path = Path(args.archive).expanduser().resolve()
    processed_dir = root / "data" / "processed" / "wikiart_subset"
    images_dir = processed_dir / "images"
    labels_dir = root / "data" / "labels"
    processed_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)

    if not archive_path.exists():
        raise FileNotFoundError(f"Archive not found: {archive_path}")

    with ZipFile(archive_path) as zf:
        with zf.open("classes.csv") as handle:
            classes = pd.read_csv(handle)

        image_names = {name for name in zf.namelist() if name.lower().endswith((".jpg", ".jpeg", ".png"))}
        df = _clean_classes(classes)
        df = df[df["filename"].isin(image_names)].copy()
        subset = _balanced_sample(df, target_size=args.target_size, seed=args.seed)
        subset = _shape_for_labeling(subset)

        if args.extract_images:
            images_dir.mkdir(parents=True, exist_ok=True)
            subset["image_path"] = [
                _extract_image(zf, member_name, images_dir, row_id, root)
                for member_name, row_id in zip(subset["source_id"], subset["id"])
            ]

    metadata_path = processed_dir / "wikiart_subset_metadata.csv"
    labels_path = labels_dir / args.output_name
    subset.to_csv(metadata_path, index=False)
    subset[LABEL_COLUMNS].to_csv(labels_path, index=False)

    print(f"Selected rows: {len(subset)}")
    print(f"Wrote metadata: {metadata_path}")
    print(f"Wrote labels: {labels_path}")
    if args.extract_images:
        print(f"Extracted images: {images_dir}")
    return 0


def _clean_classes(classes: pd.DataFrame) -> pd.DataFrame:
    df = classes.copy()
    df.columns = [column.strip().lower() for column in df.columns]
    if "filename" not in df.columns:
        raise ValueError("classes.csv must contain a filename column")

    for optional in ["artist", "genre", "description", "subset"]:
        if optional not in df.columns:
            df[optional] = ""

    df = df.dropna(subset=["filename"]).drop_duplicates(subset=["filename"]).reset_index(drop=True)
    df["filename"] = df["filename"].astype(str).str.replace("\\\\", "/", regex=False)
    df["style"] = df["filename"].str.split("/", n=1).str[0].fillna("").map(_pretty_label)
    df["genre"] = df["genre"].astype(str).map(_clean_genre)
    df["artist"] = df["artist"].fillna("").astype(str).map(_title_name)
    df["description"] = df["description"].fillna("").astype(str).str.replace("-", " ", regex=False)
    return df


def _balanced_sample(df: pd.DataFrame, target_size: int, seed: int) -> pd.DataFrame:
    if df.empty:
        raise ValueError("No image rows found after matching classes.csv to archive images")

    group_col = "style" if df["style"].replace("", pd.NA).notna().sum() else "genre"
    groups = [group for _, group in df.groupby(group_col)]
    per_group = max(1, target_size // max(len(groups), 1))

    sampled = [
        group.sample(min(len(group), per_group), random_state=seed)
        for group in groups
    ]
    subset = pd.concat(sampled, ignore_index=True)

    if len(subset) < target_size:
        remaining = df[~df["filename"].isin(subset["filename"])]
        needed = min(target_size - len(subset), len(remaining))
        if needed > 0:
            subset = pd.concat(
                [subset, remaining.sample(needed, random_state=seed)],
                ignore_index=True,
            )

    return subset.sample(frac=1, random_state=seed).head(target_size).reset_index(drop=True)


def _shape_for_labeling(subset: pd.DataFrame) -> pd.DataFrame:
    labels = subset.copy()
    labels["id"] = [f"ACD_{index:06d}" for index in range(1, len(labels) + 1)]
    labels["source"] = "wikiart"
    labels["source_id"] = labels["filename"]
    labels["image_path"] = "data/raw/wikiart/" + labels["filename"]
    labels["image_url"] = ""
    labels["emotion"] = ""
    labels["composition"] = ""
    labels["color_harmony"] = ""
    labels["contrast"] = ""
    labels["lighting"] = ""
    labels["perspective"] = ""
    labels["critique_notes"] = ""

    n_rows = len(labels)
    labels["split"] = "train"
    labels.loc[int(n_rows * 0.8): int(n_rows * 0.9) - 1, "split"] = "validation"
    labels.loc[int(n_rows * 0.9):, "split"] = "test"

    for column in LABEL_COLUMNS:
        if column not in labels.columns:
            labels[column] = ""
    return labels[LABEL_COLUMNS + [column for column in labels.columns if column not in LABEL_COLUMNS]]


def _extract_image(zf: ZipFile, member_name: str, images_dir: Path, row_id: str, root: Path) -> str:
    suffix = Path(member_name).suffix.lower() or ".jpg"
    output_path = images_dir / f"{row_id}{suffix}"
    if not output_path.exists():
        with zf.open(member_name) as source, output_path.open("wb") as target:
            target.write(source.read())
    return output_path.relative_to(root).as_posix()


def _pretty_label(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def _title_name(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title()


def _clean_genre(value: str) -> str:
    if not value or value == "nan":
        return ""
    matches = re.findall(r"'([^']+)'", value)
    if matches:
        return "; ".join(matches)
    return value.strip()


if __name__ == "__main__":
    raise SystemExit(main())
