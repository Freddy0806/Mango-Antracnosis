import urllib.request
import zipfile
import os
import shutil

# URL OFICIAL que sabemos que funciona (TFLite 2.14.0 para Python 3.11 Aarch64)
URL = "https://files.pythonhosted.org/packages/f2/e9/5fc0435129c23c17551fcfadc82bd0d5482276213dfbc641f07b4420cb6d/tflite_runtime-2.14.0-cp311-cp311-manylinux_2_34_aarch64.whl"
FILENAME = "tflite_runtime.whl"

def vendorize():
    print(f"Descargando {URL}...")
    urllib.request.urlretrieve(URL, FILENAME)
    
    print("Descomprimiendo...")
    with zipfile.ZipFile(FILENAME, 'r') as zip_ref:
        zip_ref.extractall(".")
        
    print("Limpiando...")
    if os.path.exists(FILENAME):
        os.remove(FILENAME)
        
    # Limpiar carpetas de metadatos dist-info para no ensuciar tanto
    for item in os.listdir("."):
        if item.endswith(".dist-info") and "tflite_runtime" in item:
            shutil.rmtree(item)
            print(f"Borrado: {item}")

    print("¡Listo! Carpeta 'tflite_runtime' creada.")

if __name__ == "__main__":
    vendorize()
