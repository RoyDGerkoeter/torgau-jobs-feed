# Torgau Jobs Feed Generator

Ein einfacher RSS-Feed-Generator für Stellenangebote in Torgau, der die Arbeitsagentur API verwendet.

## Übersicht

Dieses Projekt erstellt einen RSS-Feed mit aktuellen Stellenangeboten im Raum Torgau. Die Daten werden täglich von der offiziellen Arbeitsagentur JobSuche API abgerufen, gefiltert und als standardkonformer RSS-Feed bereitgestellt.

Der Feed wird automatisch täglich über GitHub Actions aktualisiert und ist öffentlich unter folgender URL verfügbar:

```
https://[dein-benutzername].github.io/torgau-jobs-feed/job_feed.xml
```

## Installation

Um das Projekt lokal zu verwenden:

1. Repository klonen:
   ```
   git clone https://github.com/[dein-benutzername]/torgau-jobs-feed.git
   cd torgau-jobs-feed
   ```

2. Abhängigkeiten installieren:
   ```
   pip install feedgen requests pytz
   ```

3. Feed-Generator ausführen:
   ```
   python torgau_feed_generator.py
   ```

## Konfiguration

Die Hauptkonfiguration erfolgt am Anfang der Datei `torgau_feed_generator.py`:

```python
# Feed-Konfiguration
FEED_TITLE = "Torgau Job Listings"
FEED_DESCRIPTION = "Aktuelle Stellenangebote in Torgau (04861) von der Arbeitsagentur"
FEED_LINK = "https://arbeitsagentur.de/"
FEED_LANGUAGE = "de"
FEED_FILE = "docs/job_feed.xml"
SEEN_JOBS_FILE = "data/seen_jobs.json"

# API-Konfiguration
API_URL = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/jobs"
API_HEADERS = {"X-API-Key": "jobboerse-jobsuche"}
```

Die Suchparameter können beim Aufruf der Funktion `get_jobs_in_torgau()` angepasst werden:

```python
jobs = get_jobs_in_torgau(
    radius_km=30,  # Umkreis um Torgau in Kilometern
    days_back=14,  # Stellenangebote der letzten X Tage
    max_results=100  # Maximale Anzahl der Ergebnisse
)
```

## Automatische Aktualisierung

Der Feed wird automatisch täglich um 6:00 Uhr UTC (8:00 Uhr MESZ) über GitHub Actions aktualisiert. Der Workflow ist in `.github/workflows/daily-feed-update.yml` definiert.

Sie können die Aktualisierung auch manuell über die GitHub-Oberfläche im "Actions"-Tab auslösen.

## Nutzung des Feeds

Der generierte RSS-Feed kann in jedem standardkonformen RSS-Reader abonniert werden. Einfach die URL des Feeds in den Reader einfügen:

```
https://[dein-benutzername].github.io/torgau-jobs-feed/job_feed.xml
```

### Integration in Websites

Der Feed kann auf verschiedene Arten in andere Websites eingebunden werden:

#### Methode 1: Direkter Link zum Feed

Bieten Sie einen direkten Link zum Abonnieren des Feeds an:

```html
<a href="https://[dein-benutzername].github.io/torgau-jobs-feed/job_feed.xml">
  Torgau Jobs abonnieren
</a>
```

#### Methode 2: Einbettung mit JavaScript

Sie können den Feed mit JavaScript einbetten, zum Beispiel mit der Bibliothek [RSS-Parser](https://github.com/rbren/rss-parser):

```html
<div id="torgau-jobs"></div>
<script src="https://cdn.jsdelivr.net/npm/rss-parser@3.12.0/dist/rss-parser.min.js"></script>
<script>
  const feedUrl = 'https://[dein-benutzername].github.io/torgau-jobs-feed/job_feed.xml';
  const CORS_PROXY = 'https://api.rss2json.com/v1/api.json?rss_url=';
  
  async function loadFeed() {
    try {
      const response = await fetch(CORS_PROXY + encodeURIComponent(feedUrl));
      const data = await response.json();
      
      if (data.status === 'ok') {
        let html = '<h2>Aktuelle Jobs in Torgau</h2><ul>';
        
        data.items.slice(0, 5).forEach(item => {
          html += `
            <li>
              <a href="${item.link}" target="_blank">${item.title}</a>
              <small>(${new Date(item.pubDate).toLocaleDateString()})</small>
            </li>
          `;
        });
        
        html += '</ul>';
        document.getElementById('torgau-jobs').innerHTML = html;
      }
    } catch (error) {
      console.error('Fehler beim Laden des Feeds:', error);
    }
  }
  
  loadFeed();
</script>
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe die LICENSE-Datei für Details.

## Disclaimer

Dieses Projekt ist nicht offiziell mit der Bundesagentur für Arbeit verbunden. Es handelt sich um eine inoffizielle Nutzung der öffentlich zugänglichen API.
