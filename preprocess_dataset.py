import cv2
import os
import shutil
import numpy as np
from concurrent.futures import ThreadPoolExecutor

SOURCE_DIR = 'dataset'
TARGET_DIR = 'dataset_gray'

def process_image(file_info):
    src_path, dest_path = file_info
    
    try:
        # Leer imagen
        img = cv2.imread(src_path)
        if img is None:
            return

        # 1. Convertir a Escala de Grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Aplicar CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # Esto resalta las manchas (antracnosis) y mejora la textura local
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)

        # 3. Convertir de nuevo a BGR (3 canales) para que sea compatible con EfficientNet
        # Aunque sea gris, el modelo espera 3 canales de entrada.
        # Al replicar el canal, la imagen se ve gris pero tiene la forma (H, W, 3)
        final_img = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

        # Guardar
        cv2.imwrite(dest_path, final_img)
        
    except Exception as e:
        print(f"Error procesando {src_path}: {e}")

def main():
    if os.path.exists(TARGET_DIR):
        print(f"Eliminando directorio existente {TARGET_DIR}...")
        shutil.rmtree(TARGET_DIR)
    
    print(f"Copiando estructura de directorios de {SOURCE_DIR} a {TARGET_DIR}...")
    shutil.copytree(SOURCE_DIR, TARGET_DIR, ignore=shutil.ignore_patterns('*.*')) # Solo carpetas

    files_to_process = []

    # Recorrer directorios y preparar lista de archivos
    for root, dirs, files in os.walk(SOURCE_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                src_path = os.path.join(root, file)
                
                # Construir ruta de destino manteniendo estructura
                rel_path = os.path.relpath(root, SOURCE_DIR)
                dest_folder = os.path.join(TARGET_DIR, rel_path)
                
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                
                dest_path = os.path.join(dest_folder, file)
                files_to_process.append((src_path, dest_path))

    print(f"Procesando {len(files_to_process)} imágenes (Grayscale + CLAHE)...")
    
    # Procesamiento en paralelo para mayor velocidad
    with ThreadPoolExecutor() as executor:
        executor.map(process_image, files_to_process)

    print("¡Preprocesamiento completado!")

if __name__ == "__main__":
    main()
