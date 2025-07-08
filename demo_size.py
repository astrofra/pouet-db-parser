import os
import matplotlib.pyplot as plt
from collections import defaultdict

# Path to the root of scene.org parties archive
BASE_DIR = r"X:\ftp.scene.org\parties"
STATS_DIR = "stats"

# Create stats directory if it doesn't exist
os.makedirs(STATS_DIR, exist_ok=True)

# Data structures
year_party_count = {}  # Number of party folders per year
year_file_count = defaultdict(int)  # Total number of files per year
year_total_size = defaultdict(int)  # Total size of files (in bytes) per year

# Walk through each year folder
for year_name in sorted(os.listdir(BASE_DIR)):
    year_path = os.path.join(BASE_DIR, year_name)
    if not os.path.isdir(year_path):
        continue
    try:
        year = int(year_name)
    except ValueError:
        continue  # Skip non-numeric folders

    party_folders = [f for f in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, f))]
    year_party_count[year] = len(party_folders)

    for party in party_folders:
        party_path = os.path.join(year_path, party)
        for root, _, files in os.walk(party_path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    year_file_count[year] += 1
                    year_total_size[year] += os.path.getsize(filepath)
                except OSError:
                    continue  # Skip unreadable files

# Convert byte size to MB
year_total_size_mb = {year: size / (1024 * 1024) for year, size in year_total_size.items()}

# Plotting function
def plot_and_save(data_dict, ylabel, title, filename):
    years = sorted(data_dict.keys())
    values = [data_dict[year] for year in years]

    plt.figure(figsize=(12, 6))
    plt.plot(years, values, marker='o')
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(STATS_DIR, filename))
    plt.close()

# Generate plots
plot_and_save(year_party_count, "Number of parties", "Number of demoparties per year", "demoparties_per_year.png")
plot_and_save(year_file_count, "Number of files", "Number of files per year (in party folders)", "files_per_year.png")
plot_and_save(year_total_size_mb, "Total size (MB)", "Total size of files per year", "size_per_year.png")

print("Stats generated in 'stats/' folder.")
