import os
import sys
import zipfile
import urllib.request
import shutil

# URL exacta del wheel de tflite-runtime 2.14.0 para Python 3.11 (aarch64/Android)
WHEELS = [
    {
        "url": "https://files.pythonhosted.org/packages/f2/e9/5fc0435129c23c17551fcfadc82bd0d5482276213dfbc641f07b4420cb6d/tflite_runtime-2.14.0-cp311-cp311-manylinux_2_34_aarch64.whl",
        "filename": "tflite_runtime.whl",
        "target_folder": "tflite_runtime"
    },
    {
        # Numpy 1.23.5 para Py3.11 Aarch64 (Compatibilidad probada)
        "url": "https://files.pythonhosted.org/packages/1a/2e/151484f495d03375d336fe05f42df5e0c511a5b81c4e7ab9e4fc7729177a/numpy-1.23.5-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl",
        "filename": "numpy.whl",
        "target_folder": "numpy"
    }
]

def setup_deps():
    print(f"Inicio de inyección manual de dependencias Android...")
    
    for lib in WHEELS:
        url = lib["url"]
        filename = lib["filename"]
        target = lib.get("target_folder")
        
        print(f"\nProcesando: {filename}")
        print(f"Descargando de {url}...")
        
        try:
            urllib.request.urlretrieve(url, filename)
            print("Descarga completada.")
        except Exception as e:
            print(f"ERROR FATAL descargando {filename}: {e}")
            sys.exit(1)

        if not os.path.exists(filename):
            print(f"ERROR: El archivo {filename} no se descargó.")
            sys.exit(1)
            
        print(f"Tamaño: {os.path.getsize(filename)} bytes")

        print("Descomprimiendo...")
        try:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(".")
            print("Descompresión exitosa.")
        except Exception as e:
            print(f"ERROR descomprimiendo {filename}: {e}")
            sys.exit(1)
            
        # Verificación opcional
        if target and os.path.exists(target):
            print(f"VERIFICADO: Carpeta '{target}' existe.")
        elif target:
             print(f"ADVERTENCIA: No se encontró la carpeta '{target}' esperada.")
        
        os.remove(filename)

    print("\n¡Limpieza completada! Dependencias inyectadas.")

if __name__ == "__main__":
    setup_deps()
