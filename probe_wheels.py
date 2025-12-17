import requests
import gzip
import io

# Termux Main Repo Packages Index
REPO_URL = "https://packages.termux.dev/apt/termux-main/dists/stable/main/binary-aarch64/Packages"
# Alternative mirror if needed
REPO_URL_2 = "https://grimler.se/termux-packages-24/dists/stable/main/binary-aarch64/Packages"

def find_package():
    url = REPO_URL
    print(f"Fetching {url}...")
    try:
        r = requests.get(url)
        if r.status_code == 404:
            print("404 on master repo, trying mirror...")
            url = REPO_URL_2
            r = requests.get(url)
    except:
        return

    content = r.text
    print(f"Index size: {len(content)} bytes")
    
    current_pkg = {}
    
    for line in content.splitlines():
        if line.strip() == "":
            # End of package block
            if current_pkg.get("Package") in ["libopenblas", "openblas", "blas-openblas"]:
                print("--- FOUND CANDIDATE ---")
                print(f"Package: {current_pkg.get('Package')}")
                print(f"Version: {current_pkg.get('Version')}")
                print(f"Filename: {current_pkg.get('Filename')}")
                print(f"Depends: {current_pkg.get('Depends')}")
                print("-----------------------")
            current_pkg = {}
            continue
            
        if ": " in line:
            key, val = line.split(": ", 1)
            current_pkg[key] = val

if __name__ == "__main__":
    find_package()
