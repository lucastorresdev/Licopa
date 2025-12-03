from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, HTMLResponse
import shutil
import os
from typing import List, Optional

from ocr import leer_texto, extraer_campos  # importamos helper de ocr

app = FastAPI()

# Crear carpeta de uploads si no existe
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def main():
    return HTMLResponse("""
        <h2>Subir comprobantes de pago (varios)</h2>
        <form action="/upload" enctype="multipart/form-data" method="post">
            <label>Seleccionar archivos (puede elegir varios):</label><br/>
            <input name="files" type="file" multiple/><br/><br/>

            <label>Mes al que pertenece el comprobante:</label><br/>
            <select name="mes">
                <option value="2025-01">Enero 2025</option>
                <option value="2025-02">Febrero 2025</option>
                <option value="2025-03">Marzo 2025</option>
                <option value="2025-04">Abril 2025</option>
                <option value="2025-05">Mayo 2025</option>
                <option value="2025-06">Junio 2025</option>
                <option value="2025-07">Julio 2025</option>
                <option value="2025-08">Agosto 2025</option>
                <option value="2025-09">Septiembre 2025</option>
                <option value="2025-10">Octubre 2025</option>
                <option value="2025-11">Noviembre 2025</option>
                <option value="2025-12">Diciembre 2025</option>
            </select><br/><br/>

            <label>Campos a extraer (marcar los que quieras enviar al Google Sheet):</label><br/>
            <input type="checkbox" name="campos" value="fecha" checked> Fecha<br/>
            <input type="checkbox" name="campos" value="nombre" checked> Nombre<br/>
            <input type="checkbox" name="campos" value="cuit"> CUIT<br/>
            <input type="checkbox" name="campos" value="monto" checked> Monto<br/><br/>

            <button type="submit">Subir y procesar</button>
        </form>
    """)

@app.post("/upload")
async def upload(
    files: List[UploadFile] = File(...),
    mes: str = Form(...),
    campos: Optional[List[str]] = Form(None)
):
    """
    Recibe varios archivos, guarda cada uno, aplica OCR y devuelve los campos seleccionados
    `campos` vendrá como lista de strings (ej: ["fecha","monto"])
    """
    respuesta = []
    campos = campos or []

    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Aplicar OCR -> devuelve lista de líneas (o texto plano)
        texto_list = leer_texto(file_path)
        # Convertir lista a texto continuo para búsquedas
        texto_plano = "\n".join(texto_list) if isinstance(texto_list, list) else str(texto_list)

        # Extraer sólo los campos solicitados
        datos_extraidos = extraer_campos(texto_plano, campos)

        respuesta.append({
            "filename": file.filename,
            "mes": mes,
            "campos_solicitados": campos,
            "datos_extraidos": datos_extraidos,
            "texto_detectado_preview": texto_list[:10]  # las primeras líneas como preview
        })

    return JSONResponse(respuesta)
