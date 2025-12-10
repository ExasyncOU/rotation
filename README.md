# PDF Rotation Detection

Automatische Erkennung des Rotationswinkels von gescannten PDF-Dokumenten mit OpenCV und Python.

## Features

- 🔍 Automatische Erkennung des Rotationswinkels
- 📊 Visualisierung der erkannten Linien
- 🚀 GitHub Actions Integration
- 🔗 N8N Workflow Integration
- 📦 Bereitstellung der Ergebnisse als JSON

## Technologie-Stack

- **Python 3.11**
- **OpenCV** - Bildverarbeitung und Kantenerkennung
- **PyMuPDF** - PDF-Verarbeitung
- **NumPy** - Numerische Berechnungen
- **GitHub Actions** - CI/CD und Automatisierung

## Verwendung

### 1. Lokale Verwendung

```bash
# Dependencies installieren
pip install -r requirements.txt

# PDF analysieren
python detect_rotation.py path/to/your/document.pdf

# Mit Visualisierung
python detect_rotation.py path/to/your/document.pdf --visualize
```

### 2. GitHub Actions (Manuell)

1. Gehe zu: `Actions` → `PDF Rotation Detection` → `Run workflow`
2. Gib die PDF-URL ein
3. Optional: Aktiviere Visualisierung
4. Klicke auf `Run workflow`

### 3. N8N Integration

#### Schritt 1: GitHub Personal Access Token erstellen

1. Gehe zu GitHub → Settings → Developer settings → Personal access tokens
2. Erstelle einen neuen Token mit den Berechtigungen:
   - `repo` (Full control of private repositories)
3. Kopiere den Token

#### Schritt 2: N8N Workflow erstellen

Verwende den **HTTP Request Node** mit folgenden Einstellungen:

**URL:**
```
https://api.github.com/repos/ExasyncOU/rotation/dispatches
```

**Method:** `POST`

**Authentication:** `Header Auth`
- Name: `Authorization`
- Value: `Bearer YOUR_GITHUB_TOKEN`

**Headers:**
```json
{
  "Accept": "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28"
}
```

**Body (JSON) - Option 1: Mit URL**
```json
{
  "event_type": "detect-rotation",
  "client_payload": {
    "pdf_url": "https://example.com/your-document.pdf",
    "visualize": false,
    "callback_url": "https://your-n8n-webhook.com/callback"
  }
}
```

**Body (JSON) - Option 2: Mit Base64 (für direkte PDF-Uploads)**
```json
{
  "event_type": "detect-rotation",
  "client_payload": {
    "pdf_base64": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8P...",
    "visualize": false,
    "callback_url": "https://your-n8n-webhook.com/callback"
  }
}
```

> **Hinweis:** Die Base64-Methode ist ideal, wenn du PDFs direkt aus N8N hochlädst.
> Siehe `N8N_BASE64_GUIDE.md` für detaillierte Anleitung.

#### Schritt 3: Callback empfangen (Optional)

Um die Ergebnisse direkt zurückzuerhalten:

1. Erstelle einen **Webhook Node** in N8N
2. Kopiere die Webhook-URL
3. Füge die URL als `callback_url` im Body ein
4. GitHub Actions sendet die Ergebnisse automatisch zurück

### Beispiel N8N Workflow

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Trigger   │─────>│ HTTP Request │─────>│   Webhook   │
│  (Webhook)  │      │   (GitHub)   │      │  (Receive)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            v
                     Repository Dispatch
                            │
                            v
                    GitHub Actions läuft
                            │
                            v
                     POST zu callback_url
```

## Ausgabe

Das Script gibt ein JSON-Objekt zurück:

```json
{
  "median_angle": -2.34,
  "mean_angle": -2.41,
  "std_dev": 5.67,
  "lines_detected": 142,
  "needs_correction": true
}
```

**Felder:**
- `median_angle`: Median-Rotationswinkel in Grad
- `mean_angle`: Durchschnittlicher Rotationswinkel
- `std_dev`: Standardabweichung der erkannten Winkel
- `lines_detected`: Anzahl der erkannten Linien
- `needs_correction`: Boolean - ob Korrektur empfohlen wird (> 0.5°)

## GitHub Actions Details

### Workflow Trigger

Der Workflow kann auf drei Arten gestartet werden:

1. **Manual (workflow_dispatch)**: Über die GitHub UI
2. **Repository Dispatch**: Von N8N oder anderen Tools
3. **API Call**: Direkt über die GitHub API

### Inputs

| Parameter | Typ | Beschreibung | Erforderlich |
|-----------|-----|--------------|--------------|
| `pdf_url` | String | URL zum PDF-Dokument | Ja |
| `visualize` | Boolean | Visualisierung erstellen | Nein (default: false) |
| `callback_url` | String | URL für Ergebnis-Callback | Nein |

### Artifacts

Die Workflow-Ergebnisse werden als Artifacts gespeichert:
- `output.txt` - Komplettes Log
- `*_lines_detected.jpg` - Visualisierung (falls aktiviert)
- `input.pdf` - Das verarbeitete PDF

Artifacts sind 7 Tage verfügbar unter: `Actions` → Workflow Run → `Artifacts`

## Fehlerbehebung

### Keine Linien erkannt

Wenn "Keine Linien gefunden!" angezeigt wird:
- Das PDF könnte zu niedrige Auflösung haben
- Das PDF könnte bereits stark gedreht sein
- Versuche `visualize=true` für Debugging

### GitHub Actions schlägt fehl

1. Prüfe, ob die PDF-URL öffentlich zugänglich ist
2. Prüfe die Logs unter `Actions` → Workflow Run
3. Stelle sicher, dass das PDF nicht zu groß ist (< 50 MB empfohlen)

## Entwicklung

### Lokales Testing

```bash
# Virtual environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Tests durchführen
python detect_rotation.py test.pdf --visualize
```

### Workflow lokal testen

Mit [act](https://github.com/nektos/act):

```bash
act repository_dispatch -e test-event.json
```

## Lizenz

MIT

## Kontakt

Bei Fragen oder Problemen erstelle bitte ein Issue im Repository.
