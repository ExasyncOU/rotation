# N8N HTTP Request - Beide Methoden

Diese Datei zeigt dir, wie du deinen bestehenden HTTP Request Node anpassen kannst, um **beide Methoden** zu unterstützen.

## Option 1: Einfacher Switch zwischen URL und Base64

### Variante A: Mit IF Node

```
Webhook → IF Node → HTTP Request (URL)
                  → HTTP Request (Base64)
```

**IF Node Bedingung:**
```
{{ $json.pdf_url !== undefined && $json.pdf_url !== "" }}
```

---

## Option 2: Code Node (Empfohlen - Flexibel)

Füge **VOR** deinem HTTP Request einen Code Node ein:

### Code Node: "Smart Payload Builder"

```javascript
// Intelligente Erkennung: URL oder Binary?
const items = $input.all();
const results = [];

for (const item of items) {
  const json = item.json;
  const binary = item.binary;

  let payload = {
    event_type: "detect-rotation",
    client_payload: {
      visualize: json.visualize || false,
      callback_url: json.callback_url || ""
    }
  };

  // Methode 1: PDF-URL wurde übergeben
  if (json.pdf_url) {
    console.log('Using URL method');
    payload.client_payload.pdf_url = json.pdf_url;
  }
  // Methode 2: Binary Daten (PDF-Upload)
  else if (binary && binary.data) {
    console.log('Using Base64 method from binary');
    payload.client_payload.pdf_base64 = binary.data.data;
  }
  // Methode 3: Base64 wurde direkt übergeben
  else if (json.pdf_base64) {
    console.log('Using Base64 method from json');
    payload.client_payload.pdf_base64 = json.pdf_base64;
  }
  else {
    throw new Error('Weder pdf_url noch pdf_base64 oder Binary-Daten gefunden!');
  }

  results.push({
    json: payload
  });
}

return results;
```

### HTTP Request Node Konfiguration

**URL:** `https://api.github.com/repos/ExasyncOU/rotation/dispatches`

**Method:** POST

**Authentication:** Header Auth
- Name: `Authorization`
- Value: `Bearer YOUR_GITHUB_TOKEN`

**Headers:**
```json
{
  "Accept": "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28"
}
```

**Body Content Type:** JSON

**Body:**
```json
={{ JSON.stringify($json) }}
```

> Der Code Node bereitet den Payload vor, der HTTP Request sendet ihn einfach weiter.

---

## Option 3: Direkt im HTTP Request (Ohne Code Node)

Falls du **keinen Code Node** verwenden möchtest:

### Body (JSON) mit Expression:

```json
{
  "event_type": "detect-rotation",
  "client_payload": {
    "pdf_url": "={{ $json.pdf_url || undefined }}",
    "pdf_base64": "={{ $json.pdf_base64 || $binary.data?.data || undefined }}",
    "visualize": "={{ $json.visualize || false }}",
    "callback_url": "={{ $json.callback_url || '' }}"
  }
}
```

> **Hinweis:** GitHub Actions ignoriert `undefined` Felder automatisch.

---

## Test-Beispiele

### Test 1: Mit URL

**POST zu deinem N8N Webhook:**

```bash
curl -X POST https://your-n8n.app.n8n.cloud/webhook/pdf-rotation \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/document.pdf",
    "visualize": false,
    "callback_url": "https://your-n8n.app.n8n.cloud/webhook/rotation-callback"
  }'
```

### Test 2: Mit Base64

**POST zu deinem N8N Webhook:**

```bash
PDF_BASE64=$(base64 -w 0 test.pdf)

curl -X POST https://your-n8n.app.n8n.cloud/webhook/pdf-rotation \
  -H "Content-Type: application/json" \
  -d "{
    \"pdf_base64\": \"$PDF_BASE64\",
    \"visualize\": true,
    \"callback_url\": \"https://your-n8n.app.n8n.cloud/webhook/rotation-callback\"
  }"
```

### Test 3: Mit Binary Upload

**POST mit File Upload:**

```bash
curl -X POST https://your-n8n.app.n8n.cloud/webhook/pdf-rotation \
  -F "data=@test.pdf" \
  -F "visualize=false" \
  -F "callback_url=https://your-n8n.app.n8n.cloud/webhook/rotation-callback"
```

---

## Dein aktueller Workflow - Anpassung

### Schritt 1: Ändere Body Content Type

**Vorher:**
- Content Type: `x-www-form-urlencoded` oder `Form Data`
- Body Parameters: Key-Value Paare

**Nachher:**
- Content Type: **JSON**
- Specify Body: **Using JSON**

### Schritt 2: Neuer Body (Beide Methoden)

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

### Schritt 3: Test

Sende eines der folgenden JSON-Objekte an deinen Webhook:

**Variante URL:**
```json
{
  "pdf_url": "https://example.com/test.pdf",
  "visualize": false
}
```

**Variante Base64:**
```json
{
  "pdf_base64": "JVBERi0xLjQKJeLjz9MK...",
  "visualize": true
}
```

---

## Workflow-Struktur Übersicht

### Einfache Version (mit Code Node)

```
┌─────────────┐      ┌──────────────────┐      ┌──────────────┐      ┌──────────┐
│   Webhook   │─────>│  Code Node       │─────>│ HTTP Request │─────>│ Response │
│ (PDF Input) │      │ (Smart Payload)  │      │  (GitHub)    │      │          │
└─────────────┘      └──────────────────┘      └──────────────┘      └──────────┘
```

### Komplexe Version (mit IF)

```
┌─────────────┐      ┌──────────┐      ┌──────────────┐      ┌──────────┐
│   Webhook   │─────>│ IF Node  │─────>│ HTTP (URL)   │─────>│ Response │
│ (PDF Input) │      │          │      └──────────────┘      │          │
└─────────────┘      └──────────┘                            └──────────┘
                            │
                            └─────>┌──────────────┐
                                   │ HTTP (Base64)│─────>
                                   └──────────────┘
```

---

## Empfehlung

Verwende die **Code Node Methode** weil:
- ✅ Automatische Erkennung der Methode
- ✅ Bessere Fehlerbehandlung
- ✅ Einfacher zu debuggen
- ✅ Nur ein HTTP Request Node nötig
- ✅ Flexible Erweiterung möglich

---

## Debugging

### Aktiviere Console Logs

Im Code Node siehst du in den Logs:
```
Using URL method
```
oder
```
Using Base64 method from binary
```

### Prüfe GitHub Actions

Nach dem Request:
1. Gehe zu https://github.com/ExasyncOU/rotation/actions
2. Schaue dir den neuesten Workflow Run an
3. Im "Prepare PDF" Step siehst du:
   - "Downloading PDF from: ..." (bei URL)
   - "Decoding PDF from Base64..." (bei Base64)
