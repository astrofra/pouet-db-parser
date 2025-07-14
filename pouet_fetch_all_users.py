# Download all Pouet user data
import random
import time
from pouet_user import fetch_user_nickname_from_id
import os

max_user_amount = 26875
max_user_id = 108641

user_cache_folder = "./pouet_users"
os.makedirs(user_cache_folder, exist_ok=True)

complete = False

while complete is False:
    time.sleep(random.uniform(120, 240))
    next_user_id = int(random.uniform(0, max_user_id))
    user_found = fetch_user_nickname_from_id(user_cache_folder, next_user_id)
    if not user_found.isdigit(): # we found an actual nickname/user
        delay = 5 + random.uniform(0, 10)
        print(f"Waiting {delay:.1f}s before next API call...")
        time.sleep(delay)

        print(f"ID {next_user_id} found!")
    else:
        print(f"no user found!")

    l = os.listdir(user_cache_folder)
    