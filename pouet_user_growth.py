import os
import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Paths
input_folder = "./pouet_users"
output_folder = "./stats"
output_image = os.path.join(output_folder, "users_cumulative.png")

# Ensure output directory exists
os.makedirs(output_folder, exist_ok=True)

# Store all registration dates
register_dates = []

# Iterate over JSON files in input_folder
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

# Plot
plt.figure(figsize=(15, 10))
plt.plot(df["register_date"], df["cumulative_users"], linewidth=2)

# Annotate key events
for label, event_date in key_events.items():
    if df["register_date"].min() <= event_date <= df["register_date"].max():
        plt.axvline(event_date, color='red', linestyle='--', alpha=0.7)
        plt.text(event_date, plt.ylim()[1]*0.95, label, rotation=90, verticalalignment='top', fontsize=12, color='darkred')

plt.title("Cumulative Registered Users on Pouet.net (2000–Present)")
plt.xlabel("Date")
plt.ylabel("Total Registered Users")
plt.grid(True)
plt.tight_layout()

# Save
plt.savefig(output_image)
print(f"Graph saved to {output_image}")
