# N8N Integration mit Base64-PDF

Diese Anleitung zeigt, wie du PDF-Dateien direkt als Base64 an GitHub Actions sendest.

## Methode 1: PDF-Datei direkt hochladen (Empfohlen)

### Workflow-Struktur

```
Webhook (PDF Upload) → Convert to Base64 → HTTP Request (GitHub) → Webhook (Result)
```

### Schritt-für-Schritt Anleitung

#### 1. Webhook Node (PDF Upload)
- **Node Type:** Webhook
- **HTTP Method:** POST
- **Path:** `pdf-upload`
- **Response Mode:** Last Node

**Wichtig:** Aktiviere "Binary Data" in den Optionen

#### 2. Code Node (Base64 Encoding)

Füge einen **Code Node** ein:

```javascript
// Hole die Binary-Daten aus dem Webhook
const binaryData = items[0].binary.data;

if (!binaryData) {
  throw new Error('Keine PDF-Datei gefunden');
}

// Konvertiere zu Base64
const base64String = binaryData.data;

// Rückgabe für nächsten Node
return [{
  json: {
    pdf_base64: base64String,
    visualize: items[0].json.visualize || false,
    callback_url: "https://DEINE-N8N-INSTANCE.app.n8n.cloud/webhook/rotation-result"
  }
}];
```

#### 3. HTTP Request Node (GitHub Trigger)

**URL:**
```
https://api.github.com/repos/ExasyncOU/rotation/dispatches
```

**Method:** POST

**Authentication:** Header Auth
- **Name:** `Authorization`
- **Value:** `Bearer YOUR_GITHUB_TOKEN`

**Headers:**
```json
{
  "Accept": "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28"
}
```

**Body (JSON):**
```json
{
  "event_type": "detect-rotation",
  "client_payload": {
    "pdf_base64": "={{ $json.pdf_base64 }}",
    "visualize": "={{ $json.visualize }}",
    "callback_url": "={{ $json.callback_url }}"
  }
}
```

#### 4. Webhook Node (Result Callback)

- **Node Type:** Webhook
- **HTTP Method:** POST
- **Path:** `rotation-result`
- **Response Code:** 200

**Output:** Empfängt JSON mit Rotationsdaten

---

## Methode 2: Einfache Variante mit HTTP Request Node

### Für Node-Version 4.3+

Wenn du bereits eine PDF als Binary hast:

**HTTP Request Node Konfiguration:**

**Body Parameters (als JSON):**
```json
{
  "event_type": "detect-rotation",
  "client_payload": {
    "pdf_base64": "={{ $binary.data.data }}",
    "visualize": false,
    "callback_url": "https://your-webhook-url.com/callback"
  }
}
```

---

## Methode 3: PDF von URL (Einfachste Variante)

Falls die PDF bereits online verfügbar ist:

**HTTP Request Node:**

**Body:**
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

---

## Test mit CURL

### Test 1: Mit Base64

```bash
# PDF zu Base64 konvertieren
PDF_BASE64=$(base64 -w 0 your-document.pdf)

# Request senden
curl -X POST https://api.github.com/repos/ExasyncOU/rotation/dispatches \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d "{
    \"event_type\": \"detect-rotation\",
    \"client_payload\": {
      \"pdf_base64\": \"$PDF_BASE64\",
      \"visualize\": true
    }
  }"
```

### Test 2: Mit URL

```bash
curl -X POST https://api.github.com/repos/ExasyncOU/rotation/dispatches \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  -d '{
    "event_type": "detect-rotation",
    "client_payload": {
      "pdf_url": "https://example.com/document.pdf",
      "visualize": false,
      "callback_url": "https://webhook.site/your-unique-id"
    }
  }'
```

---

## Wichtige Hinweise

### Größenbeschränkungen

- **GitHub API Limit:** Max. 1 MB pro Request
- **Für größere PDFs:** Verwende die URL-Methode oder upload zu Cloud Storage

### Base64 Größe berechnen

Base64 ist ca. 33% größer als das Original:
```
Original PDF: 750 KB → Base64: ~1000 KB (zu groß!)
Original PDF: 500 KB → Base64: ~665 KB (OK)
```

### Callback URL Format

Die Callback URL muss öffentlich erreichbar sein:
- ✅ `https://your-n8n.app.n8n.cloud/webhook/result`
- ✅ `https://webhook.site/unique-id` (für Tests)
- ❌ `http://localhost:5678/webhook/result` (nicht erreichbar)

---

## Debugging

### GitHub Actions Logs ansehen

1. Gehe zu: https://github.com/ExasyncOU/rotation/actions
2. Klicke auf den neuesten Workflow Run
3. Schaue dir die Logs an

### Häufige Fehler

**"Error: Neither pdf_url nor pdf_base64 provided"**
- Stelle sicher, dass `client_payload` korrekt formatiert ist
- Prüfe die JSON-Syntax

**"Error: input.pdf not created"**
- Base64 String ist ungültig oder leer
- PDF ist möglicherweise korrupt

**"Bad credentials"**
- GitHub Token ist falsch oder abgelaufen
- Token hat nicht die `repo` Berechtigung

---

## Ergebnis-Format

GitHub Actions sendet folgendes JSON an die Callback URL:

```json
{
  "median_angle": -2.34,
  "mean_angle": -2.41,
  "std_dev": 5.67,
  "lines_detected": 142,
  "needs_correction": true
}
```

### Felder Erklärung

- `median_angle`: Rotationswinkel in Grad (negativ = gegen Uhrzeigersinn)
- `mean_angle`: Durchschnittswinkel aller erkannten Linien
- `std_dev`: Standardabweichung (hoher Wert = inkonsistente Linien)
- `lines_detected`: Anzahl erkannter Linien im Dokument
- `needs_correction`: true wenn |angle| > 0.5°

---

## Vollständiges N8N Workflow Beispiel

Importiere `n8n_workflow_complete.json` in N8N für ein vollständiges Beispiel.

**Features:**
- PDF Upload via Webhook
- Automatische Base64 Konvertierung
- GitHub Actions Trigger
- Ergebnis-Empfang via Callback
- Fehlerbehandlung
