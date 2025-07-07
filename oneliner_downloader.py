import os
import time
import random
import requests
from bs4 import BeautifulSoup
import datetime

# === CONFIGURATION ===
output_dir = "pouet_oneliners"  # Folder where text files will be stored
base_delay = 15//4  # Base delay (in seconds)
random_jitter = 30//4  # Maximum additional random seconds
max_pages = 11618  # Total known number of pages to download

# Fake browser User-Agent to look more human-like
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/114.0.0.0 Safari/537.36"
    )
}

# Create output folder if it does not exist
os.makedirs(output_dir, exist_ok=True)

# Check for already downloaded pages to resume automatically
existing_files = sorted([
    int(f.split(".")[0]) for f in os.listdir(output_dir) if f.endswith(".txt") and f.split(".")[0].isdigit()
])

# Determine the starting page
start_page = existing_files[-1] + 1 if existing_files else 1

# initialize a start time:
script_start_time = time.time()

# Main loop to download pages
for page_num in range(start_page, max_pages + 1):
    url = f"https://www.pouet.net/oneliner.php?page={page_num}"
    print(f"Downloading page {page_num}...")

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error {response.status_code} while fetching page {page_num}. Stopping.")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        
        output_lines = []  # List to store extracted lines
        
        # Locate the UL element containing oneliner entries
        boxlist = soup.find("ul", class_="boxlist")
        if not boxlist:
            print(f"Boxlist not found on page {page_num}.")
            continue
        
        for li in boxlist.find_all("li"):
            if "day" in li.get("class", []):
                # Date header
                output_lines.append(li.get_text(strip=True))
            else:
                # Classic oneliner entry
                time_tag = li.find("time")
                user_tag = li.find("a", class_="usera")
                
                if not time_tag or not user_tag:
                    continue  # Skip malformed lines
                
                # <li><time datetime='2000-10-04 18:30:26' title='2000-10-04 18:30:26'>18:30</time> <a href='user.php?who=1' class='usera' title="analogue">
                time_text = time_tag.get_text(strip=True)
                nickname = user_tag.get("title", "unknown")
                pouet_id = user_tag.get("href", "unknown").split('=')[1]
                
                # Extract oneliner text by removing time and avatar image
                text_parts = li.get_text(separator=" ", strip=True).split(' ', 1)
                message_text = text_parts[1] if len(text_parts) > 1 else ""

                output_lines.append(f"{time_text} {nickname}[{pouet_id}] : {message_text}")

        # Save the extracted lines to a text file
        output_path = os.path.join(output_dir, f"{page_num:05d}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(output_lines))

        # Randomized delay to mimic human browsing behavior
        jitter = random.uniform(0, random_jitter)
        for i in range(1, 3):
            jitter *= random.uniform(0.5, 1.0)
        actual_delay = max(1, base_delay + jitter)  # Prevent negative or too short delays

        # Calculate elapsed time and estimate remaining time
        elapsed_time = time.time() - script_start_time
        pages_done = page_num - start_page + 1
        pages_remaining = max_pages - page_num

        if pages_done > 0:
            avg_time_per_page = elapsed_time / pages_done
            est_remaining_seconds = avg_time_per_page * pages_remaining
            est_days = int(est_remaining_seconds // 86400)
            est_hours = int((est_remaining_seconds % 86400) // 3600)
            
            print(f"Estimated remaining time: {est_days} days {est_hours} hours.")

        print(f"Page {page_num} saved. Sleeping {actual_delay}s.")
        time.sleep(actual_delay)

    except KeyboardInterrupt:
        print("Manual interruption detected. Stopping.")
        break
    except Exception as e:
        print(f"Error while processing page {page_num}: {e}")
        break

print("Script completed or stopped.")
