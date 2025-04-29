# Migration von Replit zu GitHub Pages

Diese Anleitung beschreibt, wie der Torgau Jobs Feed von Replit zu GitHub Pages migriert werden kann.

## Warum migrieren?

1. **Zuverlässigkeit**: GitHub Pages ist eine zuverlässige und kostenlose Hostingplattform
2. **Automatisierung**: Mit GitHub Actions können wir den Feed automatisch aktualisieren
3. **Einfachheit**: Wir benötigen keine komplexe Webanwendung, sondern nur einen RSS-Feed

## Migrations-Schritte

### 1. Repository auf GitHub erstellen

1. Melden Sie sich bei GitHub an (oder erstellen Sie ein Konto unter [github.com](https://github.com/))
2. Erstellen Sie ein neues Repository (z.B. "torgau-jobs-feed")
3. Wählen Sie "Public" als Sichtbarkeit

### 2. Dateien hochladen

Laden Sie alle Dateien aus dem `github_migration`-Ordner in das neue Repository hoch:

- `torgau_feed_generator.py`: Der Feed-Generator
- `.github/workflows/daily-feed-update.yml`: GitHub Actions Workflow
- `docs/index.html`: Landing-Page für den Feed
- `README.md`: Projektbeschreibung

Sie können dies über die GitHub-Oberfläche oder mit Git tun:

```bash
git clone https://github.com/DEIN_USERNAME/torgau-jobs-feed.git
cd torgau-jobs-feed
# Kopieren Sie die Dateien in dieses Verzeichnis
git add .
git commit -m "Initial commit"
git push
```

### 3. GitHub Pages aktivieren

1. Gehen Sie zu den Repository-Einstellungen
2. Scrollen Sie zu "GitHub Pages"
3. Als Source wählen Sie "main" und "/docs" als Verzeichnis
4. Klicken Sie auf "Save"

### 4. Erste Ausführung des Feed-Generators

1. Gehen Sie zum Tab "Actions" in Ihrem Repository
2. Klicken Sie auf "Daily Feed Update" in der linken Seitenleiste
3. Klicken Sie auf "Run workflow" und dann auf den grünen Button
4. Warten Sie, bis der Workflow abgeschlossen ist (ca. 1-2 Minuten)

### 5. Feed überprüfen

Nach erfolgreicher Ausführung können Sie den Feed unter folgender URL abrufen:

```
https://DEIN_USERNAME.github.io/torgau-jobs-feed/job_feed.xml
```

Die Landing-Page ist verfügbar unter:

```
https://DEIN_USERNAME.github.io/torgau-jobs-feed/
```

## Anpassungen

### Feed-Konfiguration ändern

Um den Feed anzupassen, bearbeiten Sie die Variablen am Anfang der Datei `torgau_feed_generator.py`:

```python
# Feed-Konfiguration
FEED_TITLE = "Torgau Job Listings"
FEED_DESCRIPTION = "Aktuelle Stellenangebote in Torgau (04861) von der Arbeitsagentur"
FEED_LINK = "https://arbeitsagentur.de/"
FEED_LANGUAGE = "de"
```

### Suchparameter ändern

Um die Suchanfrage anzupassen, ändern Sie die Parameter in der `get_jobs_in_torgau`-Funktion:

```python
jobs = get_jobs_in_torgau(
    radius_km=30,  # Umkreis um Torgau in Kilometern
    days_back=14,  # Stellenangebote der letzten X Tage
    max_results=100  # Maximale Anzahl der Ergebnisse
)
```

### Aktualisierungsfrequenz ändern

Um die Häufigkeit der Feed-Aktualisierung zu ändern, bearbeiten Sie die cron-Zeile in `.github/workflows/daily-feed-update.yml`:

```yaml
schedule:
  # Täglich um 6:00 Uhr UTC ausführen (8:00 Uhr MESZ)
  - cron: '0 6 * * *'
```

Die cron-Syntax folgt dem Format: `Minute Stunde Tag Monat Wochentag`

## Unterstützung

Bei Fragen oder Problemen können Sie:

1. Ein Issue im GitHub-Repository erstellen
2. Die GitHub Actions Logs überprüfen, um Fehler zu identifizieren
3. Die GitHub-Dokumentation zu GitHub Pages und GitHub Actions konsultieren
