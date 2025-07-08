import os
import re
import pandas as pd
from langdetect import detect, DetectorFactory, LangDetectException
import matplotlib.pyplot as plt

# Fix random seed for consistent language detection results
DetectorFactory.seed = 42

# Input and output folders
input_folder = "monthly_oneliners"
output_folder = "stats"
os.makedirs(output_folder, exist_ok=True)

# Regex pattern to match oneliner messages
line_regex = re.compile(r"^\d{2}:\d{2}\s+.*?\[\d+\]\s+:\s+(.*)$")

# Data storage
records = []

# Process each .txt file in the input folder
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".txt"):
        year_month = filename.replace(".txt", "")
        file_path = os.path.join(input_folder, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                match = line_regex.match(line)
                if match:
                    message = match.group(1)
                    try:
                        lang = detect(message)
                    except LangDetectException:
                        lang = "unknown"
                    records.append({
                        "month": year_month,
                        "message": message,
                        "lang": lang
                    })

# Convert to DataFrame
df = pd.DataFrame(records)

# Total number of messages per month
monthly_totals = df.groupby("month").size()

# Number of messages per language per month
lang_counts = df.groupby(["month", "lang"]).size().unstack(fill_value=0)

# Normalize to get proportions
lang_props = lang_counts.div(monthly_totals, axis=0)

# Plot
plt.figure(figsize=(16, 8))
for lang in lang_props.columns:
    if lang_props[lang].max() > 0.01:  # Only plot languages with some presence
        plt.plot(lang_props.index, lang_props[lang], label=lang)

plt.title("Monthly proportion of detected languages in Pouet Oneliner")
plt.xlabel("Month")
plt.ylabel("Proportion")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "lang_proportions_over_time.png"))
plt.close()

print("✅ Language detection stats saved in 'stats/lang_proportions_over_time.png'")
