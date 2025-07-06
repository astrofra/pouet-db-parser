
import os
import re
import time
import random
import requests
import pandas as pd
import matplotlib.pyplot as plt

def fetch_user_nickname_from_id(user_id):
    cache_file = os.path.join(user_cache_folder, f"{user_id}.txt")

    user_id_to_nick = None

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
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
                    with open(cache_file, "w", encoding="utf-8") as f:
                        f.write(nickname)
                else:
                    user_id_to_nick = f"ID {user_id}"
            else:
                user_id_to_nick = f"ID {user_id}"
        except Exception as e:
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

# Daily message count
daily_counts = df["day"].value_counts().sort_index()
plt.figure(figsize=(12, 6))
daily_counts.plot()
plt.title("Number of messages per day")
plt.xlabel("Date")
plt.ylabel("Number of messages")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "messages_per_day.png"))
plt.close()

print(f"Stats and graphs saved to {output_folder}")
