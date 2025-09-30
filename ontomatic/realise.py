#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Realisation extractor (ultra-simple, no classes).
- Fetch a Pouet JSON from URL (arg1 or default).
- Map available fields to a French "RÉALISATION DE L’ŒUVRE" structure.
- Heuristics kept minimal on purpose (no archive download).
"""

import json
import sys
import re
import os
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from datetime import datetime

# ----------- tiny helpers -----------

def http_get_json(url: str):
    """Fetch JSON from URL with a basic UA."""
    try:
        req = Request(url, headers={"User-Agent": "OntoMatic-Min/0.1"})
        with urlopen(req, timeout=30) as r:
            data = r.read()
        return json.loads(data.decode("utf-8", errors="replace"))
    except (HTTPError, URLError, TimeoutError) as e:
        sys.stderr.write(f"[error] cannot fetch {url}: {e}\n")
        return {}

def sanitize_filename(s: str):
    s = s.lower()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^a-z0-9\-_]", "_", s)
    return s.strip("_-")

# ----------- entrypoint -----------

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://api.pouet.net/v1/prod/?id=3054"
    data = http_get_json(url)
    if not data:
        sys.stderr.write("[error] no data\n")
        sys.exit(1)

    json_dump = json.dumps(data, ensure_ascii=False, indent=2)

    print(json_dump)

    extract = {
        "oeuvre_performance": {"evenement": {}}, 
        "oeuvre_realisation": {}, 
        "oeuvre_depot": {"referencement": {}}
        }
    extract["oeuvre_performance"]["titre_oeuvre"] = data["prod"]["name"]
    extract["oeuvre_realisation"]["type_oeuvre"] = data["prod"]["type"]
    extract["oeuvre_performance"]["evenement"]["dates_de_presentation"] = data["prod"]["releaseDate"]
    extract["oeuvre_performance"]["evenement"]["nom"] = data["prod"]["party"]["name"]
    extract["oeuvre_depot"]["referencement"]["identifiant"] = data["prod"]["id"]

    prod_id = extract["oeuvre_depot"]["referencement"]["identifiant"]
    title = extract["oeuvre_performance"]["titre_oeuvre"]
    filename = f"{prod_id}_{sanitize_filename(title)}.json"

    with open(os.path.join("ontomatic", "out", filename), "w", encoding="utf-8") as f:
        json.dump(extract, f, ensure_ascii=False, indent=2)

    # print(json.dumps(out, ensure_ascii=False, indent=2))
    # sys.stderr.write(f"[info] JSON saved to {filename}\n")

if __name__ == "__main__":
    main()
