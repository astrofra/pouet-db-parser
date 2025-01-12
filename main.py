import os
import json
import requests
import gzip
import shutil

SCENE_ORG_FTP_ROOT = "ftp://ftp.scene.org/"
SCENE_ORG_HTTP_ROOT = "https://files.scene.org/view/"

def fetch_data():
    response = requests.get('https://data.pouet.net/json.php')
    data = response.json()
    dumps = data['dumps']
    latest_date = max(dumps.keys())
    prods_url = dumps[latest_date]['prods']['url']
    filename = "_tmp/" + dumps[latest_date]['prods']['filename']
    response = requests.get(prods_url, stream=True)
    os.makedirs('_tmp', exist_ok=True)
    with open(filename, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    return filename

def parse_and_classify(filename, platforms, scene_org_local_copy, scene_org_roots):
    with gzip.open(filename, 'rt') as f:
        data = json.load(f)
    platform_dict = {platform: [] for platform in platforms}
    for prod in data['prods']:
        if prod['download']:
            # In case we find a direct link to ftp.scene.org...
            # we try to remap it to the local backup
            if prod['download'].find(SCENE_ORG_FTP_ROOT) > -1:
                for mirror_root in scene_org_roots:
                    if prod['download'].find(SCENE_ORG_FTP_ROOT + mirror_root) > -1:
                        local_link = prod['download'].replace(SCENE_ORG_FTP_ROOT + mirror_root, scene_org_local_copy)
                        local_link = local_link.replace("/", "\\")
                        prod['local_link'] = local_link
            elif prod['download'].find(SCENE_ORG_HTTP_ROOT) > -1:
                print(prod['download'])
                local_link = prod['download'].replace(SCENE_ORG_HTTP_ROOT, scene_org_local_copy)
                local_link = local_link.replace("/", "\\")
                prod['local_link'] = local_link

        for platform_key in prod['platforms']:
            platform = prod['platforms'][platform_key]
            if platform['name'] in platforms:
                platform_dict[platform['name']].append(prod)
    return platform_dict

def fetch_pouet_prods(platforms, scene_org_local_copy, scene_org_roots):
    filename = fetch_data()
    platform_dict = parse_and_classify(filename, platforms, scene_org_local_copy, scene_org_roots)
    os.makedirs('db', exist_ok=True)
    with open('db/prods.json', 'w') as f:
        json.dump(platform_dict, f, indent=2)

if __name__ == "__main__":
    platforms = ["Amstrad CPC", "Amiga AGA", "SNES/Super Famicom"]
    scene_org_local_copy = "X:\\ftp.scene.org\\"
    scene_org_roots = ["mirrors/hornet/", "pub/"]
    fetch_pouet_prods(platforms, scene_org_local_copy, scene_org_roots)
