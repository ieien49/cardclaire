#!/usr/bin/env python3
"""Convertit l'export CSV de la table Pool de Grist en pool.json.

Usage :  python convertir_pool.py Pool.csv pool.json

Colonnes reconnues (celles de ton Pool Grist) :
  Source, Album, Numero, Rarete, Titre, Extrait, Image, Url, Debut
Colonne facultative :
  Gid  -> à créer dans Grist (colonne formule  $id) avant l'export ; si elle existe,
          elle sert d'identifiant. Sinon les cartes sont numérotées 1, 2, 3... dans l'ordre du fichier.
"""
import csv, json, re, sys

CHAMPS = ["Source", "Album", "Numero", "Rarete", "Titre", "Extrait", "Image", "Url", "Debut"]


def date_iso(v):
    v = (v or "").strip()
    m = re.fullmatch(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", v)       # JJ/MM/AAAA
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return v[:10] if re.match(r"\d{4}-\d{2}-\d{2}", v) else ""


def main(src, dst):
    with open(src, newline="", encoding="utf-8-sig") as f:
        lignes = list(csv.DictReader(f))
    if not lignes:
        sys.exit("CSV vide")
    manquantes = [c for c in ("Source", "Titre") if c not in lignes[0]]
    if manquantes:
        sys.exit("Colonnes absentes du CSV : " + ", ".join(manquantes))

    sortie, vus = [], set()
    for i, l in enumerate(lignes, 1):
        o = {}
        gid = (l.get("Gid") or "").strip()
        o["id"] = int(gid) if gid.isdigit() else i
        if o["id"] in vus:
            sys.exit(f"Identifiant en double : {o['id']}")
        vus.add(o["id"])
        for c in CHAMPS:
            v = (l.get(c) or "").strip()
            if c == "Numero":
                o[c] = int(v) if v.isdigit() else ""
            elif c == "Debut":
                o[c] = date_iso(v)
            else:
                o[c] = v
        if o["Rarete"] not in ("commune", "rare", "legendaire"):
            o["Rarete"] = "commune"
        sortie.append(o)

    with open(dst, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=1)
    print(f"{len(sortie)} cartes écrites dans {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
