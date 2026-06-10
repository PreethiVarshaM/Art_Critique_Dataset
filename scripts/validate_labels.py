from __future__ import annotations

import csv
import sys
from pathlib import Path


ALLOWED_VALUES = {
    "composition": {"good", "average", "weak"},
    "color_harmony": {"good", "average", "weak"},
    "contrast": {"high", "medium", "low"},
    "lighting": {"good", "flat", "unclear"},
    "perspective": {"correct", "slightly_wrong", "wrong", "not_applicable"},
}

REQUIRED_COLUMNS = {
    "id",
    "source",
    "image_path",
    "composition",
    "color_harmony",
    "contrast",
    "lighting",
    "perspective",
}


def main() -> int:
    allow_empty = "--allow-empty" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg != "--allow-empty"]
    if len(args) != 1:
        print("Usage: python scripts/validate_labels.py data/labels/critique_labels_v1.csv [--allow-empty]")
        return 2

    csv_path = Path(args[0])
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return 2

    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing_columns:
            print(f"Missing required columns: {sorted(missing_columns)}")
            return 1

        errors: list[str] = []
        ids: set[str] = set()
        row_count = 0

        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            row_id = row.get("id", "").strip()
            if not row_id:
                errors.append(f"row {row_number}: missing id")
            elif row_id in ids:
                errors.append(f"row {row_number}: duplicate id {row_id}")
            ids.add(row_id)

            for column, allowed in ALLOWED_VALUES.items():
                value = row.get(column, "").strip()
                if allow_empty and not value:
                    continue
                if value not in allowed:
                    errors.append(
                        f"row {row_number}: invalid {column}={value!r}; expected one of {sorted(allowed)}"
                    )

        if errors:
            print("Validation failed:")
            for error in errors[:50]:
                print(f"- {error}")
            if len(errors) > 50:
                print(f"- ...and {len(errors) - 50} more")
            return 1

    print(f"Validation passed: {row_count} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
