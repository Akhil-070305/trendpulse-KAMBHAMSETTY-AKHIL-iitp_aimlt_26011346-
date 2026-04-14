from pathlib import Path
import sys

import pandas as pd


CATEGORY_ORDER = [
    "technology",
    "worldnews",
    "sports",
    "science",
    "entertainment",
]


def find_input_file() -> Path:
    """Return the newest JSON file created by Task 1."""
    json_files = sorted(Path("data").glob("trends_*.json"))
    if not json_files:
        raise FileNotFoundError("No trends JSON file found in the data folder.")
    return json_files[-1]


def load_trends(json_path: Path) -> pd.DataFrame:
    """Load the raw trends JSON into a DataFrame."""
    dataframe = pd.read_json(json_path)
    print(f"Loaded {len(dataframe)} stories from {json_path.as_posix()}")
    return dataframe


def clean_trends(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Clean duplicates, missing values, data types, and low-quality rows."""
    cleaned = dataframe.copy()

    # Make sure the columns we need always exist before cleaning.
    for column in ["post_id", "title", "score", "num_comments", "category"]:
        if column not in cleaned.columns:
            cleaned[column] = pd.NA

    # Clean whitespace first so titles containing only spaces are treated as missing.
    cleaned["title"] = cleaned["title"].astype("string").str.strip()
    cleaned.loc[cleaned["title"] == "", "title"] = pd.NA

    # Coerce numeric columns so bad values become NaN and can be handled safely.
    cleaned["post_id"] = pd.to_numeric(cleaned["post_id"], errors="coerce")
    cleaned["score"] = pd.to_numeric(cleaned["score"], errors="coerce")
    cleaned["num_comments"] = pd.to_numeric(cleaned["num_comments"], errors="coerce")

    cleaned = cleaned.drop_duplicates(subset="post_id")
    print(f"After removing duplicates: {len(cleaned)}")

    cleaned = cleaned.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(cleaned)}")

    cleaned["post_id"] = cleaned["post_id"].astype(int)
    cleaned["score"] = cleaned["score"].astype(int)
    cleaned["num_comments"] = cleaned["num_comments"].fillna(0).astype(int)

    cleaned = cleaned[cleaned["score"] >= 5].copy()
    print(f"After removing low scores: {len(cleaned)}")
    print(f"Rows remaining after cleaning: {len(cleaned)}")

    return cleaned


def save_trends(dataframe: pd.DataFrame, output_path: Path) -> None:
    """Save the cleaned DataFrame as CSV and print a category summary."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)

    print(f"\nSaved {len(dataframe)} rows to {output_path.as_posix()}")
    print("\nStories per category:")

    category_counts = dataframe["category"].value_counts()
    category_counts = category_counts.reindex(CATEGORY_ORDER, fill_value=0)
    for category, count in category_counts.items():
        print(f"{category:<15} {count}")


def main() -> None:
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_input_file()
    cleaned_trends = clean_trends(load_trends(json_path))
    save_trends(cleaned_trends, Path("data/trends_clean.csv"))


if __name__ == "__main__":
    main()
