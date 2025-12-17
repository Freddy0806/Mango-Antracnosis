import requests

# Base URLs for known Termux archives
ARCHIVES = [
    "https://archive.org/download/termux-repositories-legacy/", 
    "https://packages.termux.dev/apt/termux-main/pool/main/p/python-tflite-runtime/",
    "https://termux-pod.github.io/termux-package-archive/"
]

# Versions that likely corresponding to Python 3.11 (Late 2023 - Early 2024)
VERSIONS = [
    "2.16.1", 
    "2.15.0", 
    "2.14.0", 
    "2.13.0"
]

def probe_archive():
    print("Probing archives for older python-tflite-runtime...")
    
    # Structure often: python-tflite-runtime_VERSION_aarch64.deb
    for ver in VERSIONS:
        filename = f"python-tflite-runtime_{ver}_aarch64.deb"
        
        # Try direct Termux Main Pool (unlikely to have old, but check)
        url1 = f"https://packages.termux.dev/apt/termux-main/pool/main/p/python-tflite-runtime/{filename}"
        check_url(url1)
        
        # Try Wayback Machine / Archive.org guesses (Generic structure)
        # Often archived like: termux-main/pool/main/p/...
        
    print("Done probing.")

def check_url(url):
    try:
        r = requests.head(url, timeout=5)
        if r.status_code == 200:
            print(f"[FOUND] {url}")
            return True
        else:
            print(f"[404] {url}")
    except:
        pass
    return False

if __name__ == "__main__":
    probe_archive()
