from pathlib import Path

import numpy as np
import pandas as pd


INPUT_FILE = Path("data/trends_clean.csv")
OUTPUT_FILE = Path("data/trends_analysed.csv")


def load_data() -> pd.DataFrame:
    """Load the cleaned CSV from Task 2 and print a quick overview."""
    dataframe = pd.read_csv(INPUT_FILE)

    print(f"Loaded data: {dataframe.shape}")
    print("\nFirst 5 rows:")
    print(dataframe.head())

    average_score = dataframe["score"].mean()
    average_comments = dataframe["num_comments"].mean()

    print(f"\nAverage score   : {average_score:.2f}")
    print(f"Average comments: {average_comments:.2f}")

    return dataframe


def run_numpy_analysis(dataframe: pd.DataFrame) -> float:
    """Use NumPy to calculate the required statistics."""
    scores = dataframe["score"].to_numpy()
    comments = dataframe["num_comments"].to_numpy()

    mean_score = np.mean(scores)
    median_score = np.median(scores)
    std_score = np.std(scores)
    max_score = np.max(scores)
    min_score = np.min(scores)

    top_category = dataframe["category"].value_counts().idxmax()
    top_category_count = dataframe["category"].value_counts().max()

    most_commented_index = np.argmax(comments)
    most_commented_story = dataframe.iloc[most_commented_index]

    print("\n--- NumPy Stats ---")
    print(f"Mean score   : {mean_score:.2f}")
    print(f"Median score : {median_score:.2f}")
    print(f"Std deviation: {std_score:.2f}")
    print(f"Max score    : {max_score}")
    print(f"Min score    : {min_score}")
    print(f"\nMost stories in: {top_category} ({top_category_count} stories)")
    print(
        f'Most commented story: "{most_commented_story["title"]}" '
        f'- {int(most_commented_story["num_comments"])} comments'
    )

    return float(mean_score)


def add_columns(dataframe: pd.DataFrame, average_score: float) -> pd.DataFrame:
    """Add the extra columns required for later tasks."""
    dataframe = dataframe.copy()

    # Engagement estimates how much discussion a story gets per upvote.
    dataframe["engagement"] = dataframe["num_comments"] / (dataframe["score"] + 1)

    # A story is popular when its score is above the dataset average.
    dataframe["is_popular"] = dataframe["score"] > average_score

    return dataframe


def save_data(dataframe: pd.DataFrame) -> None:
    """Save the analysed dataset for Task 4."""
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE.as_posix()}")


def main() -> None:
    dataframe = load_data()
    average_score = run_numpy_analysis(dataframe)
    analysed_dataframe = add_columns(dataframe, average_score)
    save_data(analysed_dataframe)


if __name__ == "__main__":
    main()
