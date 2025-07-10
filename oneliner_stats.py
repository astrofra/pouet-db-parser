import os
import re
import time
import random
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta

def fetch_user_nickname_from_id(user_id):
    cache_file_txt = os.path.join(user_cache_folder, f"{user_id}.txt")
    cache_file_json = os.path.join(user_cache_folder, f"{user_id}.json")

    user_id_to_nick = None

    if os.path.exists(cache_file_txt):
        with open(cache_file_txt, "r", encoding="utf-8") as f:
            nickname = f.read().strip()
        user_id_to_nick = nickname
    else:
        try:
            url = f"https://api.pouet.net/v1/user/?id={user_id}"
            response = requests.get(url)
            if response.status_code == 200:
                json_data = response.json()
                if json_data.get("success") and "user" in json_data:
                    nickname = json_data["user"].get("nickname", f"ID {user_id}")
                    user_id_to_nick = nickname

                    # Save nickname
                    with open(cache_file_txt, "w", encoding="utf-8") as f:
                        f.write(nickname)

                    # Save full JSON data
                    with open(cache_file_json, "w", encoding="utf-8") as f:
                        f.write(response.text)
                else:
                    user_id_to_nick = f"ID {user_id}"
            else:
                user_id_to_nick = f"ID {user_id}"
        except Exception:
            user_id_to_nick = f"ID {user_id}"

        delay = 5 + random.uniform(0, 3)
        print(f"Waiting {delay:.1f}s before next API call...")
        time.sleep(delay)

    return user_id_to_nick


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

# Identify top users
user_counts_global = df["pouet_id"].value_counts().head(20)
top_user_ids = user_counts_global.index.tolist()

# Resolve nicknames with caching
user_id_to_nick = {}
for user_id in top_user_ids:
    user_id_to_nick[user_id] = fetch_user_nickname_from_id(user_id)

# Global histogram
plt.figure(figsize=(10, 6))
labels = [f"{user_id_to_nick.get(uid, f'ID {uid}')} [{uid}]" for uid in user_counts_global.index]
plt.bar(labels, user_counts_global.values)
plt.title("Top 20 most active users (global)")
plt.ylabel("Number of messages")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "top20_global.png"))
plt.close()

# Yearly histograms
for year in sorted(df["year"].unique()):
    yearly_df = df[df["year"] == year]
    year_counts = yearly_df["pouet_id"].value_counts().head(20)

    for user_id in year_counts.index:
        user_id_to_nick[user_id] = fetch_user_nickname_from_id(user_id)
    
    plt.figure(figsize=(10, 6))
    labels = [f"{user_id_to_nick.get(uid, f'ID {uid}')} [{uid}]" for uid in year_counts.index]
    plt.bar(labels, year_counts.values)
    plt.title(f"Top 20 most active users - {year}")
    plt.ylabel("Number of messages")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_folder, f"top20_{year}.png"))
    plt.close()

# Define key events to annotate
key_events = {
    # Sociopolitical / global context
    "Breakpoint 2008": pd.to_datetime("2008-03-21"),
    "2008 Financial Crisis": pd.to_datetime("2008-09-15"),
    "COVID-19 lockdown (Europe)": pd.to_datetime("2020-03-15"),
    "Demoscene recognized in France (PCI)": pd.to_datetime("2024-02-01"),

    # Platform shifts
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

# Filter spike days
spike_days = daily_counts[daily_counts >= spike_threshold]

# Add to key_events only if spike is not within 15 days of existing event
for date, count in spike_days.items():
    is_near_existing_event = False
    for existing_date in key_events.values():
        if abs(pd.to_datetime(date) - existing_date) <= timedelta(days=15):
            is_near_existing_event = True
            break
    if not is_near_existing_event:
        label = f"({date})"
        key_events[label] = pd.to_datetime(date)

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

# Set x-axis ticks to every 6 months, format them as 'YYYY-MM'
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

# Optional: rotate for readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

ax.set_title("Number of messages per day with 60-day smoothing")
ax.set_xlabel("Date")
ax.set_ylabel("Number of messages")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(output_folder, "messages_per_day.png"))
plt.close()

# Weekly user activity (Top 20 users globally)
active_users_max = 8
df["week"] = df["datetime"].dt.to_period("W").apply(lambda r: r.start_time)

weekly_counts = df[df["pouet_id"].isin(top_user_ids[:active_users_max])].groupby(["week", "pouet_id"]).size().unstack(fill_value=0)
weekly_counts = weekly_counts[top_user_ids[:active_users_max]]
labels = [f"{user_id_to_nick.get(uid, f'ID {uid}')} [{uid}]" for uid in top_user_ids[:active_users_max]]

plt.figure(figsize=(20, 8))
for idx, uid in enumerate(top_user_ids[:active_users_max]):
    weekly_mean_counts = weekly_counts.rolling(window=30, center=True).mean()
    plt.plot(weekly_mean_counts.index, weekly_mean_counts[uid], label=labels[idx])

plt.title(f"Weekly activity of the {active_users_max} most active users (30-day rolling mean)")
plt.xlabel("Week")
plt.ylabel("Number of messages")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_folder, f"weekly_activity_top{active_users_max}.png"))
plt.close()

print(f"Stats and graphs saved to {output_folder}")
