import urllib.request
import zipfile
import os
import shutil

# ChaquoPython Numpy Wheel (Android aarch64 native, cp312)
WHEEL_URL = "https://chaquo.com/pypi-13.1/numpy/numpy-1.26.2-0-cp312-cp312-android_21_arm64_v8a.whl"
WHEEL_FILE = "numpy_chaquo_cp312.whl"

def vendorize_chaquo():
    print(f"Descargando {WHEEL_URL}...")
    try:
        req = urllib.request.Request(WHEEL_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(WHEEL_FILE, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Descarga OK.")
    except Exception as e:
        print(f"Error descargando: {e}")
        return

    print("Instalando Numpy desde Chaquo Wheel...")
    
    # We extract into ./numpy (root of app)
    # The wheel structure matches python conventions.
    TARGET_ROOT = "."
    
    try:
        with zipfile.ZipFile(WHEEL_FILE, 'r') as zf:
            for member in zf.namelist():
                # We only want the 'numpy' folder.
                # Wheel might contain numpy-1.26.2.dist-info etc.
                if member.startswith("numpy/"):
                    zip_info = zf.getinfo(member)
                    
                    # Target path
                    target_path = os.path.join(TARGET_ROOT, member)
                    
                    if member.endswith("/"):
                        os.makedirs(target_path, exist_ok=True)
                    else:
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        with zf.open(member) as source, open(target_path, "wb") as outfile:
                            shutil.copyfileobj(source, outfile)
                        
                        # Preserve executable bit for .so? Windows doesn't care much but good practice
                        # if running on linux. But we are on windows.
            
            print("Extracción completada.")

    except Exception as e:
        print(f"Error extrayendo: {e}")
        return

    if os.path.exists(WHEEL_FILE):
        os.remove(WHEEL_FILE)
    
    print("¡Numpy (Chaquo) instalado correctamente!")

if __name__ == "__main__":
    vendorize_chaquo()
