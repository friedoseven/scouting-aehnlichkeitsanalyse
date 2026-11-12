# Scouting-Ähnlichkeitsanalyse

Welche U23-Spieler aus kleineren Ligen (AUT, NED, BEL, DEN, 2. Bundesliga) haben ein ähnliches
statistisches Profil wie die Feldspieler von RB Leipzig?

Daten: FotMob (Saison 2026/27). Methode: 17 Kennzahlen pro 90 Minuten, z-Scores je Positionsgruppe,
Kosinus-Ähnlichkeit.

## Ausführen
```
pip install -r requirements.txt
python 01_daten_holen.py        # -> spielerdaten.csv
python 02_aehnlichkeit.py       # -> ergebnis/
python 03_grafiken.py --ref "Antonio Nusa" --kand "Carlos Forbs"
```
Falls FotMob den Abruf blockiert: `01_daten_holen_browser.js` auf fotmob.com in der Konsole ausführen.

Optionen für Schritt 2: `--max-alter` (23), `--min-minuten` (450), `--min-minuten-ref` (290), `--team`

Die Rohdaten sind nicht im Repo enthalten.
