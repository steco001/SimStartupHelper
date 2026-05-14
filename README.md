# SimStartUpHelper

Startet Hilfsprogramme für Simulatoren und Spiele über konfigurierbare Profile.

## Starten

Doppelklick auf **SimStartUpHelper.exe**.

## Bedienung

### Profile

Beim ersten Start werden drei Profile angelegt: **Le Mans Ultimate**, **iRacing** und **Flight Simulator 24**.

| Schaltfläche | Funktion |
|---|---|
| `+` | Neues Profil erstellen |
| `✏` | Aktuelles Profil umbenennen |
| `Clone` | Aktuelles Profil klonen |
| `✕` | Aktuelles Profil löschen |

Das aktive Profil wird im Dropdown ausgewählt. Beim Wechsel werden alle laufenden Programme des vorherigen Profils automatisch beendet.

### Programme

Jedes Profil enthält eine Liste von Programmen. Pro Eintrag:

- **Name** — Anzeigename
- **Pfad** — Pfad zur `.exe` (Dateiauswahl über `...`)
- **Argumente** — optionale Kommandozeilenargumente (z.B. `-profile LMU`)
- **Delay** — Startverzögerung in Sekunden (0 = sofort)

| Schaltfläche | Funktion |
|---|---|
| `+ Hinzufügen` | Neues Programm zum Profil hinzufügen |
| `✏` | Programm bearbeiten |
| `✕` | Programm entfernen |

### Starten und Stoppen

- **▶ Profil starten** — startet alle Programme in Reihenfolge mit den konfigurierten Verzögerungen
- **■ Stoppen** — beendet alle laufenden Programme des Profils
- Der grüne Punkt (●) neben jedem Programm zeigt an, dass das Programm läuft

### System-Tray

Das App-Icon erscheint im Benachrichtigungsbereich (System-Tray). Über das Tray-Icon:

- **Doppelklick** oder **Rechtsklick → Öffnen** — Fenster wiederherstellen
- **Rechtsklick → Beenden** — alle Programme stoppen und App beenden

Das Schließen-Symbol (X) beendet die App vollständig.

## Datenspeicherung

Profile werden automatisch gespeichert unter:

```
%APPDATA%\SimStartUpHelper\profiles.json
```

## Entwicklung

Abhängigkeiten installieren:

```
pip install -r requirements.txt
```

Direkt aus dem Quellcode starten:

```
python main.py
```

Exe neu bauen:

```
python -m PyInstaller --noconsole --onefile --name SimStartUpHelper --icon assets/app.ico --distpath . SimStartUpHelper.pyw
```
