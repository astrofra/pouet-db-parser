import random
import time
import json
import os
from pouet_user import fetch_user_nickname_from_id

# Constants
max_user_id = 108641
user_cache_folder = "./pouet_users"
not_found_file = "not_found_users.json"

os.makedirs(user_cache_folder, exist_ok=True)

# Load not-found cache
if os.path.exists(not_found_file):
    with open(not_found_file, "r", encoding="utf-8") as f:
        not_found_users = set(json.load(f))
else:
    not_found_users = set()

def save_not_found_cache():
    with open(not_found_file, "w", encoding="utf-8") as f:
        json.dump(sorted(not_found_users), f, indent=2)

# Main loop
try:
    while True:
        time.sleep(random.uniform(30, 120))  # between 30 seconds and 2 minutes

        next_user_id = random.randint(0, max_user_id)

        # Skip if already cached or known not to exist
        json_path = os.path.join(user_cache_folder, f"{next_user_id}.json")
        if os.path.exists(json_path) or next_user_id in not_found_users:
            continue

        user_found = fetch_user_nickname_from_id(user_cache_folder, next_user_id)

        if not user_found.isdigit():  # user exists
            print(f"✔ ID {next_user_id} exists (nickname: {user_found})")
            delay = 5 + random.uniform(0, 10)
            print(f"Waiting {delay:.1f}s before next API call...")
            time.sleep(delay)
        else:
            print(f"✘ ID {next_user_id} not found")
            not_found_users.add(next_user_id)
            save_not_found_cache()

except KeyboardInterrupt:
    print("\nInterrupted by user, saving state...")
    save_not_found_cache()