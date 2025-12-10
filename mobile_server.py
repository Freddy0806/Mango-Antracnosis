from fastapi import FastAPI, UploadFile, File
import uvicorn
import flet.fastapi as flet_fastapi
from main import main
import os
import socket
import shutil

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# 1. Definir App FastAPI manualmente
app = FastAPI()

# Configurar CORS (Importante para acceso móvil/red)
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],      # Permitir todos los métodos (POST, PUT, OPTIONS, etc.)
    allow_headers=["*"],      # Permitir todas las cabeceras
)

# Asegurar directorios
cwd = os.getcwd()
assets_abs = os.path.join(cwd, "assets")
uploads_abs = os.path.join(cwd, "uploads")
for folder in [assets_abs, uploads_abs]:
    if not os.path.exists(folder):
        os.makedirs(folder)

from fastapi import FastAPI, UploadFile, File, Request

# ... (imports)

# 2. Endpoint de subida personalizado
# Soportamos POST y PUT por si acaso Flet cambia el método
@app.post("/api/upload")
@app.put("/api/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    print(f"DEBUG: Receiving upload request: {request.method} {request.url}")
    print(f"DEBUG: Headers: {request.headers}")
    try:
        file_path = os.path.join(uploads_abs, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"DEBUG: File saved to {file_path}")
        return {"filename": file.filename, "path": file_path}
    except Exception as e:
        print(f"DEBUG: Upload error: {str(e)}")
        return {"error": str(e)}

# 3. Montar Flet App en la raiz
# Nota: No pasamos upload_dir aquí porque manejaremos la subida nosotros
app.mount("/", flet_fastapi.app(main, assets_dir=assets_abs))

if __name__ == "__main__":
    local_ip = get_local_ip()
    print(f"\n========================================================")
    print(f"  SERVIDOR CUSTOM (FastAPI + Manual Upload)")
    print(f"  Accede a: http://{local_ip}:8000")
    print(f"========================================================\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
