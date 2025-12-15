import urllib.request
import tarfile
import io
import os
import shutil
import lzma

# List of packages to vendorize for a COMPLETE functional Numpy on Android (Termux-based)
PACKAGES = [
    {
        "name": "python-numpy",
        "url": "https://grimler.se/termux-packages-24/pool/main/p/python-numpy/python-numpy_2.2.5-2_aarch64.deb",
        "extract_root": True, # Extract python files to ./numpy
        "so_target": None     # .so files inside are already in place relative to python files
    },
    {
        "name": "libopenblas",
        "url": "https://packages.termux.dev/apt/termux-main/pool/main/libo/libopenblas/libopenblas_0.3.30-2_aarch64.deb",
        "extract_root": False,
        "so_target": "numpy/_core" # Inject into core
    },
    {
        "name": "libc++_shared",
        "url": "https://grimler.se/termux-packages-24/pool/main/libc/libc++/libc++_29_aarch64.deb",
        "extract_root": False,
        "so_target": "numpy/_core"
    },
    {
        "name": "libandroid-support",
        "url": "https://grimler.se/termux-packages-24/pool/main/liba/libandroid-support/libandroid-support_29-1_aarch64.deb",
        "extract_root": False,
        "so_target": "numpy/_core"
    }
]

def download_deb(url, filename):
    print(f"Descargando {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Descarga OK.")
        return True
    except Exception as e:
        print(f"Error descargando {url}: {e}")
        return False

def extract_data_tar(deb_file):
    print(f"Analizando {deb_file}...")
    with open(deb_file, "rb") as f:
        content = f.read()
        
        candidates = [b"data.tar.xz", b"data.tar.zst"]
        header_start = -1
        
        for cand in candidates:
            idx = content.find(cand)
            if idx != -1:
                # Check for ar header magic \x60\x0a at offset 58
                if content[idx+58:idx+60] == b"\x60\x0a":
                    header_start = idx
                    break
        
        if header_start != -1:
            size_bytes = content[header_start+48 : header_start+58]
            try:
                size = int(size_bytes.strip())
                data_start = header_start + 60
                return content[data_start : data_start+size]
            except:
                pass
    return None

def vendorize_all():
    for pkg in PACKAGES:
        deb_name = f"temp_{pkg['name']}.deb"
        if not download_deb(pkg['url'], deb_name):
            continue
            
        data = extract_data_tar(deb_name)
        if not data:
            print(f"Error extrayendo data de {deb_name}")
            continue
            
        print(f"Instalando {pkg['name']}...")
        
        try:
            with io.BytesIO(data) as bio:
                with lzma.open(bio) as xz:
                    with tarfile.open(fileobj=xz, mode="r|") as tar:
                        for member in tar:
                            # Python Numpy Logic
                            if pkg["extract_root"]:
                                # Path: ./data/data/com.termux/files/usr/lib/python3.12/site-packages/numpy/...
                                if "site-packages/numpy/" in member.name:
                                    # Strip prefix to get relative path inside numpy/
                                    # e.g. "numpy/__init__.py"
                                    rel_path = member.name.split("site-packages/")[-1] 
                                    target_path = rel_path # This is "numpy/..."
                                    
                                    if member.isdir():
                                        os.makedirs(target_path, exist_ok=True)
                                    else:
                                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                                        with open(target_path, "wb") as outfile:
                                            outfile.write(tar.extractfile(member).read())
                                        #print(f"Extracted {target_path}")

                            # Shared Lib Logic
                            elif pkg["so_target"]:
                                if member.name.endswith(".so") and member.isfile():
                                    filename = os.path.basename(member.name)
                                    target_dir = pkg["so_target"]
                                    os.makedirs(target_dir, exist_ok=True)
                                    target_path = os.path.join(target_dir, filename)
                                    with open(target_path, "wb") as outfile:
                                        outfile.write(tar.extractfile(member).read())
                                    print(f"Inyectado {filename} en {target_path}")

        except Exception as e:
            print(f"Error procesando tar: {e}")
        
        if os.path.exists(deb_name):
            os.remove(deb_name)
            
    print("\n¡Vendorización Completa Finalizada!")

if __name__ == "__main__":
    vendorize_all()
