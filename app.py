from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import os
import csv
import re
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
CSV_FILE = "pagos.csv"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_basic_fields(text):
    # Expresiones simples para empezar
    monto = None
    fecha = None
    nombre = None

    # monto: busca $ o cantidad con decimales o comas
    m = re.search(r"\$?\s*([0-9]{1,3}(?:[.,][0-9]{3})*(?:[.,][0-9]{2})?)", text)
    if m:
        monto = m.group(1)

    # fecha dd/mm/yyyy o dd-mm-yyyy o yyyy-mm-dd
    f = re.search(r"(\d{2}[\/\-]\d{2}[\/\-]\d{4})", text)
    if f:
        fecha = f.group(1)

    # nombre: busca rótulos comunes "Nombre" o "Cliente"
    n = re.search(r"(?:Nombre|Cliente)[:\s]*([A-Za-zÁÉÍÓÚáéíóúÑñ\s]{3,40})", text, re.IGNORECASE)
    if n:
        nombre = n.group(1).strip()

    return nombre or "No detectado", monto or "No detectado", fecha or "No detectado"

@app.route("/", methods=["GET"])
def index():
    return "API OCR activo"

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió archivo"}), 400

    f = request.files['file']
    if f.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400

    filename = secure_filename(f.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    f.save(filepath)

    # OCR
    try:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img, lang='spa+eng')  # spa si está disponible
    except Exception as e:
        return jsonify({"error": "Error procesando imagen", "detail": str(e)}), 500

    # Extraer campos básicos
    nombre, monto, fecha = extract_basic_fields(text)

    # Guardar en CSV
    header_needed = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, mode='a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if header_needed:
            writer.writerow(["nombre", "monto", "fecha", "texto_raw"])
        writer.writerow([nombre, monto, fecha, text.replace("\n", " ")])

    return jsonify({
        "nombre": nombre,
        "monto": monto,
        "fecha": fecha,
        "texto_raw": text
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
