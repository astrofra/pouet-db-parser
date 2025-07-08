import os
import re
from collections import Counter
import matplotlib.pyplot as plt
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Fix random seed to make language detection deterministic
DetectorFactory.seed = 0

# Folders
input_folder = "./monthly_oneliners"
output_folder = "./stats"
os.makedirs(output_folder, exist_ok=True)

# Regex to detect message lines: HH:MM nickname[ID] : message
line_regex = re.compile(r"^(\d{2}:\d{2})\s+.*?\[\d+\]\s+:\s+(.*)$")

language_counter = Counter()
total_messages = 0
detected_messages = 0

for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".txt"):
        filepath = os.path.join(input_folder, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                match = line_regex.match(line)
                if match:
                    message = match.group(2)
                    total_messages += 1
                    try:
                        lang = detect(message)
                        language_counter[lang] += 1
                        detected_messages += 1
                    except LangDetectException:
                        language_counter["unknown"] += 1

# Display results
print(f"Total messages: {total_messages}")
print(f"Detected language for: {detected_messages}")

# Save pie chart
labels = list(language_counter.keys())
sizes = list(language_counter.values())

plt.figure(figsize=(10, 8))
plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
plt.axis("equal")
plt.title("Language distribution in Pouet Oneliners")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "language_distribution.png"))
plt.close()

print(f"Language distribution chart saved to {output_folder}")
