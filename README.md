# Document Rotation Detection

Automatische Erkennung des Rotationswinkels von gescannten Dokumenten (PDF, PNG, JPEG, etc.) mit OpenCV und Python.

## Features

- 🔍 Automatische Erkennung des Rotationswinkels
- 📄 **Mehrere Dateiformate**: PDF, PNG, JPEG, JPG, BMP, TIFF
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

# Dokument analysieren (PDF, PNG, JPEG, etc.)
python detect_rotation.py path/to/your/document.pdf
python detect_rotation.py path/to/your/image.png
python detect_rotation.py path/to/your/scan.jpg

# Mit Visualisierung
python detect_rotation.py path/to/your/document.pdf --visualize
```

**Unterstützte Formate:** PDF, PNG, JPEG, JPG, BMP, TIFF

### 2. GitHub Actions (Manuell)

1. Gehe zu: `Actions` → `PDF Rotation Detection` → `Run workflow`
2. Gib die Datei-URL ein (PDF, PNG, JPEG werden automatisch erkannt)
3. Optional: Aktiviere Visualisierung
4. Klicke auf `Run workflow`

### 3. N8N Integration (Beide Methoden: URL oder Base64)

Der Workflow unterstützt **zwei Methoden** zum Senden von Dateien:
- ✅ **URL-Methode**: Datei liegt bereits online (z.B. Cloud Storage)
- ✅ **Base64-Methode**: Datei direkt aus N8N hochladen/senden

**Unterstützte Formate:** PDF, PNG, JPEG, JPG, BMP, TIFF (automatische Erkennung)

#### Quick Start: Importiere fertigen Workflow

Importiere `n8n_workflow_flexible.json` in N8N für einen sofort einsatzbereiten Workflow mit **intelligenter Erkennung** beider Methoden.

#### Schritt 1: GitHub Personal Access Token erstellen

1. Gehe zu GitHub → Settings → Developer settings → Personal access tokens
2. Erstelle einen neuen Token mit den Berechtigungen:
   - `repo` (Full control of private repositories)
3. Kopiere den Token

#### Schritt 2: N8N Workflow erstellen (Manuelle Konfiguration)

**Empfehlung**: Verwende einen **Code Node** für flexible Unterstützung beider Methoden.

##### Code Node: "Smart Payload Builder"

```javascript
const json = $input.item.json;
const binary = $input.item.binary;

let payload = {
  event_type: "detect-rotation",
  client_payload: {
    visualize: json.visualize || false,
    callback_url: json.callback_url || ""
  }
};

// Automatische Erkennung: URL oder Base64?
if (json.pdf_url) {
  payload.client_payload.pdf_url = json.pdf_url;
} else if (binary && binary.data) {
  payload.client_payload.pdf_base64 = binary.data.data;
} else if (json.pdf_base64) {
  payload.client_payload.pdf_base64 = json.pdf_base64;
}

return { json: payload };
```

##### HTTP Request Node Konfiguration

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

**Body Content Type:** `JSON`

**Body (mit Code Node - Empfohlen):**
```json
={{ JSON.stringify($json) }}
```
> Der Code Node bereitet automatisch den richtigen Payload vor (URL oder Base64)

**Body (Ohne Code Node - Manuell):**
```json
{
  "event_type": "detect-rotation",
  "client_payload": {
    "pdf_url": "={{ $json.pdf_url }}",
    "pdf_base64": "={{ $json.pdf_base64 || ($binary.data ? $binary.data.data : undefined) }}",
    "visualize": "={{ $json.visualize || false }}",
    "callback_url": "={{ $json.callback_url || '' }}"
  }
}
```
> Beide Felder werden akzeptiert, GitHub Actions verwendet automatisch die richtige Methode

#### Verwendungsbeispiele

**Beispiel 1: Datei von URL laden (PDF, PNG, JPEG)**

Sende folgendes JSON an deinen N8N Webhook:
```json
{
  "pdf_url": "https://example.com/your-document.pdf",
  "visualize": false,
  "callback_url": "https://your-n8n-webhook.com/callback"
}
```

```json
{
  "pdf_url": "https://example.com/scan.png",
  "visualize": true,
  "callback_url": "https://your-n8n-webhook.com/callback"
}
```

**Beispiel 2: Datei als Base64 senden**

Sende folgendes JSON an deinen N8N Webhook:
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8P...",
  "visualize": true,
  "callback_url": "https://your-n8n-webhook.com/callback"
}
```

**Beispiel 3: Datei als Binary hochladen**

Sende ein Multipart-Form-Upload an deinen N8N Webhook:
```bash
curl -X POST https://your-n8n.app.n8n.cloud/webhook/pdf-rotation \
  -F "data=@document.pdf" \
  -F "visualize=false"

curl -X POST https://your-n8n.app.n8n.cloud/webhook/pdf-rotation \
  -F "data=@scan.png" \
  -F "visualize=true"
```

> **Detaillierte Anleitungen:**
> - `n8n_workflow_flexible.json` - Kompletter Workflow zum Importieren
> - `n8n_http_request_examples.md` - Schritt-für-Schritt Konfiguration
> - `N8N_BASE64_GUIDE.md` - Detaillierte Base64 Anleitung

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
  "needs_correction": true,
  "file_type": "image"
}
```

**Felder:**
- `median_angle`: Median-Rotationswinkel in Grad
- `mean_angle`: Durchschnittlicher Rotationswinkel
- `std_dev`: Standardabweichung der erkannten Winkel
- `lines_detected`: Anzahl der erkannten Linien
- `needs_correction`: Boolean - ob Korrektur empfohlen wird (> 0.5°)
- `file_type`: Erkannter Dateityp (`"pdf"` oder `"image"`)

## GitHub Actions Details

### Workflow Trigger

Der Workflow kann auf drei Arten gestartet werden:

1. **Manual (workflow_dispatch)**: Über die GitHub UI
2. **Repository Dispatch**: Von N8N oder anderen Tools
3. **API Call**: Direkt über die GitHub API

### Inputs

| Parameter | Typ | Beschreibung | Erforderlich |
|-----------|-----|--------------|--------------|
| `pdf_url` | String | URL zum PDF-Dokument | Nein* |
| `pdf_base64` | String | Base64-kodiertes PDF | Nein* |
| `visualize` | Boolean | Visualisierung erstellen | Nein (default: false) |
| `callback_url` | String | URL für Ergebnis-Callback | Nein |

*Mindestens eines von `pdf_url` oder `pdf_base64` muss angegeben werden

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

## Repository Dateien

| Datei | Beschreibung |
|-------|--------------|
| `detect_rotation.py` | Python-Script für Rotationserkennung |
| `requirements.txt` | Python Dependencies |
| `.github/workflows/rotation-detection.yml` | GitHub Actions Workflow (unterstützt URL + Base64) |
| `n8n_workflow_flexible.json` | ⭐ **Empfohlen**: Kompletter N8N Workflow mit intelligenter Erkennung |
| `n8n_workflow_complete.json` | Alternative N8N Workflow Variante |
| `n8n_http_request_examples.md` | 📖 Detaillierte Konfigurationsanleitung für N8N |
| `N8N_BASE64_GUIDE.md` | 📖 Schritt-für-Schritt Base64 Anleitung |
| `README.md` | Diese Datei |

### Welche Datei soll ich verwenden?

**Für schnellen Start:**
- Importiere `n8n_workflow_flexible.json` in N8N
- Konfiguriere dein GitHub Token
- Fertig! ✅

**Für manuelle Konfiguration:**
- Lies `n8n_http_request_examples.md`
- Folge der Schritt-für-Schritt Anleitung

**Für Base64-Details:**
- Lies `N8N_BASE64_GUIDE.md`
- Verstehe alle Optionen und Limits

## Lizenz

MIT

## Kontakt

Bei Fragen oder Problemen erstelle bitte ein Issue im Repository.
