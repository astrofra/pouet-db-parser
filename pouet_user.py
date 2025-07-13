import requests
import random
import time
import os

def fetch_user_nickname_from_id(cache_folder, user_id):
    cache_file_txt = os.path.join(cache_folder, f"{user_id}.txt")
    cache_file_json = os.path.join(cache_folder, f"{user_id}.json")

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
                    print(f"ID {user_id} not found!")
                    user_id_to_nick = f"ID {user_id}"
            else:
                print("response.status_code" + response.status_code)
                user_id_to_nick = f"ID {user_id}"
        except Exception:
            user_id_to_nick = f"ID {user_id}"

        delay = 5 + random.uniform(5, 10)
        print(f"Waiting {delay:.1f}s before next API call...")
        time.sleep(delay)

    return user_id_to_nick