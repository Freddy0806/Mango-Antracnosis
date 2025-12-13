import os
import sys
import subprocess
import zipfile
import glob

def install_local_pip():
    # Ensure we have a pip module available
    try:
        import pip
    except ImportError:
        print("Instalando pip localmente...")
        subprocess.check_call([sys.executable, "-m", "ensurepip"])

def download_and_extract(package_spec, platform_tag, python_version="3.11"):
    print(f"\n--- Procesando {package_spec} para {platform_tag} ---")
    
    # 1. Download with pip
    # Usa --no-deps para evitar descargar dependencias que ya tengamos o que se resuelvan mal
    cmd = [
        sys.executable, "-m", "pip", "download",
        package_spec,
        "--platform", platform_tag,
        "--python-version", python_version,
        "--only-binary=:all:",
        "--no-deps",
        "-d", "."
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Falló la descarga de {package_spec}. Detalles: {e}")
        sys.exit(1)

    # 2. Find downloaded wheel
    # Buscamos el whl más reciente en el directorio actual (que acabamos de bajar)
    # Suponemos que el nombre del paquete está al inicio del whl
    pkg_name = package_spec.split("==")[0]
    whl_files = glob.glob(f"*{pkg_name}*.whl")
    
    if not whl_files:
        print(f"ERROR: No se encontró el archivo .whl descargado para {pkg_name}")
        sys.exit(1)
        
    whl_file = whl_files[0]
    print(f"Archivo descargado: {whl_file} ({os.path.getsize(whl_file)} bytes)")

    # 3. Extract
    print(f"Descomprimiendo {whl_file}...")
    try:
        with zipfile.ZipFile(whl_file, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("Descompresión exitosa.")
    except Exception as e:
        print(f"ERROR descomprimiendo: {e}")
        sys.exit(1)

    # 4. Clean up
    os.remove(whl_file)
    print("Limpieza completada.")

def setup_deps():
    install_local_pip()
    
    # Lista de paquetes a "vendorizar" (incluir manualmente)
    # Estas versiones son conocidas por funcionar con Flet 0.24.1 + Python 3.11 en Android
    deps = [
        # TFLite Runtime oficial
        ("tflite-runtime==2.14.0", "manylinux_2_34_aarch64"),
        # Numpy 1.23.5 (Compatible con TFLite 2.14 y muy estable)
        ("numpy==1.23.5", "manylinux_2_17_aarch64")
    ]

    for pkg, tag in deps:
        download_and_extract(pkg, tag)

    print("\n¡Todas las dependencias manuales han sido inyectadas!")

if __name__ == "__main__":
    setup_deps()
