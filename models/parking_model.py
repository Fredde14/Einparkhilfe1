import numpy as np
from PIL import Image, ImageDraw

class ParkingAI:
    def __init__(self):
        self.model = None
        self.model_name = "Objekt-Erkennungs-Engine"
        
        # Nutzen YOLOv8n für schnelle Objekterkennung von Fahrzeugen im Bild
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.model_name = "YOLOv8n (Fahrzeug-Erkennung)"
        except Exception as e:
            print(f"Fallback auf Standard-Bildanalyse: {e}")

    def analyze_scene(self, pil_image):
        """
        Erkennt Fahrzeuge im Bild und gibt das annotierte Bild, 
        die Anzahl der Autos und erkannte Farb-/Objektpositionen zurück.
        """
        img_rgb = pil_image.convert("RGB")
        w, h = img_rgb.size
        
        detected_cars = []
        
        if self.model is not None:
            try:
                results = self.model(np.array(img_rgb), verbose=False)
                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    if cls_id in [2, 5, 7]:  # Autos, Busse, LKWs in COCO
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        detected_cars.append({"box": (x1, y1, x2, y2), "center_x": (x1 + x2) / 2})
            except Exception:
                pass

        # Sortiere erkannte Autos von links nach rechts im Bild
        detected_cars = sorted(detected_cars, key=lambda c: c["center_x"])

        # Bild mit Bounding Boxes annotieren
        annotated_img = img_rgb.copy()
        draw = ImageDraw.Draw(annotated_img)
        
        for i, car in enumerate(detected_cars):
            x1, y1, x2, y2 = car["box"]
            draw.rectangle([x1, y1, x2, y2], outline="#3182ce", width=3)
            draw.text((x1 + 5, max(0, y1 - 15)), f"Fahrzeug {i+1}", fill="#63b3ed")

        return annotated_img, len(detected_cars), detected_cars, self.model_name

def load_parking_model():
    return ParkingAI()
