import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Paths
input_folder = "./pouet_users"
output_folder = "./stats"
output_image_cumulative = os.path.join(output_folder, "users_cumulative.png")
output_image_monthly = os.path.join(output_folder, "users_monthly_new.png")

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

# Store all registration dates
register_dates = []

# Iterate over JSON files
for filename in os.listdir(input_folder):
    if filename.endswith(".json"):
        filepath = os.path.join(input_folder, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                reg_date_str = data.get("user", {}).get("registerDate")
                if reg_date_str:
                    reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d %H:%M:%S")
                    register_dates.append(reg_date)
        except (json.JSONDecodeError, KeyError, ValueError):
            print(f"Skipping invalid file: {filename}")

# Convert to DataFrame
df = pd.DataFrame(register_dates, columns=["register_date"])
df.sort_values("register_date", inplace=True)
df["cumulative_users"] = range(1, len(df) + 1)

# Key events
key_events = {
    "2008 Financial Crisis": pd.to_datetime("2008-09-15"),
    "COVID-19 lockdown (Europe)": pd.to_datetime("2020-03-15"),
    "Youtube launch": pd.to_datetime("2005-04-23"),
    "Twitter launch": pd.to_datetime("2006-07-15"),
    "Discord popularity": pd.to_datetime("2015-06-01"),
    "Facebook launch": pd.to_datetime("2005-01-01"),
    "Facebook in Europe": pd.to_datetime("2008-01-01"),
    "Pouet.net v2": pd.to_datetime("2013-08-01")
}

# === Plot cumulative curve ===
plt.figure(figsize=(15, 8))
plt.plot(df["register_date"], df["cumulative_users"], linewidth=2)

for label, event_date in key_events.items():
    if df["register_date"].min() <= event_date <= df["register_date"].max():
        plt.axvline(event_date, color='red', linestyle='--', alpha=0.7)
        plt.text(event_date, plt.ylim()[1]*0.95, label, rotation=90, verticalalignment='top', fontsize=10, color='darkred')

plt.title("Cumulative Registered Users on Pouet.net (2000–Present)")
plt.xlabel("Date")
plt.ylabel("Total Registered Users")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_image_cumulative)
print(f"Cumulative graph saved to {output_image_cumulative}")

# === Plot monthly registrations (derivative) ===
df_monthly = df["register_date"].dt.to_period("M").value_counts().sort_index()
df_monthly.index = df_monthly.index.to_timestamp()

plt.figure(figsize=(15, 6))
plt.bar(df_monthly.index, df_monthly.values, width=20, color='steelblue', edgecolor='black')

for label, event_date in key_events.items():
    if df_monthly.index.min() <= event_date <= df_monthly.index.max():
        plt.axvline(event_date, color='red', linestyle='--', alpha=0.7)
        plt.text(event_date, plt.ylim()[1]*0.95, label, rotation=90, verticalalignment='top', fontsize=10, color='darkred')

plt.title("New Pouet.net Users per Month")
plt.xlabel("Date")
plt.ylabel("New Registered Users")
plt.grid(True, axis='y', linestyle=':')
plt.tight_layout()
plt.savefig(output_image_monthly)
print(f"Monthly registrations graph saved to {output_image_monthly}")
