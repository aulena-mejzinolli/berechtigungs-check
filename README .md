# Berechtigungs-Check

Kleines Python-Skript, das in einer Liste von Benutzerkonten zwei typische Risiken findet:

1. **Inaktive Konten:** Der letzte Login liegt länger als 90 Tage zurück, oder das Konto wurde noch nie benutzt.
2. **Abgelaufene temporäre Berechtigungen:** Eine befristete Rolle ist abgelaufen, aber noch zugewiesen.

Zusätzlich meldet das Skript **Datenfehler**, zum Beispiel ein falsches Datumsformat oder eine befristete Rolle ohne Ablaufdatum. Solche Zeilen werden nicht stillschweigend übersprungen, sondern zur manuellen Klärung ausgegeben.

## Warum das wichtig ist

Vergessene Konten und Rechte, die nie entzogen wurden, verstoßen gegen das Least-Privilege-Prinzip und sind ein Einfallstor für Missbrauch. Deshalb werden solche Kontrollen in Unternehmen regelmäßig durchgeführt (Bereinigungsroutinen).

## Nutzung

Benötigt nur Python 3, keine zusätzlichen Pakete.

```
python berechtigungs_check.py benutzer.csv
python berechtigungs_check.py benutzer.csv --tage 60
python berechtigungs_check.py benutzer.csv --stichtag 2026-11-06
```

## Aufbau der CSV

| Spalte | Bedeutung |
|---|---|
| benutzer_id | Benutzerkennung |
| name, abteilung | zur Einordnung im Bericht |
| status | aktiv oder gesperrt (gesperrte Konten werden übersprungen) |
| letzter_login | Datum JJJJ-MM-TT, leer = noch nie angemeldet |
| temp_rolle | befristete Rolle, leer = keine |
| temp_gueltig_bis | Ablaufdatum der befristeten Rolle |

Die Beispieldaten in `benutzer.csv` sind komplett erfunden.

## Beispielausgabe (Stichtag 2026-11-06)

```
BERECHTIGUNGS-CHECK  Stichtag: 2026-11-06  Grenze: 90 Tage
Geprüfte Konten: 8

Inaktive Konten: Sperrung prüfen (3)
  - U1002 (Ben Muster, Lager): letzter Login vor 178 Tagen (2026-05-12)
  - U1005 (Eva Demo, Personal): noch nie angemeldet
  - U1007 (Gina Fiktiv, Vertrieb): letzter Login vor 114 Tagen (2026-07-15)

Abgelaufene temporäre Rollen: Entzug prüfen (2)
  - U1003 (Clara Test, Buchhaltung): Rolle Z_FI_ZAHLUNG_FREIGABE war gültig bis 2026-09-30
  - U1007 (Gina Fiktiv, Vertrieb): Rolle Z_SD_PREISE_AENDERN war gültig bis 2026-08-15

Datenfehler: manuell klären (1)
  - U1008 (Hans Platzhalter, IT): Datum '15.10.2026' hat falsches Format (erwartet JJJJ-MM-TT)
```

## Bezug zu SAP

In SAP würde man diese Informationen über das Benutzerinformationssystem (Transaktion SUIM) auswerten. Das Skript bildet die Prüflogik vereinfacht mit einer CSV-Datei nach.

## Grenzen

- Das Skript schlägt nur vor. Gesperrt oder entzogen wird erst nach Freigabe durch die verantwortliche Stelle.
- Funktionstrennung (SoD) wird nicht geprüft.
- Keine echten Daten verwenden: Benutzerdaten sind personenbezogen (DSGVO).
