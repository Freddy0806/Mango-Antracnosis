import urllib.request
import tarfile
import io
import os
import shutil
import lzma

# Termux libgfortran5 (Mirror)
DEB_URL = "https://grimler.se/termux-packages-24/pool/main/libg/libgfortran5/libgfortran5_14.2.0_aarch64.deb"
DEB_FILE = "termux_libgfortran.deb"

def vendorize_gfortran():
    print(f"Descargando {DEB_URL}...")
    try:
        req = urllib.request.Request(DEB_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(DEB_FILE, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Descarga OK.")
    except Exception as e:
        print(f"Error descargando: {e}")
        return

    print("Analizando archivo .deb...")
    data_tar_xz = None
    
    with open(DEB_FILE, "rb") as f:
        # Standard deb extraction
        while True:
            header = f.read(60)
            if not header or len(header) < 60:
                break
            
            name = header[:16].strip().decode()
            size = int(header[48:58].strip())
            content_pos = f.tell()
            
            if name.startswith("data.tar.xz") or name.startswith("data.tar.zst"):
                print(f"Encontrado {name} ({size} bytes)")
                f.seek(content_pos)
                data_tar_xz = f.read(size)
                break
            else:
                f.seek(content_pos + size + (size % 2)) 

    if not data_tar_xz:
        print("No se encontró data.tar.xz")
        return

    print("Extrayendo libgfortran.so.5 ...")
    TARGET_DIR = "numpy/_core"
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    try:
        with io.BytesIO(data_tar_xz) as bio:
            with lzma.open(bio) as xz:
                with tarfile.open(fileobj=xz, mode="r|") as tar:
                    found = False
                    for member in tar:
                        # usually lib/libgfortran.so.5.0.0
                        if "libgfortran.so.5" in member.name and member.isfile():
                            print(f"Encontrado: {member.name}")
                            source = tar.extractfile(member)
                            target_path = os.path.join(TARGET_DIR, "libgfortran.so.5")
                            with open(target_path, "wb") as outfile:
                                outfile.write(source.read())
                            print(f"Guardado en {target_path}")
                            found = True
                            
                            # Symlink for generic name if needed? 
                            # OpenBLAS probably needs libgfortran.so.5 specifically
                            
                    if not found:
                        print("Advertencia: No se encontró libgfortran.so.5")

    except Exception as e:
        print(f"Error extrayendo: {e}")
        return

    if os.path.exists(DEB_FILE):
        os.remove(DEB_FILE)
    
    print("¡Éxito! Libgfortran inyectado.")

if __name__ == "__main__":
    vendorize_gfortran()
