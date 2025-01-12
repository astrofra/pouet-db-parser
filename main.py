import os
import json
import requests
import gzip
import shutil

SCENE_ORG_FTP_ROOT = "ftp://ftp.scene.org/"
SCENE_ORG_HTTP_ROOT = "https://files.scene.org/view/"


def fetch_data():
    try:
        response = requests.get('https://data.pouet.net/json.php')
        response.raise_for_status()  # Did the request failed ?
        data = response.json()
    except requests.RequestException as e:
        print(f"Request failed : {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Cannot read JSON : {e}")
        return None

    dumps = data.get('dumps', {})
    if not dumps:
        print("No dump found in the https response.")
        return None

    latest_date = max(dumps.keys())
    prods_url = dumps[latest_date]['prods']['url']
    filename = "_tmp/" + dumps[latest_date]['prods']['filename']
    try:
        response = requests.get(prods_url, stream=True)
        response.raise_for_status()
        os.makedirs('_tmp', exist_ok=True)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
    except requests.RequestException as e:
        print(f"Error while downloading : {e}")
        return None
    return filename


def parse_and_classify(filename, platforms, scene_org_local_copy, scene_org_roots):
    try:
        with gzip.open(filename, 'rt') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading gzip file: {e}")
        return {}

    platform_dict = {platform: [] for platform in platforms}
    for prod in data.get('prods', []):
        if 'download' in prod:
            # Remap ftp.scene.org -> local backup
            if SCENE_ORG_FTP_ROOT in prod['download']:
                for mirror_root in scene_org_roots:
                    if SCENE_ORG_FTP_ROOT + mirror_root in prod['download']:
                        local_link = prod['download'].replace(SCENE_ORG_FTP_ROOT + mirror_root, scene_org_local_copy)
                        prod['local_link'] = local_link.replace("/", "\\")
            elif SCENE_ORG_HTTP_ROOT in prod['download']:
                local_link = prod['download'].replace(SCENE_ORG_HTTP_ROOT, scene_org_local_copy)
                prod['local_link'] = local_link.replace("/", "\\")

        for platform_key in prod.get('platforms', {}):
            platform = prod['platforms'][platform_key]
            if platform.get('name') in platforms:
                platform_dict[platform['name']].append(prod)
    return platform_dict


def save_platform_data(platform_dict):
    os.makedirs('db', exist_ok=True)
    for platform, prods in platform_dict.items():
        filename = f"db/{platform.replace('/', '_').replace(' ', '_').lower()}.json"
        with open(filename, 'w') as f:
            json.dump(prods, f, indent=2)
        print(f"Exported : {filename}")


def fetch_pouet_prods(platforms, scene_org_local_copy, scene_org_roots):
    filename = fetch_data()
    platform_dict = parse_and_classify(filename, platforms, scene_org_local_copy, scene_org_roots)
    save_platform_data(platform_dict)
    # os.makedirs('db', exist_ok=True)
    # with open('db/prods.json', 'w') as f:
    #     json.dump(platform_dict, f, indent=2)


if __name__ == "__main__":
    platforms = ["Amstrad CPC", "Amiga AGA", "SNES/Super Famicom"]
    scene_org_local_copy = "X:\\ftp.scene.org\\"
    scene_org_roots = ["mirrors/hornet/", "pub/"]
    fetch_pouet_prods(platforms, scene_org_local_copy, scene_org_roots)