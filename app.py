from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os

app = FastAPI()

# Crear carpeta de uploads si no existe
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def main():
    return HTMLResponse("""
        <h2>Subir comprobante de pago</h2>
        <form action="/upload" enctype="multipart/form-data" method="post">
            <input name="file" type="file" />
            <button type="submit">Subir</button>
        </form>
    """)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return {"status": "ok", "file_saved": file_path}
