import os
from pathlib import Path

MATPLOTLIB_CACHE_DIR = Path("/tmp/trendpulse_matplotlib")
MATPLOTLIB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MATPLOTLIB_CACHE_DIR))
os.environ.setdefault("XDG_CACHE_HOME", str(MATPLOTLIB_CACHE_DIR))

import matplotlib

# Use a non-interactive backend so the script works in terminal-only environments.
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path("data/trends_analysed.csv")
OUTPUT_DIR = Path("outputs")


def shorten_title(title: str, max_length: int = 50) -> str:
    """Trim long titles so chart labels stay readable."""
    if len(title) <= max_length:
        return title
    return title[: max_length - 3] + "..."


def load_data() -> pd.DataFrame:
    """Load the analysed CSV from Task 3."""
    dataframe = pd.read_csv(INPUT_FILE)
    print(f"Loaded data: {dataframe.shape}")
    return dataframe


def plot_top_stories(dataframe: pd.DataFrame, ax=None) -> None:
    """Plot the top 10 stories by score as a horizontal bar chart."""
    top_stories = dataframe.nlargest(10, "score").copy()
    top_stories["short_title"] = top_stories["title"].apply(shorten_title)
    top_stories = top_stories.sort_values("score")

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 6))

    ax.barh(top_stories["short_title"], top_stories["score"], color="steelblue")
    ax.set_title("Top 10 Stories by Score")
    ax.set_xlabel("Score")
    ax.set_ylabel("Story Title")


def plot_category_counts(dataframe: pd.DataFrame, ax=None) -> None:
    """Plot the number of stories in each category."""
    category_counts = dataframe["category"].value_counts().sort_index()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))

    ax.bar(category_counts.index, category_counts.values, color=colors[: len(category_counts)])
    ax.set_title("Stories per Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Stories")
    ax.tick_params(axis="x", rotation=30)


def plot_score_vs_comments(dataframe: pd.DataFrame, ax=None) -> None:
    """Plot score against comment count and colour by popularity."""
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 6))

    popular = dataframe[dataframe["is_popular"] == True]
    not_popular = dataframe[dataframe["is_popular"] == False]

    ax.scatter(
        not_popular["score"],
        not_popular["num_comments"],
        color="gray",
        alpha=0.7,
        label="Not Popular",
    )
    ax.scatter(
        popular["score"],
        popular["num_comments"],
        color="crimson",
        alpha=0.7,
        label="Popular",
    )

    ax.set_title("Score vs Comments")
    ax.set_xlabel("Score")
    ax.set_ylabel("Number of Comments")
    ax.legend()


def save_single_charts(dataframe: pd.DataFrame) -> None:
    """Create and save the three required charts."""
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    plot_top_stories(dataframe, ax1)
    fig1.tight_layout()
    fig1.savefig(OUTPUT_DIR / "chart1_top_stories.png")
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    plot_category_counts(dataframe, ax2)
    fig2.tight_layout()
    fig2.savefig(OUTPUT_DIR / "chart2_categories.png")
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(8, 6))
    plot_score_vs_comments(dataframe, ax3)
    fig3.tight_layout()
    fig3.savefig(OUTPUT_DIR / "chart3_scatter.png")
    plt.close(fig3)


def save_dashboard(dataframe: pd.DataFrame) -> None:
    """Combine all charts into one dashboard figure."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    plot_top_stories(dataframe, axes[0])
    plot_category_counts(dataframe, axes[1])
    plot_score_vs_comments(dataframe, axes[2])

    fig.suptitle("TrendPulse Dashboard", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUTPUT_DIR / "dashboard.png")
    plt.close(fig)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    dataframe = load_data()
    save_single_charts(dataframe)
    save_dashboard(dataframe)
    print(f"Saved charts to {OUTPUT_DIR.as_posix()}/")


if __name__ == "__main__":
    main()
