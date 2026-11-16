import numpy as np
from PIL import Image, ImageDraw

class ParkingAI:
    def __init__(self):
        self.model = None
        self.model_name = "Geometrie- & Referenz-Engine"
        
        # 1. Versuch: RT-DETR (Vision Transformer Objekterkennung)
        try:
            from ultralytics import RTDETR
            self.model = RTDETR("rtdetr-l.pt")
            self.model_name = "RT-DETR (Transformer Vision)"
        except Exception:
            # 2. Versuch: YOLOv8s (Small - genauer als Nano)
            try:
                from ultralytics import YOLO
                self.model = YOLO("yolov8s.pt")
                self.model_name = "YOLOv8s Vision"
            except Exception as e:
                print(f"Fallback auf reine Python/PIL-Geometrie: {e}")

    def analyze_parking_space(self, pil_image, corner_points, ref_car_length=4.5):
        """
        Analysiert das Bild mit RT-DETR / Vision-Modell und berechnet über die
        angegebenen Eckpunkte + Referenzfahrzeug-Maße die reale Länge & Breite in Metern.
        
        corner_points: Dict mit 'x_start', 'x_end', 'y_top', 'y_bottom' (in % der Bildgröße)
        ref_car_length: Geschätzte Länge der parkenden Referenzautos im Bild (Standard 4.5m)
        """
        img_rgb = pil_image.convert("RGB")
        w, h = img_rgb.size
        
        detected_boxes = []
        cars_detected = 0

        # Objekterkennung ausführen (Klassen: 2=car, 5=bus, 7=truck)
        if self.model is not None:
            try:
                results = self.model(np.array(img_rgb), verbose=False)
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    if cls_id in [2, 5, 7]:
                        cars_detected += 1
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        detected_boxes.append((x1, y1, x2, y2, cls_id))
            except Exception:
                pass

        # --- ECKPUNKTE IN PIXEL UMRECHNEN ---
        px_x1 = w * (corner_points["x_start"] / 100.0)
        px_x2 = w * (corner_points["x_end"] / 100.0)
        px_y1 = h * (corner_points["y_top"] / 100.0)
        px_y2 = h * (corner_points["y_bottom"] / 100.0)

        gap_px_width = max(10.0, abs(px_x2 - px_x1))
        gap_px_height = max(10.0, abs(px_y2 - px_y1))

        # --- KALIBRIERUNG: PIXEL ZU METER ---
        # Wenn die KI Autos erkennt, nutzen wir deren durchschnittliche Pixelbreite als Maßstab!
        if detected_boxes:
            avg_car_px_w = np.mean([abs(b[2] - b[0]) for b in detected_boxes])
            meters_per_pixel = ref_car_length / max(avg_car_px_w, 30.0)
        else:
            # Fallback-Maßstab über Bildbreite (~12m Sichtfeld in typischer Straßenperspektive)
            meters_per_pixel = 12.0 / w

        # Perspektivische Korrektur (Tiefe im Bild streckt vertikale Pixel)
        estimated_length = round(gap_px_width * meters_per_pixel, 2)
        estimated_width = round((gap_px_height * meters_per_pixel) * 0.65, 2)

        # Plausibilitätsgrenzen für realistische Werte
        estimated_length = float(np.clip(estimated_length, 2.0, 9.5))
        estimated_width = float(np.clip(estimated_width, 1.5, 3.8))

        # --- VISUALISIERUNG DER ECKPUNKTE & KI-BOXEN ---
        annotated_img = self._draw_annotated_image(
            img_rgb.copy(),
            detected_boxes,
            (px_x1, px_y1, px_x2, px_y2),
            estimated_length,
            estimated_width
        )

        return estimated_length, estimated_width, annotated_img, cars_detected, self.model_name

    def _draw_annotated_image(self, img, detected_boxes, gap_rect, est_len, est_wid):
        draw = ImageDraw.Draw(img)
        
        # 1. Erkannte Referenzfahrzeuge (Blau)
        for (x1, y1, x2, y2, _) in detected_boxes:
            draw.rectangle([x1, y1, x2, y2], outline="#3182ce", width=3)
            draw.text((x1 + 5, max(0, y1 - 15)), "Referenz-KFZ", fill="#63b3ed")

        # 2. Markierte Parklücke über Eckpunkte (Grün/Cyan)
        gx1, gy1, gx2, gy2 = gap_rect
        draw.rectangle([gx1, gy1, gx2, gy2], outline="#00e676", width=4)

        # 4 Eckpunkte deutlich als Kreise hervorheben
        r = 7
        corners = [(gx1, gy1), (gx2, gy1), (gx1, gy2), (gx2, gy2)]
        for cx, cy in corners:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#ff9100", outline="#ffffff", width=2)

        # Maß-Label direkt an der Lücke
        draw.text((gx1 + 8, gy1 + 8), f"Luecke: {est_len:.1f}m x {est_wid:.1f}m", fill="#00e676")

        return img

def load_parking_model():
    return ParkingAI()
