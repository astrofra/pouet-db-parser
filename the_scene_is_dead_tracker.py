import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from rapidfuzz import fuzz

# Folders
input_folder = "./pouet_oneliners"
output_folder = "./stats"
os.makedirs(output_folder, exist_ok=True)

# Regex for valid oneliner lines
line_regex = re.compile(r"^(\d{2}:\d{2})\s+(.*?)\[(\d+)\]\s+:\s+(.*)$")

# Reference phrase to track
target_phrase = "the scene is dead"

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
df["quarter"] = df["datetime"].dt.to_period("Q")

# Fuzzy match logic
match_threshold = 80  # Percent similarity to consider a valid occurrence

def fuzzy_match_found(msg):
    for i in range(len(msg) - len(target_phrase) + 1):
        window = msg[i:i+len(target_phrase)+10]
        if fuzz.partial_ratio(target_phrase, window) >= match_threshold:
            return True
    return False

df["is_scene_dead_mention"] = df["message"].apply(fuzzy_match_found)

# Count mentions per quarter
quarterly_counts = df[df["is_scene_dead_mention"]].groupby("quarter").size()

# Plot
plt.figure(figsize=(12, 6))
quarterly_counts.sort_index().plot(marker="o")
plt.title("Quarterly occurrence of 'the scene is dead' variations (fuzzy matched)")
plt.xlabel("Quarter")
plt.ylabel("Number of mentions")
plt.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "scene_is_dead_quarterly.png"))
plt.close()

print(f"Quarterly 'scene is dead' curve saved to {output_folder}")
