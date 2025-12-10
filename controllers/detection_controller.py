import cv2
import numpy as np
import os
import sqlite3
import datetime

# Intentar importar TensorFlow completo o TFLite Runtime
try:
    import tensorflow as tf
    USE_TFLITE = False
    print("Usando TensorFlow Full (PC)")
except ImportError:
    try:
        import tflite_runtime.interpreter as tflite
        USE_TFLITE = True
        print("Usando TFLite Runtime (Móvil)")
    except ImportError:
        print("Error: No se encontró TensorFlow ni TFLite Runtime")
        USE_TFLITE = None

from controllers.auth_controller import auth_controller
from utils.email_service import email_service

class DetectionController:
    def __init__(self, db_path="users.db", model_path="mango_model_gray.h5"):
        self.db_path = db_path
        self.model_path = model_path
        self.model = None
        self.interpreter = None
        self._init_db()
        self.load_model()

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

    def load_model(self): # Renamed from _load_model
        # Lógica de búsqueda robusta para Android/PC
        search_paths = [
            "mango_model_gray.tflite",
            "assets/mango_model_gray.tflite",
            os.path.join(os.path.dirname(__file__), "..", "mango_model_gray.tflite"),
            os.path.join(os.path.dirname(__file__), "..", "assets", "mango_model_gray.tflite"),
            "/data/user/0/com.flet.mango_antracnosis/files/flet/app/assets/mango_model_gray.tflite" # Hardcoded common Android path
        ]
        
        found_path = None
        for path in search_paths:
            if os.path.exists(path):
                found_path = path
                break
            # Try absolute path resolution
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                found_path = abs_path
                break

        # Fallback a H5 si estamos en PC
        h5_path = "mango_model_gray.h5"
        if not found_path and os.path.exists(h5_path):
             found_path = h5_path

        self.last_search_debug = f"CWD: {os.getcwd()} | Searched: {search_paths} | Found: {found_path}"
        print(self.last_search_debug)

        try:
            if found_path:
                if found_path.endswith(".tflite"):
                     try:
                        if USE_TFLITE:
                            self.interpreter = tflite.Interpreter(model_path=found_path)
                            print(f"Modelo TFLite cargado (Runtime): {found_path}")
                        elif 'tf' in globals():
                            self.interpreter = tf.lite.Interpreter(model_path=found_path)
                            print(f"Modelo TFLite cargado (TF): {found_path}")
                        else:
                            raise ImportError("Ni tflite_runtime ni tensorflow disponibles.")
                        
                        self.interpreter.allocate_tensors()
                        self.input_details = self.interpreter.get_input_details()
                        self.output_details = self.interpreter.get_output_details()
                        self.use_interpreter_logic = True
                        
                     except Exception as e_tflite:
                         print(f"Error cargando TFLite en {found_path}: {e_tflite}")
                         self.model_load_error = str(e_tflite)

                elif found_path.endswith(".h5") and not USE_TFLITE:
                    if 'tf' in globals():
                        self.model = tf.keras.models.load_model(found_path)
                        self.use_interpreter_logic = False
                        print(f"Modelo H5 cargado: {found_path}")
                    else:
                        self.model_load_error = "Modelo es .h5 pero TensorFlow no está instalado (Móvil?)"
            else:
                # Debugging brutal: Listar archivos para ver qué pasa
                files_in_cwd = os.listdir('.')
                self.model_load_error = f"No se encontró el modelo. CWD: {os.getcwd()}. Files: {files_in_cwd}"
                print(self.model_load_error)

        except Exception as e:
            print(f"Error general cargando modelo: {e}")
            self.model_load_error = str(e)

    def detect_disease(self, image_path): # Renamed from predict_image
        if (self.model is None and self.interpreter is None):
            error_msg = getattr(self, 'model_load_error', 'Modelo no cargado (Razón desconocida)')
            debug_msg = getattr(self, 'last_search_debug', 'No debug info')
            return {"error": f"{error_msg}\nDEBUG: {debug_msg}"}

        try:
            # Preprocesamiento
            # 1. Cargar imagen en escala de grises
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            
            if img is None:
                return {"error": "No se pudo leer la imagen"}

            # CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            img = clahe.apply(img)
            
            # Resize
            img = cv2.resize(img, (224, 224))
            
            # Convertir a 3 canales (EfficientNet lo requiere)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            
            # Normalización (EfficientNet suele esperar 0-255, pero verificamos float)
            img_array = img.astype(np.float32)
            img_array = np.expand_dims(img_array, axis=0) # (1, 224, 224, 3)

            # Inferencia
            if self.interpreter or (hasattr(self, 'use_interpreter_logic') and self.use_interpreter_logic):
                # Usar Intérprete TFLite
                input_data = img_array
                self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
                self.interpreter.invoke()
                prediction = self.interpreter.get_tensor(self.output_details[0]['index'])
            else:
                # Usar Keras Model H5
                prediction = self.model.predict(img_array)

            predicted_class = np.argmax(prediction, axis=1)[0]
            confidence = np.max(prediction)
            
            # Mapeo de resultados
            # Asumimos que las clases se cargaron en orden alfanumérico: nivel_0, nivel_1, ...
            levels = {
                0: {"status": "Sano", "phase": "Nivel 0: Fruto sano", "treatment": "Ninguno. Monitoreo preventivo."},
                1: {"status": "Antracnosis", "phase": "Nivel 1: Infección leve", "treatment": "Aplicar fungicidas a base de cobre. Podar partes afectadas."},
                2: {"status": "Antracnosis", "phase": "Nivel 2: Infección moderada", "treatment": "Aplicar fungicidas sistémicos (ej. Azoxistrobina). Mejorar aireación."},
                3: {"status": "Antracnosis", "phase": "Nivel 3: Infección severa", "treatment": "Eliminar frutos infectados. Programa intensivo de fungicidas."},
                4: {"status": "Antracnosis", "phase": "Nivel 4: Infección muy severa", "treatment": "Destrucción total del fruto y cuarentena de la zona."}
            }

            result_info = levels.get(predicted_class, levels[0])
            
            # Guardar imagen procesada para visualización
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_filename = f"processed_{timestamp}.jpg"
            processed_path = os.path.join("assets", processed_filename)
            
            # Asegurar que existe directorio assets
            if not os.path.exists("assets"):
                os.makedirs("assets")
                
            cv2.imwrite(processed_path, img) # Save the preprocessed image (CLAHE, resized, 3-channel)

            result = {
                "status": result_info["status"],
                "phase": result_info["phase"],
                "confidence": float(confidence),
                "treatment": result_info["treatment"],
                "infection_ratio": float(confidence * 100), 
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

