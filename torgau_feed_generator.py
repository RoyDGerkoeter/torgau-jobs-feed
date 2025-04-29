import requests
import logging
from datetime import datetime
from feedgen.feed import FeedGenerator
import pytz
import json
import os

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def ensure_directory_exists(file_path):
    """Stellt sicher, dass das Verzeichnis für eine Datei existiert"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Verzeichnis erstellt: {directory}")

def load_seen_jobs():
    """Lädt die bereits gesehenen Job-IDs aus einer JSON-Datei"""
    ensure_directory_exists(SEEN_JOBS_FILE)
    try:
        if os.path.exists(SEEN_JOBS_FILE):
            with open(SEEN_JOBS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Fehler beim Laden der gesehenen Jobs: {str(e)}")
        return {}

def save_seen_jobs(seen_jobs):
    """Speichert die gesehenen Job-IDs in einer JSON-Datei"""
    ensure_directory_exists(SEEN_JOBS_FILE)
    try:
        with open(SEEN_JOBS_FILE, 'w') as f:
            json.dump(seen_jobs, f)
    except Exception as e:
        logger.error(f"Fehler beim Speichern der gesehenen Jobs: {str(e)}")

def get_jobs_in_torgau(radius_km=30, days_back=14, max_results=100):
    """Holt Jobs aus der Arbeitsagentur API für Torgau"""
    params = {
        "wo": "Torgau",
        "umkreis": radius_km,
        "veroeffentlichtseit": days_back,
        "size": max_results,
        "page": 1
    }
    
    try:
        logger.info(f"API-Anfrage mit Parametern: {params}")
        response = requests.get(API_URL, headers=API_HEADERS, params=params, timeout=(5, 30))
        response.raise_for_status()
        
        data = response.json()
        jobs = data.get('stellenangebote', [])
        logger.info(f"API-Antwort: {len(jobs)} Jobs gefunden")
        
        return jobs
    except Exception as e:
        logger.error(f"Fehler bei der API-Anfrage: {str(e)}")
        return []

def parse_date(date_str):
    """Parst ein Datum aus der API in ein datetime-Objekt"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=pytz.UTC)
    except (ValueError, TypeError):
        logger.warning(f"Konnte Datum nicht parsen: {date_str}, verwende aktuelles Datum")
        return datetime.now(pytz.UTC)

def update_feed(jobs):
    """Aktualisiert den RSS-Feed mit neuen Jobs"""
    # Feed-Generator initialisieren
    fg = FeedGenerator()
    fg.title(FEED_TITLE)
    fg.description(FEED_DESCRIPTION)
    fg.link(href=FEED_LINK, rel='alternate')
    fg.language(FEED_LANGUAGE)
    
    # Lade bekannte Jobs
    seen_jobs = load_seen_jobs()
    new_jobs_found = False
    
    for job in jobs:
        try:
            # Notwendige Daten extrahieren
            job_id = job.get('refnr', 'unknown')
            title = job.get('titel') or job.get('beruf') or "Stellenangebot in Torgau"
            
            # Publikationsdatum formatieren
            pub_date = parse_date(job.get('aktuelleVeroeffentlichungsdatum'))
            
            # Details für die Beschreibung zusammenstellen
            details = []
            
            # Grundlegende Job-Informationen
            details.append(f"<strong>Beruf:</strong> {job.get('beruf', 'N/A')}")
            details.append(f"<strong>Arbeitgeber:</strong> {job.get('arbeitgeber', 'N/A')}")
            
            # Ortsinformationen
            arbeitsort = job.get('arbeitsort', {})
            location = []
            if arbeitsort.get('plz'):
                location.append(arbeitsort.get('plz'))
            if arbeitsort.get('ort'):
                location.append(arbeitsort.get('ort'))
            if arbeitsort.get('region'):
                location.append(arbeitsort.get('region'))
            
            details.append(f"<strong>Ort:</strong> {' '.join(location)}")
            
            # Beschreibung hinzufügen, falls vorhanden
            if job.get('taetigkeitsbeschreibung'):
                details.append(f"<strong>Beschreibung:</strong> {job.get('taetigkeitsbeschreibung')}")
            
            # Weitere Details
            if job.get('arbeitszeitText'):
                details.append(f"<strong>Arbeitszeit:</strong> {job.get('arbeitszeitText')}")
            if job.get('befristungText'):
                details.append(f"<strong>Befristung:</strong> {job.get('befristungText')}")
            
            # Job-URL generieren
            job_url = job.get('externeUrl', f"https://www.arbeitsagentur.de/jobsuche/suche?id={job_id}")
            
            # Neuen Feed-Eintrag erstellen
            entry = fg.add_entry()
            entry.id(job_id)
            entry.title(title)
            entry.description("<br>".join(details))
            entry.link(href=job_url)
            entry.published(pub_date)
            entry.updated(pub_date)
            
            # Job als gesehen markieren
            if job_id not in seen_jobs:
                seen_jobs[job_id] = {
                    'title': title,
                    'first_seen': datetime.now().isoformat()
                }
                new_jobs_found = True
            
            logger.info(f"Job zum Feed hinzugefügt: {title} ({job_id})")
            
        except Exception as e:
            logger.error(f"Fehler beim Hinzufügen des Jobs zum Feed: {str(e)}")
    
    # Gesehene Jobs speichern, wenn neue gefunden wurden
    if new_jobs_found:
        save_seen_jobs(seen_jobs)
    
    # Feed-Datei speichern
    ensure_directory_exists(FEED_FILE)
    fg.rss_file(FEED_FILE, pretty=True)
    logger.info(f"Feed in {FEED_FILE} gespeichert")

if __name__ == "__main__":
    logger.info("Starte Torgau Jobs Feed Generator")
    
    # Jobs von der API holen
    jobs = get_jobs_in_torgau(radius_km=30, days_back=14, max_results=100)
    
    if jobs:
        # Feed aktualisieren
        update_feed(jobs)
        logger.info("Feed-Generierung abgeschlossen")
    else:
        logger.warning("Keine Jobs gefunden, Feed nicht aktualisiert")
