# ocr.py
from paddleocr import PaddleOCR
import re

# Inicializamos PaddleOCR (solo español)
ocr = PaddleOCR(use_angle_cls=True, lang='spanish')

def leer_texto(ruta_imagen):
    """
    Devuelve lista de líneas de texto detectado.
    """
    resultado = ocr.ocr(ruta_imagen, cls=True)
    lines = []

    for block in resultado:
        for line in block:
            txt = line[1][0].strip()
            if txt:
                lines.append(txt)

    return lines


# --- Regex existentes ---
RE_DATE = re.compile(r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})")
RE_CUIT = re.compile(r"(\d{2}\-?\d{8}\-?\d|\d{11})")
RE_AMOUNT = re.compile(r"(?:(?:\$|ARS)?\s?)(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)")


def guess_name(lines):
    texto_str = "\n".join(lines) if isinstance(lines, list) else str(lines)
    for ln in texto_str.splitlines():
        if len(ln.strip()) > 3 and not re.search(r"\d", ln):
            low = ln.lower()
            if any(skip in low for skip in ["total", "pago", "importe", "cuenta", "cuit", "fecha"]):
                continue
            return ln.strip()
    return None


def extraer_campos(texto, campos_a_buscar):
    resultado = {}
    texto_str = texto if isinstance(texto, str) else "\n".join(texto)

    if "fecha" in campos_a_buscar:
        m = RE_DATE.search(texto_str)
        resultado["fecha"] = m.group(1) if m else None

    if "cuit" in campos_a_buscar:
        m = RE_CUIT.search(texto_str)
        if m:
            c = m.group(1)
            nums = re.sub(r"\D", "", c)
            if len(nums) == 11:
                c = f"{nums[:2]}-{nums[2:10]}-{nums[10]}"
            resultado["cuit"] = c
        else:
            resultado["cuit"] = None

    if "monto" in campos_a_buscar:
        matches = RE_AMOUNT.findall(texto_str)
        if matches:
            raw = matches[-1]
            normalized = raw.replace(".", "").replace(",", ".") \
                if raw.count(",") == 1 and raw.count(".") <= 1 else raw.replace(",", "")
            resultado["monto"] = normalized
        else:
            resultado["monto"] = None

    if "nombre" in campos_a_buscar:
        nombre = guess_name(texto_str)
        resultado["nombre"] = nombre

    return resultado
