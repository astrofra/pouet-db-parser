import os
import matplotlib.pyplot as plt
from collections import defaultdict

BASE_DIR = r"X:\ftp.scene.org\parties"
STATS_DIR = "stats"
os.makedirs(STATS_DIR, exist_ok=True)

# Data containers
year_party_count = {}
year_file_count = defaultdict(int)
year_total_size = defaultdict(int)

for year_name in sorted(os.listdir(BASE_DIR)):
    year_path = os.path.join(BASE_DIR, year_name)
    if not os.path.isdir(year_path):
        continue
    try:
        year = int(year_name)
    except ValueError:
        continue

    party_folders = [f for f in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, f))]
    year_party_count[year] = len(party_folders)

    for party in party_folders:
        party_path = os.path.join(year_path, party)
        for root, _, files in os.walk(party_path):
            for file in files:
                try:
                    full_path = os.path.join(root, file)
                    year_file_count[year] += 1
                    year_total_size[year] += os.path.getsize(full_path)
                except OSError:
                    continue

year_total_size_mb = {year: size / (1024 * 1024) for year, size in year_total_size.items()}

# Sort all years
all_years = sorted(set(year_party_count) | set(year_file_count) | set(year_total_size_mb))

# Values aligned by year
parties = [year_party_count.get(y, 0) for y in all_years]
files = [year_file_count.get(y, 0) for y in all_years]
sizes = [year_total_size_mb.get(y, 0.0) for y in all_years]

# Plot with multiple y-axes
fig, ax1 = plt.subplots(figsize=(14, 6))

# First axis: number of parties
ax1.plot(all_years, parties, 'b-', label='Number of Parties')
ax1.set_ylabel('Number of Parties', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# # Second axis: number of files
# ax2 = ax1.twinx()
# ax2.plot(all_years, files, 'g-', label='Number of Files')
# ax2.set_ylabel('Number of Files', color='g')
# ax2.tick_params(axis='y', labelcolor='g')

# Third axis: total size in MB
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('axes', 1.1))  # Offset the third y-axis
ax3.plot(all_years, sizes, 'r-', label='Total Size (MB)')
ax3.set_ylabel('Total Size (MB)', color='r')
ax3.tick_params(axis='y', labelcolor='r')

# Grid and title
ax1.set_xlabel('Year')
plt.title('Demoparty Archives: Number of Parties, Files, and Total Size per Year')
ax1.grid(True)

# Save to file
plt.tight_layout()
plt.savefig(os.path.join(STATS_DIR, "demoparty_stats_combined.png"))
plt.close()

print("✅ Combined stats chart saved to stats/demoparty_stats_combined.png")
