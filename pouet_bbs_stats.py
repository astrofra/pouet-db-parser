import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

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
                topic = json.load(f)
                posts = topic.get("posts", [])
                for post in posts:
                    timestamp_str = post.get("timestamp")
                    if timestamp_str:
                        try:
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            data.append({
                                "datetime": timestamp,
                                "date": timestamp.date(),
                                "time": timestamp.time(),
                                "nickname": post.get("user_nick", "unknown"),
                                "pouet_id": int(post.get("user_id", -1)),
                                "message": post.get("content", "")
                            })
                        except ValueError:
                            print(f"Invalid timestamp: {timestamp_str}")
            except json.JSONDecodeError:
                print(f"Invalid JSON file: {filename}")

# Convert to DataFrame
df = pd.DataFrame(data)
df["year"] = df["datetime"].dt.year
df["month"] = df["datetime"].dt.to_period("M")
df["day"] = df["datetime"].dt.date

# Define key events to annotate
key_events = {
    "Breakpoint 2008": pd.to_datetime("2008-03-21"),
    "2008 Financial Crisis": pd.to_datetime("2008-09-15"),
    "COVID-19 lockdown (Europe)": pd.to_datetime("2020-03-15"),
    "Demoscene recognized in France (PCI)": pd.to_datetime("2025-02-01"),
    "Youtube launch": pd.to_datetime("2005-04-23"),
    "Twitter launch": pd.to_datetime("2006-07-15"),
    "Discord popularity": pd.to_datetime("2015-06-01"),
    "Facebook in Europe": pd.to_datetime("2008-01-01"),
    "Pouet.net v2": pd.to_datetime("2013-08-01")
}

# Daily message count with 60-day rolling average and key events
daily_counts = df["day"].value_counts().sort_index()
rolling_counts = daily_counts.rolling(window=60, center=True).mean()
rolling_std_counts = daily_counts.rolling(window=60, center=True).std()
rolling_median_counts = daily_counts.rolling(window=60, center=True).median()

# Compute median and detect spikes
median_daily = daily_counts.median()
spike_threshold = 7 * median_daily
spike_days = daily_counts[daily_counts >= spike_threshold]

# # Add spike days to key_events if not near existing
# for date, count in spike_days.items():
#     is_near_existing_event = any(abs(pd.to_datetime(date) - ed) <= timedelta(days=15) for ed in key_events.values())
#     if not is_near_existing_event:
#         label = f"({date})"
#         key_events[label] = pd.to_datetime(date)

# Plotting
fig, ax = plt.subplots(figsize=(18, 6))
daily_counts.plot(ax=ax, label="Raw daily count", alpha=0.5)
rolling_counts.plot(ax=ax, label="60-day rolling average", color="red", linewidth=2)
rolling_median_counts.plot(ax=ax, label="60-day rolling median", color="yellow", linewidth=1.5)
rolling_std_counts.plot(ax=ax, label="60-day rolling std dev", color="green", linewidth=1)

# Annotate key events
for label, date in key_events.items():
    if daily_counts.index.min() <= date.date() <= daily_counts.index.max():
        ax.axvline(date, color="purple", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.text(date, ax.get_ylim()[1]*0.95, label, rotation=90, verticalalignment='top', fontsize=11, color="purple")

# X-axis formatting
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_title("BBS message activity per day with 60-day smoothing")
ax.set_xlabel("Date")
ax.set_ylabel("Number of messages")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(output_folder, "bbs_messages_per_day.png"))
plt.close()

print(f"Stats and graphs saved to {output_folder}")
