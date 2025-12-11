import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
import sys
import os
import json
import mimetypes

def get_file_type(file_path):
    """
    Erkennt den Dateityp anhand der Dateiendung und MIME-Type
    """
    # Versuche anhand der Dateiendung
    ext = os.path.splitext(file_path)[1].lower()

    if ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']:
        return 'image'

    # Fallback: MIME-Type prüfen
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        if mime_type == 'application/pdf':
            return 'pdf'
        elif mime_type.startswith('image/'):
            return 'image'

    # Default: Versuche als Bild zu laden
    return 'image'

def load_image_from_file(file_path):
    """
    Lädt ein Bild aus verschiedenen Dateiformaten (PDF, PNG, JPEG, etc.)
    Gibt ein RGB numpy array zurück
    """
    file_type = get_file_type(file_path)

    if file_type == 'pdf':
        print(f"Lade PDF-Datei: {file_path}")
        print("Konvertiere PDF zu Bild...")

        # PDF öffnen und erste Seite konvertieren
        doc = fitz.open(file_path)
        page = doc[0]  # Erste Seite

        # Konvertiere zu Pixmap (Bild) mit hoher Auflösung
        mat = fitz.Matrix(2, 2)  # 2x Zoom für bessere Qualität
        pix = page.get_pixmap(matrix=mat)

        # Konvertiere zu numpy array
        img_data = pix.samples
        image = np.frombuffer(img_data, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

        # Wenn RGBA, konvertiere zu RGB
        if pix.n == 4:
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        elif pix.n == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        doc.close()

    else:
        print(f"Lade Bilddatei: {file_path}")

        # Bild direkt mit OpenCV laden
        image = cv2.imread(file_path)

        if image is None:
            raise ValueError(f"Konnte Bilddatei nicht laden: {file_path}")

        # OpenCV lädt in BGR, konvertiere zu RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image

def detect_rotation_angle(file_path, create_visualization=False):
    """
    Erkennt den Rotationswinkel eines gescannten Dokuments (PDF, PNG, JPEG, etc.)

    Args:
        file_path: Pfad zur Datei (PDF, PNG, JPEG, JPG, BMP, TIFF)
        create_visualization: Ob eine Visualisierung erstellt werden soll

    Returns:
        Dictionary mit Rotationsergebnissen oder None bei Fehler
    """
    print(f"Analysiere Datei: {file_path}")

    # Lade Bild (automatische Erkennung ob PDF oder Bilddatei)
    try:
        image = load_image_from_file(file_path)
    except Exception as e:
        print(f"Fehler beim Laden der Datei: {e}")
        return None

    # In Graustufen konvertieren
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    print(f"Bildgröße: {gray.shape}")

    # Kanten erkennen
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Hough-Linien-Transformation
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100,
                            minLineLength=100, maxLineGap=10)

    if lines is None:
        print("Keine Linien gefunden!")
        return None

    # Winkel aller Linien berechnen
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        # Winkel berechnen (in Grad)
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))

        # Normalisiere auf -45 bis 45 Grad
        # (da horizontale Linien entweder ~0° oder ~180° sein können)
        if angle < -45:
            angle += 90
        elif angle > 45:
            angle -= 90

        angles.append(angle)

    # Median-Winkel verwenden (robuster gegen Ausreißer)
    median_angle = np.median(angles)
    mean_angle = np.mean(angles)

    print(f"\nErgebnisse:")
    print(f"  Anzahl erkannter Linien: {len(lines)}")
    print(f"  Median-Winkel: {median_angle:.2f}°")
    print(f"  Durchschnitts-Winkel: {mean_angle:.2f}°")
    print(f"  Standard-Abweichung: {np.std(angles):.2f}°")

    # Visualisierung erstellen
    if create_visualization:
        # Kleinere Version für Visualisierung
        scale = 0.3
        vis_image = cv2.resize(image, None, fx=scale, fy=scale)

        # Linien einzeichnen
        for line in lines:
            x1, y1, x2, y2 = line[0]
            x1, y1, x2, y2 = int(x1*scale), int(y1*scale), int(x2*scale), int(y2*scale)
            cv2.line(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 1)

        # Speichern (Dateiendung durch _lines_detected.jpg ersetzen)
        base_name = os.path.splitext(file_path)[0]
        output_path = f"{base_name}_lines_detected.jpg"
        cv2.imwrite(output_path, cv2.cvtColor(vis_image, cv2.COLOR_RGB2BGR))
        print(f"\nVisualisierung gespeichert: {output_path}")

    return {
        "median_angle": float(median_angle),
        "mean_angle": float(mean_angle),
        "std_dev": float(np.std(angles)),
        "lines_detected": int(len(lines)),
        "needs_correction": bool(abs(median_angle) > 0.5),
        "file_type": get_file_type(file_path)
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python detect_rotation.py <file_path> [--visualize]")
        print("Supported formats: PDF, PNG, JPEG, JPG, BMP, TIFF")
        sys.exit(1)

    file_path = sys.argv[1]
    visualize = "--visualize" in sys.argv

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    result = detect_rotation_angle(file_path, create_visualization=visualize)

    if result is not None:
        print(f"\n{'='*50}")
        print(f"ERGEBNIS: Das Dokument ist um {result['median_angle']:.2f}° geneigt")
        print(f"{'='*50}")

        if result['needs_correction']:
            print(f"\nEmpfehlung: Rotiere das Bild um {-result['median_angle']:.2f}° um es zu korrigieren")
        else:
            print(f"\nDas Dokument ist bereits gut ausgerichtet!")

        # JSON output für GitHub Actions
        print("\n::set-output name=rotation_result::" + json.dumps(result))
    else:
        print("Error: Could not detect rotation")
        sys.exit(1)
