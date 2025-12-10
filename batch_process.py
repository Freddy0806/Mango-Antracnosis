import cv2
import numpy as np
import pandas as pd
import os
import argparse

def process_image(image_path):
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        img = cv2.resize(img, (500, 500))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Máscara Mango
        lower_mango = np.array([10, 40, 40])
        upper_mango = np.array([100, 255, 255])
        mask_mango = cv2.inRange(hsv, lower_mango, upper_mango)
        kernel = np.ones((5,5), np.uint8)
        mask_mango = cv2.morphologyEx(mask_mango, cv2.MORPH_CLOSE, kernel)
        mask_mango = cv2.morphologyEx(mask_mango, cv2.MORPH_OPEN, kernel)
        
        fruit_area = cv2.countNonZero(mask_mango)
        if fruit_area == 0:
            return 0.0

        # Máscara Manchas
        lower_brown = np.array([0, 0, 0])
        upper_brown = np.array([180, 255, 80])
        mask_spots = cv2.inRange(hsv, lower_brown, upper_brown)
        mask_disease = cv2.bitwise_and(mask_spots, mask_spots, mask=mask_mango)
        mask_disease = cv2.morphologyEx(mask_disease, cv2.MORPH_OPEN, kernel)
        
        disease_area = cv2.countNonZero(mask_disease)
        
        return (disease_area / fruit_area) * 100
    except Exception as e:
        print(f"Error procesando {image_path}: {e}")
        return None

def classify_severity(ratio):
    if ratio <= 1.0: return 0, "Sano"
    if ratio <= 5.0: return 1, "Leve"
    if ratio <= 9.0: return 2, "Moderada"
    if ratio <= 49.0: return 3, "Severa"
    return 4, "Muy Severa"

def main(dataset_path, output_csv):
    results = []
    print(f"Procesando imágenes en: {dataset_path}")
    
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                full_path = os.path.join(root, file)
                ratio = process_image(full_path)
                
                if ratio is not None:
                    level, label = classify_severity(ratio)
                    results.append({
                        "filename": file,
                        "path": full_path,
                        "infection_ratio": ratio,
                        "severity_level": level,
                        "label": label
                    })
                    print(f"Procesado: {file} -> Nivel {level} ({ratio:.2f}%)")
    
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Resultados guardados en {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procesar dataset de mangos")
    parser.add_argument("dataset_path", help="Ruta a la carpeta con imágenes")
    parser.add_argument("--output", default="resultados_mango.csv", help="Nombre del archivo CSV de salida")
    args = parser.parse_args()
    
    if os.path.exists(args.dataset_path):
        main(args.dataset_path, args.output)
    else:
        print("La ruta del dataset no existe.")
