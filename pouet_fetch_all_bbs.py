import os
import re
import time
import json
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Constants
OUTPUT_FOLDER = "./bbs"
LOG_FILE = os.path.join(OUTPUT_FOLDER, "bbs_index.log")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

BASE_URL = "https://www.pouet.net/topic.php?which={}&page={}"

HEADERS = {
    "User-Agent": (
        "AstrofraResearchBot/1.0 (+https://www.pouet.net/user.php?who=38632 ; contact: astrofra@gmail.com)"
    )
}



def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


def read_scraped_ids():
    if not os.path.isfile(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(int(line.split(";")[0]) for line in f if line.strip())


def log_scraped_topic(topic_id, filename_base):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{topic_id};{filename_base}\n")


def get_total_pages(soup):
    select = soup.find("select", {"name": "page"})
    if select:
        return max([int(o.text) for o in select.find_all("option")])
    return 1


def get_topic_title(soup):
    h2 = soup.select_one("#pouetbox_bbsview h2")
    return h2.text.strip() if h2 else "untitled"


def extract_posts(soup):
    posts = []
    for post_div in soup.find_all("div", class_="bbspost"):
        content_tag = post_div.find("div", class_="content")
        foot_tag = post_div.find("div", class_="foot")
        if not content_tag or not foot_tag:
            continue

        content = content_tag.get_text(separator="\n").strip()
        date_match = re.search(r"added on the\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", foot_tag.text)
        date_str = date_match.group(1) if date_match else "unknown"

        user_link = foot_tag.find("a", href=re.compile(r"user\.php\?who=\d+"))
        nickname = user_link.text.strip() if user_link else "unknown"
        user_id_match = re.search(r"who=(\d+)", user_link["href"]) if user_link else None
        user_id = user_id_match.group(1) if user_id_match else "?"

        posts.append({
            "timestamp": date_str,
            "user_nick": nickname,
            "user_id": user_id,
            "content": content
        })
    return posts


def save_topic_files(topic_id, creation_date, title, posts):
    date_str = creation_date.strftime("%Y-%m-%d")
    filename_base = f"{topic_id:05d}_{date_str}_{sanitize_filename(title)}"
    txt_path = os.path.join(OUTPUT_FOLDER, filename_base + ".txt")
    json_path = os.path.join(OUTPUT_FOLDER, filename_base + ".json")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"# Topic {topic_id} – {title}\n\n")
        for post in posts:
            f.write(f"{post['timestamp']} by {post['user_nick']}[{post['user_id']}]\n")
            f.write(post['content'] + "\n\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "topic_id": topic_id,
            "title": title,
            "creation_date": date_str,
            "posts": posts
        }, f, indent=2, ensure_ascii=False)

    return filename_base


def scrape_topic(topic_id):
    try:
        r = requests.get(BASE_URL.format(topic_id, 1), headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None, f"Skipped (HTTP {r.status_code})"

        soup = BeautifulSoup(r.text, "html.parser")
        total_pages = get_total_pages(soup)
        title = get_topic_title(soup)
        all_posts = extract_posts(soup)

        for page in range(2, total_pages + 1):
            print('.', end='')
            time.sleep(random.uniform(10, 30))
            r_page = requests.get(BASE_URL.format(topic_id, page), headers=HEADERS, timeout=10)
            soup_page = BeautifulSoup(r_page.text, "html.parser")
            all_posts += extract_posts(soup_page)

        if not all_posts:
            return None, "No posts found"

        creation_date = datetime.strptime(all_posts[0]['timestamp'], "%Y-%m-%d %H:%M:%S")
        filename_base = save_topic_files(topic_id, creation_date, title, all_posts)
        log_scraped_topic(topic_id, filename_base)
        return filename_base, None

    except Exception as e:
        return None, f"ERROR: {e}"


def format_eta(seconds):
    delta = timedelta(seconds=int(seconds))
    hours, remainder = divmod(delta.seconds, 3600)
    minutes = remainder // 60
    return f"{hours}h{minutes:02d}m"


def main(start_id=1, end_id=12872):
    scraped = read_scraped_ids()
    to_do = [i for i in range(start_id, end_id + 1) if i not in scraped]
    total = len(to_do)
    start_time = time.time()

    for idx, topic_id in enumerate(to_do, start=1):
        topic_start = time.time()
        filename, error = scrape_topic(topic_id)

        elapsed = time.time() - start_time
        avg_time = elapsed / idx
        remaining = total - idx
        eta = format_eta(avg_time * remaining)

        if filename:
            status = f"OK → {filename}"
        elif error:
            status = error
        else:
            status = "Unknown status"

        next_delay = int(random.uniform(20, 80))

        print(f"[{topic_id:05d}] {status} | Next query in {next_delay}s | {remaining} remaining | ETA ≈ {eta}")

        time.sleep(next_delay)


if __name__ == "__main__":
    main(start_id=8079, end_id=12880)
