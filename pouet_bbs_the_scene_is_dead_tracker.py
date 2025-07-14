import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from rapidfuzz import fuzz
from meme_arrays import meme_array_scene_is_dead

def fuzzy_occurence(target_phrases, output_png):
    # Folders
    input_folder = "./bbs"
    output_folder = "./stats"
    os.makedirs(output_folder, exist_ok=True)

    # Data storage
    data = []

    # Read all .json files
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".json"):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                try:
                    thread = json.load(f)
                    posts = thread.get("posts", [])
                    for post in posts:
                        timestamp = post.get("timestamp")
                        content = post.get("content", "").strip().lower()
                        if timestamp and content:
                            data.append({
                                "datetime": timestamp,
                                "message": content
                            })
                except json.JSONDecodeError as e:
                    print(f"Error reading {filename}: {e}")

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df["quarter"] = df["datetime"].dt.to_period("Q")
    df["month"] = df["datetime"].dt.to_period("M")

    # Fuzzy match logic
    match_threshold = 97  # Percent similarity

    def fuzzy_match_found(msg):
        for phrase in target_phrases:
            for i in range(len(msg) - len(phrase) + 1):
                window = msg[i:i+len(phrase)+5]
                if fuzz.partial_ratio(phrase, window) >= match_threshold:
                    print("Found match of : '" + phrase + "' with '" + window + "'")
                    return True
        return False

    df["is_scene_dead_mention"] = df["message"].apply(fuzzy_match_found)

    # Count mentions per quarter and per month
    quarterly_counts = df[df["is_scene_dead_mention"]].groupby("quarter").size()
    monthly_counts = df[df["is_scene_dead_mention"]].groupby("month").size()

    # Plot both curves
    plt.figure(figsize=(14, 7))
    monthly_counts.sort_index().plot(label="Monthly", color="blue", marker="o")
    quarterly_counts.sort_index().plot(label="Quarterly", color="red", linewidth=2)
    plt.title("Occurrence of '" + target_phrases[0] + "' (and variations)")
    plt.xlabel("Time")
    plt.ylabel("Number of mentions")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, output_png))
    plt.close()

    df[df["is_scene_dead_mention"]].to_csv(
    os.path.join(output_folder, "occurence_bbs_scene_is_dead_mentions.csv"),
    index=False,
    columns=["datetime", "message"]
    )

    print(f"Monthly and quarterly overlay curve saved to {output_folder}")

# Exemple d'appel
fuzzy_occurence(
    meme_array_scene_is_dead,
    "occurence_bbs_scene_is_dead_monthly_quarterly.png"
)
