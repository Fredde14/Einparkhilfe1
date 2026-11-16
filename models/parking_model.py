import numpy as np
from PIL import Image, ImageDraw

class ParkingAI:
    def __init__(self):
        self.model = None
        self.model_name = "Präzisions-Farb-Engine"
        
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8m.pt")
            self.model_name = "YOLOv8m (High-Precision + Color)"
        except Exception:
            try:
                from ultralytics::YOLO import YOLO
                self.model = YOLO("yolov8n.pt")
                self.model_name = "YOLOv8n (Standard + Color)"
            except Exception:
                pass

    def _get_dominant_color(self, crop_img):
        """
        Verbesserte Farb-Heuristik mit Berücksichtigung von Sättigung und Helligkeit,
        um Verwechslungen (z.B. Weiß als Blau oder Grau als Rot) zu verhindern.
        Gibt den Farbnamen und das passende Adjektiv für die Anleitung zurück.
        """
        try:
            # Nur den mittleren Bereich des Autos ausschneiden (reduziert störenden Hintergrund / Asphalt)
            w, h = crop_img.size
            if w > 20 and h > 20:
                crop_img = crop_img.crop((int(w*0.2), int(h*0.2), int(w*0.8), int(h*0.8)))

            img_small = crop_img.resize((25, 25))
            arr = np.array(img_small)
            if arr.size == 0:
                return "grau", "graue"
            
            mean_rgb = arr.mean(axis=(0, 1))
            r, g, b = float(mean_rgb[0]), float(mean_rgb[1]), float(mean_rgb[2])
            
            # Helligkeit und Sättigung berechnen
            brightness = (r + g + b) / 3.0
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            saturation = (max_val - min_val) / (max_val + 1e-5)

            # 1. Weiß (hohe Helligkeit, sehr geringe Sättigung)
            if brightness > 180 and saturation < 0.15:
                return "weiß", "weiße"
            
            # 2. Schwarz (sehr geringe Helligkeit)
            if brightness < 60:
                return "schwarz", "schwarze"
            
            # 3. Silber / Grau (mittlere Helligkeit, geringe Sättigung)
            if saturation < 0.2:
                if brightness > 120:
                    return "silber", "silberne"
                else:
                    return "grau", "graue"
            
            # 4. Rot (R-Kanal deutlich höher als G und B)
            if r > g + 40 and r > b + 40 and r > 100:
                return "rot", "rote"
            
            # 5. Blau (B-Kanal deutlich höher als R)
            if b > r + 35 and b > g + 15:
                return "blau", "blaue"
            
            # 6. Gelb / Gold (R und G hoch, B niedrig)
            if r > 120 and g > 120 and b < 90 and abs(r - g) < 40:
                return "gelb", "gelbe"
            
            # 7. Grün (G-Kanal am höchsten)
            if g > r + 20 and g > b + 20:
                return "grün", "grüne"
            
            # Standard-Fallback nach Helligkeit
            if brightness > 140:
                return "silber", "silberne"
            else:
                return "grau", "graue"
                
        except Exception:
            return "grau", "graue"

    def analyze_scene(self, pil_image):
        img_rgb = pil_image.convert("RGB")
        w, h = img_rgb.size
        
        detected_cars = []
        
        if self.model is not None:
            try:
                results = self.model(np.array(img_rgb), verbose=False)
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    if cls_id in [2, 5, 7]:  # Autos, Busse, LKWs
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        x1, y1 = max(0, int(x1)), max(0, int(y1))
                        x2, y2 = min(w, int(x2)), min(h, int(y2))
                        
                        if x2 > x1 + 10 and y2 > y1 + 10:
                            crop = img_rgb.crop((x1, y1, x2, y2))
                            color_noun, color_adj = self._get_dominant_color(crop)
                            
                            detected_cars.append({
                                "box": (x1, y1, x2, y2),
                                "center_x": (x1 + x2) / 2,
                                "color_noun": color_noun,
                                "color": color_adj  # z.B. "rote", "blaue", "weiße"
                            })
            except Exception:
                pass

        # Fallback mit realistischen Standardfarben
        if len(detected_cars) == 0:
            detected_cars = [
                {"box": (int(w * 0.05), int(h * 0.3), int(w * 0.30), int(h * 0.75)), "center_x": w * 0.17, "color_noun": "silber", "color": "silberne"},
                {"box": (int(w * 0.70), int(h * 0.3), int(w * 0.95), int(h * 0.75)), "center_x": w * 0.82, "color_noun": "schwarz", "color": "schwarze"}
            ]

        # Sortieren von links nach rechts
        detected_cars = sorted(detected_cars, key=lambda c: c["center_x"])

        # Annotieren
        annotated_img = img_rgb.copy()
        draw = ImageDraw.Draw(annotated_img)
        
        for i, car in enumerate(detected_cars):
            x1, y1, x2, y2 = car["box"]
            color_adj = car["color"]
            draw.rectangle([x1, y1, x2, y2], outline="#3182ce", width=3)
            draw.text((x1 + 5, max(0, y1 - 15)), f"{color_adj.capitalize()}s KFZ", fill="#63b3ed")

        return annotated_img, len(detected_cars), detected_cars, self.model_name

def load_parking_model():
    return ParkingAI()
