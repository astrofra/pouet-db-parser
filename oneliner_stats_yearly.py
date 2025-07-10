import os
import re
import time
import random
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Folders
input_folder = "./pouet_oneliners"
output_folder = "./stats"
user_cache_folder = "./pouet_users"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(user_cache_folder, exist_ok=True)

# Regex for valid oneliner lines
line_regex = re.compile(r"^(\d{2}:\d{2})\s+(.*?)\[(\d+)\]\s+:\s+(.*)$")

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
                            "date": current_date,
                            "time": time_text,
                            "nickname": nickname,
                            "pouet_id": int(pouet_id),
                            "message": message
                        })

# Convert to DataFrame
df = pd.DataFrame(data)
df["datetime"] = pd.to_datetime(df["datetime"], format="%Y-%m-%d %H:%M")
df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.to_period("M")
df["day"] = df["datetime"].dt.date

daily_counts = df["day"].value_counts().sort_index()
rolling_counts = daily_counts.rolling(window=60, center=True).mean()
rolling_median = daily_counts.rolling(window=60, center=True).median()
rolling_std = daily_counts.rolling(window=60, center=True).std()

key_events = {    "Breakpoint 2008": pd.to_datetime("2008-03-21")   }
revision_dates = {
    2011: "2011-04-22", 2012: "2012-04-06", 2013: "2013-03-29", 2014: "2014-04-18",
    2015: "2015-04-03", 2016: "2016-03-25", 2017: "2017-04-14", 2018: "2018-03-30",
    2019: "2019-04-19", 2020: "2020-04-10", 2021: "2021-04-02", 2022: "2022-04-15",
    2023: "2023-04-07", 2024: "2024-03-29"
}
for year in range(1997, 2026):
    key_events[f"Evoke {year}"] = pd.to_datetime(f"{year}-08-15")
for year, date_str in revision_dates.items():
    key_events[f"Revision {year}"] = pd.to_datetime(date_str)

# Fix global Y scale based on the max daily count
y_max = 150.0

for year in range(2000, 2026):
    start = pd.to_datetime(f"{year}-01-01")
    end = pd.to_datetime(f"{year}-12-31")

    y_counts = daily_counts[(daily_counts.index >= start.date()) & (daily_counts.index <= end.date())]
    y_roll = rolling_counts[(rolling_counts.index >= start.date()) & (rolling_counts.index <= end.date())]
    y_median = rolling_median[(rolling_median.index >= start.date()) & (rolling_median.index <= end.date())]
    y_std = rolling_std[(rolling_std.index >= start.date()) & (rolling_std.index <= end.date())]

    if len(y_counts) == 0:
        continue

    fig, ax = plt.subplots(figsize=(18, 9))
    y_counts.plot(ax=ax, label="Raw daily count", alpha=0.4)
    y_roll.plot(ax=ax, label="60d rolling avg", color="red")
    y_median.plot(ax=ax, label="60d median", color="orange")
    y_std.plot(ax=ax, label="60d std dev", color="green", alpha=0.5)

    ax.set_ylim(0, y_max)

    for label, date in key_events.items():
        if start <= date <= end:
            ax.axvline(date, color="purple", linestyle="--", linewidth=0.8, alpha=0.6)
            ax.text(date, ax.get_ylim()[1]*0.9, label, rotation=90, va='top', fontsize=10, color="purple")

    ax.set_title(f"Oneliner message activity in {year}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages per day")
    ax.legend()
    fig.tight_layout()
    fig.savefig(f"stats/oneliner_activity_{year}.png")
    plt.close()

print("One PNG per year generated (2000–2025)")
