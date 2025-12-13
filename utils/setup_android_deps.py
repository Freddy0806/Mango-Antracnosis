import os
import sys
import zipfile
import urllib.request
import shutil

# URL exacta del wheel de tflite-runtime 2.14.0 para Python 3.11 (aarch64/Android)
import json

# TFLite Runtime no está en PyPI JSON estándar bajo ese nombre a veces, o es confuso.
# Pero para Numpy sí funciona perfecto.
# Dejaremos TFLite hardcodeado (que sí funcionó) y Numpy dinámico.

TFLITE_URL = "https://files.pythonhosted.org/packages/f2/e9/5fc0435129c23c17551fcfadc82bd0d5482276213dfbc641f07b4420cb6d/tflite_runtime-2.14.0-cp311-cp311-manylinux_2_34_aarch64.whl"

def get_pypi_url(package_name, version, filename_filter):
    print(f"Buscando URL para {package_name} {version}...")
    api_url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read().decode())
            for release in data.get("urls", []):
                if filename_filter(release["filename"]):
                    return release["url"], release["filename"]
    except Exception as e:
        print(f"Error consultando PyPI: {e}")
    return None, None

def setup_deps():
    print(f"Inicio de inyección inteligente de dependencias...")
    
    # Lista de tareas: (URL Directa o None, Función de búsqueda o None, Carpeta Destino)
    tasks = [
        {
            "name": "tflite_runtime",
            "direct_url": TFLITE_URL,
            "filename": "tflite_runtime.whl",
            "target": "tflite_runtime"
        },
        {
            "name": "numpy",
            "pypi_query": {
                "package": "numpy",
                "version": "1.23.5",
                "filter": lambda f: "cp311-cp311-manylinux" in f and "aarch64" in f
            },
            "target": "numpy"
        }
    ]

    for task in tasks:
        url = task.get("direct_url")
        filename = task.get("filename", "temp.whl")
        
        # Resolver URL dinámicamente si es necesario
        if not url and "pypi_query" in task:
            q = task["pypi_query"]
            url, real_filename = get_pypi_url(q["package"], q["version"], q["filter"])
            if url:
                print(f"URL encontrada: {url}")
            else:
                print(f"ERROR: No se encontró URL para {task['name']}")
                sys.exit(1)

        print(f"Descargando {task['name']}...")
        try:
            urllib.request.urlretrieve(url, filename)
            print("Descarga OK.")
        except Exception as e:
            print(f"ERROR descargando {url}: {e}")
            sys.exit(1)

        print(f"Extrayendo {filename}...")
        try:
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(".")
            print("Extracción OK.")
        except Exception as e:
            print(f"ERROR extrayendo: {e}")
            sys.exit(1)
            
        if os.path.exists(filename):
            os.remove(filename)

    print("\n¡Dependencias inyectadas correctamente!")

if __name__ == "__main__":
    setup_deps()
