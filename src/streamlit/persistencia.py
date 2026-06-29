import json
import os

PANELES_FILE = ".paneles_cache.json"


def cargar_paneles():
    if os.path.exists(PANELES_FILE):
        try:
            with open(PANELES_FILE) as f:
                paneles = json.load(f)
            changed = False
            next_id = 1
            for p in paneles:
                if "uid" not in p:
                    p["uid"] = next_id
                    next_id += 1
                    changed = True
            if changed:
                guardar_paneles(paneles)
            return paneles
        except (json.JSONDecodeError, OSError):
            return []
    return []


def guardar_paneles(paneles):
    try:
        with open(PANELES_FILE, "w") as f:
            json.dump(paneles, f, indent=2)
    except OSError:
        pass
