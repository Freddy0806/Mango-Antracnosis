import tensorflow as tf

# Cargar el modelo existente
model_path = "mango_model_gray.h5"
print(f"Cargando modelo desde {model_path}...")
model = tf.keras.models.load_model(model_path)

# Convertir a TFLite
print("Convirtiendo a TensorFlow Lite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Optimizaciones (opcional, ayuda a reducir tamaño)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

tflite_model = converter.convert()

# Guardar
tflite_path = "mango_model_gray.tflite"
with open(tflite_path, "wb") as f:
    f.write(tflite_model)

print(f"Modelo convertido y guardado en {tflite_path}")
print("Listo para despliegue móvil.")
