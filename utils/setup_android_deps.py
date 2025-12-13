import os
import sys
import zipfile
import urllib.request
import shutil

# URL exacta del wheel de tflite-runtime 2.14.0 para Python 3.11 (aarch64/Android)
WHEEL_URL = "https://files.pythonhosted.org/packages/f2/e9/5fc0435129c23c17551fcfadc82bd0d5482276213dfbc641f07b4420cb6d/tflite_runtime-2.14.0-cp311-cp311-manylinux_2_34_aarch64.whl"
WHEEL_FILE = "tflite_runtime.whl"

def setup_deps():
    print(f"Inicio de descarga de dependencias Android...")
    
    # 1. Descargar el wheel
    print(f"Descargando {WHEEL_URL}...")
    try:
        urllib.request.urlretrieve(WHEEL_URL, WHEEL_FILE)
        print("Descarga completada.")
    except Exception as e:
        print(f"ERROR FATAL descargando wheel: {e}")
        # Intento de fallback o fail
        sys.exit(1)

    # 2. Verificar descarga
    if not os.path.exists(WHEEL_FILE):
        print("ERROR: El archivo no se descargó.")
        sys.exit(1)
        
    print(f"Tamaño del archivo: {os.path.getsize(WHEEL_FILE)} bytes")

    # 3. Descomprimir
    print("Descomprimiendo wheel...")
    try:
        with zipfile.ZipFile(WHEEL_FILE, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("Descompresión exitosa.")
    except Exception as e:
        print(f"ERROR descomprimiendo: {e}")
        sys.exit(1)

    # 4. Verificar carpeta extraida
    if os.path.exists("tflite_runtime"):
        print("VERIFICADO: Carpeta 'tflite_runtime' existe. Inyección lista.")
    else:
        print("ERROR: No se encontró la carpeta 'tflite_runtime' tras descomprimir.")
        sys.exit(1)

    # 5. Limpieza
    os.remove(WHEEL_FILE)
    print("Limpieza completada.")

if __name__ == "__main__":
    setup_deps()
