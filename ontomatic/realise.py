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

def get(d, *keys, default=None):
    """Nested get with default."""
    cur = d
    for k in keys:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return default
    return cur

def to_str(x):
    if x is None:
        return ""
    if isinstance(x, (int, float)):
        return str(x)
    return f"{x}"

def safe_date(s):
    """Try to standardize to YYYY-MM-DD if possible."""
    if not s:
        return ""
    # accept YYYY, YYYY-MM, YYYY/MM/DD, etc.
    m = re.match(r"^(\d{4})(?:[-/](\d{1,2}))?(?:[-/](\d{1,2}))?", s)
    if not m:
        return s
    y = int(m.group(1))
    mm = int(m.group(2)) if m.group(2) else 1
    dd = int(m.group(3)) if m.group(3) else 1
    try:
        return datetime(y, mm, dd).strftime("%Y-%m-%d")
    except ValueError:
        return s

def norm_list(x):
    if not x:
        return []
    if isinstance(x, list):
        return x
    return [x]

# ----------- minimal heuristics -----------

def guess_logiciel_from_links(prod: dict):
    """Very rough hints from links/strings (no downloads)."""
    hints = []
    # platform name if present
    plat = get(prod, "platform") or {}
    plat_name = plat.get("name") if isinstance(plat, dict) else to_str(plat)
    if plat_name:
        hints.append(("plateforme", plat_name))
    # type (pc demo, 64k, etc.) sometimes present
    typ = prod.get("type") or prod.get("prodtype") or None
    if typ:
        hints.append(("type_oeuvre", to_str(typ)))
    # look at download/video fields to infer Windows/DOS/Amiga tiny hints
    for k in ("download", "downloadLink", "video", "youtube", "url"):
        v = to_str(prod.get(k, ""))
        if not v:
            continue
        if ".exe" in v or "windows" in v.lower():
            hints.append(("environnement_execution", "Windows (assumed)"))
        if "amiga" in v.lower() or ".adf" in v.lower() or ".lha" in v.lower():
            hints.append(("environnement_execution", "Amiga (assumed)"))
        if "dos" in v.lower():
            hints.append(("environnement_execution", "DOS (assumed)"))
    return hints

def map_collaborateurs(prod: dict):
    """Map Pouet 'credits' and 'groups' to collaborators (person/group)."""
    collabs = []
    # persons
    for c in norm_list(prod.get("credits")):
        name = c.get("name") or c.get("nick") or ""
        role = c.get("role") or ""
        if name:
            collabs.append({"personne": name, "role_dans_la_realisation": role, "collectif": ""})
    # groups
    for g in norm_list(prod.get("groups")):
        gname = g.get("name") or ""
        if gname:
            collabs.append({"personne": "", "role_dans_la_realisation": "groupe", "collectif": gname})
    return collabs

def map_logiciel_block(prod: dict):
    """Construct a minimal 'LOGICIEL' block with characteristics from hints."""
    hints = guess_logiciel_from_links(prod)
    carac = {
        "type_de_logiciel": "",
        "langage_de_programmation": "",
        "environnement_d_execution": "",
        "environnement_de_developpement": "",
        "version": "",
        "site_web": "",
        "licence_et_droits": "",
        "dates": [],
        "developpeur": ""
    }
    # apply hints
    for k, v in hints:
        if k == "environnement_execution" or k == "environnement_d_execution":
            carac["environnement_d_execution"] = v
        elif k == "type_oeuvre":
            # not a logiciel field, ignore here
            pass
        elif k == "plateforme":
            # map to env exec if nothing set yet
            if not carac["environnement_d_execution"]:
                carac["environnement_d_execution"] = v

    logiciel = {
        "nom_du_logiciel": "",
        "caracteristiques": carac,
        "data_appelees_par_le_logiciel": []
    }
    return logiciel

def map_equipement_block(prod: dict):
    """Rough 'EQUIPEMENT INFORMATIQUE' based on platform string."""
    plat = get(prod, "platform") or {}
    plat_name = plat.get("name") if isinstance(plat, dict) else to_str(plat)
    equip = {
        "type_de_machine": plat_name or "",
        "marque_modele": "",
        "systeme_exploitation_et_sp": "",
        "caracteristiques_du_systeme": "",
        "fabricant": "",
        "annee": ""
    }
    # very light heuristics
    if plat_name:
        if "amiga" in plat_name.lower():
            equip["systeme_exploitation_et_sp"] = "AmigaOS (assumed)"
        elif "pc" in plat_name.lower() or "windows" in plat_name.lower():
            equip["systeme_exploitation_et_sp"] = "Windows (assumed)"
        elif "dos" in plat_name.lower():
            equip["systeme_exploitation_et_sp"] = "MS-DOS (assumed)"
    return equip

def map_etapes_conception(prod: dict):
    """Pouet has no real 'design steps'; we derive a single coarse step from release date."""
    d = prod.get("releasedate") or prod.get("date") or ""
    step = {
        "date": safe_date(to_str(d)),
        "circonstance": "",
        "description": "Sortie (release) de la version connue via Pouet",
        "etat_d_avancee": "",
        "element_factuel": ""
    }
    return [step] if (step["date"] or step["description"]) else []

def map_architecture_and_functions(prod: dict):
    """Placeholders for 'Architecture de l'œuvre' and 'Fonctions'."""
    # We can use platform/type to fill something minimal.
    typ = prod.get("type") or prod.get("prodtype") or ""
    arch = "Architecture non spécifiée (données Pouet)"
    funs = []
    if typ:
        funs.append(f"type d’œuvre: {to_str(typ)}")
    return arch, funs

# ----------- main mapping -----------

def build_realisation(pouet_json: dict):
    """Map Pouet payload (which may have 'prod' root) to 'Réalisation' JSON."""
    prod = pouet_json.get("prod", pouet_json)

    # core
    date = safe_date(to_str(prod.get("releasedate") or prod.get("date") or ""))
    type_oeuvre = to_str(prod.get("type") or prod.get("prodtype") or "")

    architecture, fonctions = map_architecture_and_functions(prod)

    realisation = {
        "oeuvre_realisation": {
            "date": date,
            "type_d_oeuvre": type_oeuvre,
            "architecture_de_l_oeuvre": architecture,
            "fonctions_dans_l_oeuvre": fonctions,
            "logiciel": map_logiciel_block(prod),
            "equipement_informatique": map_equipement_block(prod),
            "collaborateurs": map_collaborateurs(prod),
            "etapes_de_la_conception": map_etapes_conception(prod),
            # The following branches exist in the reference graph but we keep them empty here:
            "production": {},
            "apports_exterieurs": []
        }
    }
    return realisation

# ----------- entrypoint -----------

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://api.pouet.net/v1/prod/?id=3054"
    data = http_get_json(url)
    if not data:
        sys.stderr.write("[error] no data\n")
        sys.exit(1)
    out = build_realisation(data)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
