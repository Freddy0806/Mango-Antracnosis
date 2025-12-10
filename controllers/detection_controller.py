import cv2
import numpy as np
import os
import sqlite3
import datetime
import tensorflow as tf
from controllers.auth_controller import auth_controller
from utils.email_service import email_service

class DetectionController:
    def __init__(self, db_path="users.db", model_path="mango_model_gray.h5"):
        self.db_path = db_path
        self.model_path = model_path
        self.model = None
        self._init_db()
        self._load_model()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                image_path TEXT,
                status TEXT,
                phase TEXT,
                confidence REAL,
                treatment TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def _load_model(self):
        if os.path.exists(self.model_path):
            try:
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"Modelo IA ({self.model_path}) cargado exitosamente.")
            except Exception as e:
                print(f"Error cargando modelo: {e}")
        else:
            print(f"Advertencia: No se encontró el modelo en {self.model_path}. La detección fallará hasta que se entrene el modelo.")

    def detect_disease(self, image_path):
        if not os.path.exists(image_path):
            return {"error": "Imagen no encontrada"}

        if self.model is None:
            return {"error": "Modelo IA no encontrado. Por favor entrena el modelo primero."}

        try:
            # 1. Leer imagen
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "No se pudo leer la imagen"}
            
            # 2. Preprocesamiento (Grayscale + CLAHE) - IGUAL QUE EN ENTRENAMIENTO
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            final_img = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR) # 3 canales para EfficientNet

            # 3. Resize y preparación
            img_resized = cv2.resize(final_img, (224, 224))
            img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
            img_array = np.expand_dims(img_array, axis=0) # Batch dimension
            # img_array = img_array / 255.0 # REMOVIDO: EfficientNet espera 0-255

            # 2. Predicción
            predictions = self.model.predict(img_array)
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])

            # 3. Mapeo de resultados
            # Asumimos que las clases se cargaron en orden alfanumérico: nivel_0, nivel_1, ...
            levels = {
                0: {"status": "Sano", "phase": "Nivel 0: Fruto sano", "treatment": "Ninguno. Monitoreo preventivo."},
                1: {"status": "Antracnosis", "phase": "Nivel 1: Infección leve", "treatment": "Aplicar fungicidas a base de cobre. Podar partes afectadas."},
                2: {"status": "Antracnosis", "phase": "Nivel 2: Infección moderada", "treatment": "Aplicar fungicidas sistémicos (ej. Azoxistrobina). Mejorar aireación."},
                3: {"status": "Antracnosis", "phase": "Nivel 3: Infección severa", "treatment": "Eliminar frutos infectados. Programa intensivo de fungicidas."},
                4: {"status": "Antracnosis", "phase": "Nivel 4: Infección muy severa", "treatment": "Destrucción total del fruto y cuarentena de la zona."}
            }

            result_info = levels.get(class_idx, levels[0])
            
            # Guardar imagen procesada para visualización
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_filename = f"processed_{timestamp}.jpg"
            processed_path = os.path.join("assets", processed_filename)
            
            # Asegurar que existe directorio assets
            if not os.path.exists("assets"):
                os.makedirs("assets")
                
            cv2.imwrite(processed_path, final_img)

            result = {
                "status": result_info["status"],
                "phase": result_info["phase"],
                "confidence": confidence,
                "treatment": result_info["treatment"],
                "infection_ratio": confidence * 100, 
                "processed_image": processed_path # Devolvemos la imagen procesada (Gris+CLAHE)
            }

            # Guardar en BD y enviar correo
            if auth_controller.current_user:
                self.save_detection(auth_controller.current_user["id"], image_path, result)
                
                subject = f"Nueva Detección IA: {result['status']} ({result['phase']})"
                body = f"Usuario: {auth_controller.current_user['username']}\nEstado: {result['status']}\nFase: {result['phase']}\nConfianza: {confidence:.2f}\nTratamiento: {result['treatment']}"
                email_service.send_email("admin@example.com", subject, body)

            return result

        except Exception as e:
            print(f"Error en detección IA: {e}")
            return {"error": str(e)}

    def save_detection(self, user_id, image_path, result):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO detections (user_id, image_path, status, phase, confidence, treatment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, image_path, result["status"], result["phase"], result["confidence"], result["treatment"]))
        conn.commit()
        conn.close()

    def get_user_detections(self, user_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM detections WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        detections = []
        for row in rows:
            detections.append({
                "id": row[0],
                "image_path": row[2],
                "status": row[3],
                "phase": row[4],
                "confidence": row[5],
                "treatment": row[6],
                "timestamp": row[7]
            })
        return detections

detection_controller = DetectionController()

