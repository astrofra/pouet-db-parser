import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from rapidfuzz import fuzz
from meme_arrays import meme_array_scene_is_dead

def fuzzy_occurence(target_phrases, output_png):
    # Folders
    input_folder = "./pouet_oneliners"
    output_folder = "./stats"
    os.makedirs(output_folder, exist_ok=True)

    # Regex for valid oneliner lines
    line_regex = re.compile(r"^(\d{2}:\d{2})\s+(.*?)\[(\d+)\]\s+:\s+(.*)$")

    # List of phrases to track
    # # target_phrases = ["the scene is dead", "the scene died", "la scene est morte"]

    # Data storage
    data = []

    # Read all .txt files
    for filename in sorted(os.listdir(input_folder)):
        if filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                current_date = None
                for line in f:
                    line = line.strip()
                    if re.match(r"^\d{4}-\d{2}-\d{2}$", line):
                        current_date = line
                    else:
                        match = line_regex.match(line)
                        if match and current_date:
                            time_text, nickname, pouet_id, message = match.groups()
                            datetime_str = f"{current_date} {time_text}"
                            data.append({
                                "datetime": datetime_str,
                                "message": message.lower()
                            })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M")
    df = df.sort_values("datetime")
    df["quarter"] = df["datetime"].dt.to_period("Q")
    df["month"] = df["datetime"].dt.to_period("M")

    # Fuzzy match logic
    match_threshold = 97  # Percent similarity to consider a valid occurrence

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
    plt.title("Occurrence of '" + target_phrases[0] + '(...)' + "' variations (monthly & quarterly)")
    plt.xlabel("Time")
    plt.ylabel("Number of mentions")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, output_png))
    plt.close()

    df[df["is_scene_dead_mention"]].to_csv(
    os.path.join(output_folder, "occurence_scene_is_dead_mentions.csv"),
    index=False,
    columns=["datetime", "message"]
    )

    print(f"Monthly and quarterly overlay curve saved to {output_folder}")

fuzzy_occurence(meme_array_scene_is_dead, 
                "occurence_scene_is_dead_monthly_quarterly.png")
# fuzzy_occurence(["works on my machine", "works on my pc", "works on my computer", "works on my amiga"], "occurence_works_on_my_machine_quarterly.png")