import urllib.request
import tarfile
import io
import os
import shutil
import lzma

# URL for Termux Numpy (Android aarch64 native)
# Updated to mirror found in search
DEB_URL = "https://packages.termux.org/apt/termux-main/pool/main/p/python-numpy/python-numpy_2.2.5-2_aarch64.deb"
DEB_FILE = "termux_numpy.deb"

def vendorize_numpy():
    print(f"Descargando {DEB_URL}...")
    try:
        # User-Agent header sometimes needed for some mirrors
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
        magic = f.read(8)
        if magic != b"!<arch>\n":
            print("No es un archivo AR válido.")
            return
            
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
        print("No se encontró data.tar.xz dentro del .deb")
        return

    print("Extrayendo contenido de data.tar.xz...")
    try:
        with io.BytesIO(data_tar_xz) as bio:
            with lzma.open(bio) as xz:
                with tarfile.open(fileobj=xz, mode="r|") as tar:
                    extracted_count = 0
                    for member in tar:
                        # Inspect members to find numpy folder
                        if "numpy" in member.name and (member.isfile() or member.isdir()):
                            # Typical path: ./data/data/com.termux/files/usr/lib/python3.12/site-packages/numpy/...
                            original_name = member.name
                            if "site-packages/numpy/" in original_name:
                                relative_path = original_name.split("site-packages/numpy/", 1)[1]
                                if not relative_path: continue 
                                
                                dest_path = os.path.join("numpy", relative_path)
                                
                                if member.isdir():
                                    os.makedirs(dest_path, exist_ok=True)
                                else:
                                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                    source = tar.extractfile(member)
                                    if source:
                                        with open(dest_path, "wb") as outfile:
                                            outfile.write(source.read())
                                        extracted_count += 1
                    
                    print(f"Extraídos {extracted_count} archivos de Numpy.")

    except Exception as e:
        print(f"Error extrayendo tar.xz: {e}")
        return

    if os.path.exists(DEB_FILE):
        os.remove(DEB_FILE)
    
    print("¡Éxito! Numpy nativo de Android (Termux) inyectado.")

if __name__ == "__main__":
    if os.path.exists("numpy"):
        shutil.rmtree("numpy")
    vendorize_numpy()
