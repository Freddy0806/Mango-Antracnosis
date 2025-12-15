import urllib.request
import tarfile
import io
import os
import shutil
import lzma

# Termux libandroid-support
DEB_URL = "https://grimler.se/termux-packages-24/pool/main/liba/libandroid-support/libandroid-support_29-1_aarch64.deb"
DEB_FILE = "termux_android_support.deb"

def vendorize_support():
    print(f"Descargando {DEB_URL}...")
    try:
        req = urllib.request.Request(DEB_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(DEB_FILE, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Descarga OK.")
    except Exception as e:
        print(f"Error descargando: {e}")
        return

    print("Analizando archivo .deb (Robust Scan)...")
    data_tar_xz = None
    
    with open(DEB_FILE, "rb") as f:
        content = f.read()
        
        candidates = [b"data.tar.xz", b"data.tar.zst"]
        header_start = -1
        
        for cand in candidates:
            idx = content.find(cand)
            if idx != -1:
                # Header length is 60. Ends with `\x60\x0a`
                if content[idx+58:idx+60] == b"\x60\x0a":
                    print(f"Header encontrado en offset {idx}")
                    header_start = idx
                    break
        
        if header_start != -1:
            size_bytes = content[header_start+48 : header_start+58]
            try:
                size = int(size_bytes.strip())
                print(f"Tamaño de data: {size} bytes")
                data_start = header_start + 60
                data_tar_xz = content[data_start : data_start+size]
            except Exception as e:
                print(f"Error parseando tamaño: {e}")

    if not data_tar_xz:
        print("No se encontró data.tar.xz")
        return

    print("Extrayendo libandroid-support.so...")
    TARGET_DIR = "numpy/_core"
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    try:
        with io.BytesIO(data_tar_xz) as bio:
            with lzma.open(bio) as xz:
                with tarfile.open(fileobj=xz, mode="r|") as tar:
                    found = False
                    for member in tar:
                        if "libandroid-support.so" in member.name and member.isfile():
                            print(f"Encontrado: {member.name}")
                            source = tar.extractfile(member)
                            target_path = os.path.join(TARGET_DIR, "libandroid-support.so")
                            with open(target_path, "wb") as outfile:
                                outfile.write(source.read())
                            print(f"Guardado en {target_path}")
                            found = True
                    
                    if not found:
                        print("Advertencia: No se encontró libandroid-support.so")

    except Exception as e:
        print(f"Error extrayendo: {e}")
        return

    if os.path.exists(DEB_FILE):
        os.remove(DEB_FILE)
    
    print("¡Éxito! Support lib inyectado.")

if __name__ == "__main__":
    vendorize_support()
