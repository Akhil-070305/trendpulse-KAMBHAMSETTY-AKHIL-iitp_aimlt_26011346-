import json
import os
import time
from datetime import datetime

import requests


TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{}.json"
HEADERS = {"User-Agent": "TrendPulse/1.0"}
MAX_STORY_IDS = 500
MAX_PER_CATEGORY = 25

# The category order matters because some keywords overlap (for example "game").
# We assign the first matching category from this list.
CATEGORY_KEYWORDS = {
    "technology": [
        "ai",
        "software",
        "tech",
        "code",
        "computer",
        "data",
        "cloud",
        "api",
        "gpu",
        "llm",
    ],
    "worldnews": [
        "war",
        "government",
        "country",
        "president",
        "election",
        "climate",
        "attack",
        "global",
    ],
    "sports": [
        "nfl",
        "nba",
        "fifa",
        "sport",
        "game",
        "team",
        "player",
        "league",
        "championship",
    ],
    "science": [
        "research",
        "study",
        "space",
        "physics",
        "biology",
        "discovery",
        "nasa",
        "genome",
    ],
    "entertainment": [
        "movie",
        "film",
        "music",
        "netflix",
        "game",
        "book",
        "show",
        "award",
        "streaming",
    ],
}


def fetch_top_story_ids():
    """Fetch the first 500 top Hacker News story IDs."""
    try:
        response = requests.get(TOP_STORIES_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        story_ids = response.json()
        return story_ids[:MAX_STORY_IDS]
    except requests.RequestException as error:
        print(f"Failed to fetch top story IDs: {error}")
        return []


def fetch_story_details(story_id, cache):
    """Fetch story data once and reuse it across category loops."""
    if story_id in cache:
        return cache[story_id]

    try:
        response = requests.get(
            ITEM_URL_TEMPLATE.format(story_id),
            headers=HEADERS,
            timeout=10,
        )
        response.raise_for_status()
        story_data = response.json()
        cache[story_id] = story_data
        return story_data
    except requests.RequestException as error:
        print(f"Failed to fetch story {story_id}: {error}")
        cache[story_id] = None
        return None


def detect_category(title):
    """Return the first category whose keywords appear in the title."""
    title_lower = title.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in title_lower for keyword in keywords):
            return category

    return None


def build_story_record(story_data, category):
    """Extract the required fields for the output JSON."""
    return {
        "post_id": story_data.get("id"),
        "title": story_data.get("title", ""),
        "category": category,
        "score": story_data.get("score", 0),
        "num_comments": story_data.get("descendants", 0),
        "author": story_data.get("by", "unknown"),
        "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def collect_stories():
    """Collect up to 25 stories for each category from the top 500 IDs."""
    top_story_ids = fetch_top_story_ids()
    if not top_story_ids:
        return []

    collected_stories = []
    collected_ids = set()
    story_cache = {}
    category_names = list(CATEGORY_KEYWORDS.keys())

    for index, category in enumerate(category_names):
        stories_in_category = 0

        for story_id in top_story_ids:
            if stories_in_category >= MAX_PER_CATEGORY:
                break

            story_data = fetch_story_details(story_id, story_cache)
            if not story_data or story_id in collected_ids:
                continue

            title = story_data.get("title", "")
            if not title:
                continue

            assigned_category = detect_category(title)
            if assigned_category != category:
                continue

            collected_stories.append(build_story_record(story_data, category))
            collected_ids.add(story_id)
            stories_in_category += 1

        # Sleep only between category loops, not after the last one.
        if index < len(category_names) - 1:
            time.sleep(2)

    return collected_stories


def save_stories_to_json(stories):
    """Save the collected stories in the required data folder."""
    os.makedirs("data", exist_ok=True)
    file_name = f"trends_{datetime.now().strftime('%Y%m%d')}.json"
    file_path = os.path.join("data", file_name)

    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(stories, json_file, indent=4, ensure_ascii=False)

    return file_path


def main():
    stories = collect_stories()
    output_path = save_stories_to_json(stories)
    print(f"Collected {len(stories)} stories. Saved to {output_path}")


if __name__ == "__main__":
    main()
