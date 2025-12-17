import urllib.request
import tarfile
import io
import os
import shutil
import lzma

# URL for Termux package (Android aarch64 native)
# Using a reliable mirror
DEB_URL = "https://packages.termux.dev/apt/termux-main/pool/main/p/python-tflite-runtime/python-tflite-runtime_2.20.0_aarch64.deb"
DEB_FILE = "termux_tflite.deb"

def vendorize_termux():
    print(f"Descargando {DEB_URL}...")
    try:
        urllib.request.urlretrieve(DEB_URL, DEB_FILE)
        print("Descarga OK.")
    except Exception as e:
        print(f"Error descargando: {e}")
        return

    # Parse AR archive manually to find data.tar.xz
    # AR format: "!<arch>\n" then entries.
    # Entry: Name(16), Timestamp(12), Owner(6), Group(6), Mode(8), Size(10), End(2)
    
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
            
            # Content is here
            content_pos = f.tell()
            
            if name.startswith("data.tar.xz") or name.startswith("data.tar.zst"):
                print(f"Encontrado {name} ({size} bytes)")
                f.seek(content_pos)
                data_tar_xz = f.read(size)
                break
            else:
                f.seek(content_pos + size + (size % 2)) # Align to 2 bytes

    if not data_tar_xz:
        print("No se encontró data.tar.xz dentro del .deb")
        return

    print("Extrayendo contenido de data.tar.xz...")
    try:
        # Use lzma and tarfile
        with io.BytesIO(data_tar_xz) as bio:
            with lzma.open(bio) as xz:
                with tarfile.open(fileobj=xz, mode="r|") as tar:
                    # Filter and extract only tflite_runtime
                    extracted_count = 0
                    for member in tar:
                        if "tflite_runtime" in member.name and (member.isfile() or member.isdir()):
                            # Structure is usually ./data/data/com.termux/files/usr/lib/python3.11/site-packages/tflite_runtime/...
                            # We want to strip the prefix
                            original_name = member.name
                            if "site-packages/tflite_runtime/" in original_name:
                                relative_path = original_name.split("site-packages/tflite_runtime/", 1)[1]
                                if not relative_path: continue # Skip the folder itself if empty name
                                
                                dest_path = os.path.join("tflite_runtime", relative_path)
                                
                                if member.isdir():
                                    os.makedirs(dest_path, exist_ok=True)
                                else:
                                    # Ensure parent dir
                                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                    source = tar.extractfile(member)
                                    if source:
                                        with open(dest_path, "wb") as outfile:
                                            # Copy manually
                                            outfile.write(source.read())
                                        extracted_count += 1
                    
                    print(f"Extraídos {extracted_count} archivos.")

    except Exception as e:
        print(f"Error extrayendo tar.xz: {e}")
        return

    # Clean up
    if os.path.exists(DEB_FILE):
        os.remove(DEB_FILE)
    
    print("¡Éxito! Librería tflite_runtime nativa de Android (Termux) inyectada.")

if __name__ == "__main__":
    # Clean previous installation first
    if os.path.exists("tflite_runtime"):
        shutil.rmtree("tflite_runtime")
    vendorize_termux()
