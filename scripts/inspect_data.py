import csv
from pathlib import Path

DATA_DIR = Path("data/raw")


def inspect_csv(file_path):
    print(f"\n{'=' * 60}")
    print(f"FILE: {file_path.name}")
    print(f"{'=' * 60}")

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)

        header = next(reader)
        print(f"Columns ({len(header)}):")
        print(header)

        print("\nFirst 3 rows:")
        for i, row in enumerate(reader):
            print(row)
            if i == 2:
                break


for csv_file in DATA_DIR.glob("*.csv"):
    inspect_csv(csv_file)