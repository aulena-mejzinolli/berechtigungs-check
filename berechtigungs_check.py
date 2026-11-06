"""
Berechtigungs-Check: findet inaktive Benutzerkonten und abgelaufene
temporäre Berechtigungen in einer CSV-Liste und gibt einen Bericht aus.

Aufruf:
    python berechtigungs_check.py benutzer.csv
    python berechtigungs_check.py benutzer.csv --tage 60 --stichtag 2026-11-06
"""

import argparse
import csv
from datetime import date, datetime

DATUMSFORMAT = "%Y-%m-%d"  # erwartetes Format, z. B. 2026-11-06


def lies_datum(text):
    """Wandelt Text in ein Datum um. Gibt None zurück, wenn das Feld leer ist.
    Wirft ValueError, wenn das Format falsch ist."""
    text = text.strip()
    if text == "":
        return None
    return datetime.strptime(text, DATUMSFORMAT).date()


def pruefe_benutzer(zeilen, stichtag, max_tage):
    """Prüft jede Zeile und sammelt die Befunde in drei Listen."""
    inaktiv = []         # zu lange kein Login oder noch nie eingeloggt
    abgelaufen = []      # temporäre Rolle ist abgelaufen, aber noch zugewiesen
    datenfehler = []     # Zeilen, die nicht sauber geprüft werden können

    for zeile in zeilen:
        benutzer = f"{zeile['benutzer_id']} ({zeile['name']}, {zeile['abteilung']})"

        # Gesperrte Konten sind schon behandelt, die überspringen wir.
        if zeile["status"].strip().lower() == "gesperrt":
            continue

        # 1) Letzter Login
        try:
            login = lies_datum(zeile["letzter_login"])
            if login is None:
                inaktiv.append(f"{benutzer}: noch nie angemeldet")
            else:
                tage = (stichtag - login).days
                if tage > max_tage:
                    inaktiv.append(f"{benutzer}: letzter Login vor {tage} Tagen ({login})")
        except ValueError:
            datenfehler.append(
                f"{benutzer}: Datum '{zeile['letzter_login']}' hat falsches Format (erwartet JJJJ-MM-TT)"
            )

        # 2) Temporäre Rolle
        rolle = zeile["temp_rolle"].strip()
        if rolle:
            try:
                bis = lies_datum(zeile["temp_gueltig_bis"])
                if bis is None:
                    datenfehler.append(f"{benutzer}: Rolle {rolle} ohne Ablaufdatum")
                elif bis < stichtag:
                    abgelaufen.append(f"{benutzer}: Rolle {rolle} war gültig bis {bis}")
            except ValueError:
                datenfehler.append(
                    f"{benutzer}: Ablaufdatum '{zeile['temp_gueltig_bis']}' hat falsches Format"
                )

    return inaktiv, abgelaufen, datenfehler


def drucke_abschnitt(titel, eintraege):
    print(f"\n{titel} ({len(eintraege)})")
    print("-" * len(titel))
    if not eintraege:
        print("  keine")
    for eintrag in eintraege:
        print(f"  - {eintrag}")


def main():
    parser = argparse.ArgumentParser(description="Prüft Benutzerkonten auf Inaktivität und abgelaufene Rollen.")
    parser.add_argument("datei", help="CSV-Datei mit Benutzerkonten")
    parser.add_argument("--tage", type=int, default=90, help="ab wie vielen Tagen ohne Login ein Konto inaktiv ist (Standard: 90)")
    parser.add_argument("--stichtag", help="Prüfdatum im Format JJJJ-MM-TT (Standard: heute)")
    args = parser.parse_args()

    stichtag = lies_datum(args.stichtag) if args.stichtag else date.today()

    with open(args.datei, newline="", encoding="utf-8") as f:
        zeilen = list(csv.DictReader(f))

    inaktiv, abgelaufen, datenfehler = pruefe_benutzer(zeilen, stichtag, args.tage)

    print(f"BERECHTIGUNGS-CHECK  Stichtag: {stichtag}  Grenze: {args.tage} Tage")
    print(f"Geprüfte Konten: {len(zeilen)}")
    drucke_abschnitt("Inaktive Konten: Sperrung prüfen", inaktiv)
    drucke_abschnitt("Abgelaufene temporäre Rollen: Entzug prüfen", abgelaufen)
    drucke_abschnitt("Datenfehler: manuell klären", datenfehler)
    print("\nHinweis: Der Bericht ist ein Vorschlag. Gesperrt oder entzogen wird erst nach Freigabe.")


if __name__ == "__main__":
    main()
