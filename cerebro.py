# ======================================================
# CEREBRO.PY — NÚCLEO DE PENSAMIENTO OPTIMIZADO v1.1
# Compatible con Render + Aprendizaje Persistente
# ======================================================

import requests
import json
import os
import re

# ======================================================
# RUTAS SEGURAS (Render-friendly)
# ======================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MEMORIA_APRENDIZAJE = os.path.join(DATA_DIR, "conocimiento_propio.json")

# ======================================================
# MAPA SEMÁNTICO DE ENTIDADES
# ======================================================

MAPA_ENTIDADES = {
    "inca": "Imperio incaico",
    "incas": "Imperio incaico",
    "incaico": "Imperio incaico",

    "maya": "Cultura maya",
    "mayas": "Cultura maya",

    "egipto": "Antiguo Egipto",
    "egipcio": "Antiguo Egipto",
    "egipcia": "Antiguo Egipto",

    "romano": "Imperio romano",
    "roma": "Imperio romano",
    "romanos": "Imperio romano",

    "grecia": "Antigua Grecia",
    "griego": "Antigua Grecia",

    "edad media": "Edad Media"
}

# ======================================================
# JSON SEGURO
# ======================================================

def cargar_json(path, default):
    try:
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(default, f, ensure_ascii=False, indent=2)
            return default

        with open(path, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            return json.loads(contenido) if contenido else default

    except Exception as e:
        print(f"[CEREBRO JSON ERROR] {e}")
        return default


def guardar_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        print(f"[CEREBRO WRITE ERROR] {e}")

# ======================================================
# INTENCIÓN SEMÁNTICA
# ======================================================

def detectar_intencion(texto):
    t = texto.lower()

    if any(p in t for p in ["cuando", "año", "fecha"]):
        return "fecha"

    if any(p in t for p in ["donde", "ubicacion", "lugar"]):
        return "lugar"

    if any(p in t for p in ["quien", "personaje", "emperador", "rey"]):
        return "persona"

    if any(p in t for p in ["causa", "porque", "razon"]):
        return "causa"

    if any(p in t for p in ["consecuencia", "resultado"]):
        return "consecuencia"

    return "descripcion"

# ======================================================
# EXTRACCIÓN DE ENTIDAD
# ======================================================

def extraer_entidad(texto):
    t = texto.lower()

    # 1️⃣ coincidencia directa
    for palabra, entidad in MAPA_ENTIDADES.items():
        if palabra in t:
            return entidad

    # 2️⃣ limpieza fuerte
    t = re.sub(r"[¿?¡!]", "", t)

    basura = {
        "sabes", "historia", "de", "los", "las", "el", "la",
        "sobre", "que", "en", "un", "una", "dime", "hablame",
        "háblame", "cuentame", "cuéntame", "aparecieron"
    }

    palabras = [p for p in t.split() if p not in basura]

    return " ".join(palabras).strip()

# ======================================================
# WIKIPEDIA — BÚSQUEDA INTELIGENTE
# ======================================================

from urllib.parse import quote
import requests

def buscar_wikipedia(entidad):
    if not entidad:
        return None

    try:
        entidad_url = quote(entidad.strip())

        # 1️⃣ intento directo
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{entidad_url}"
        r = requests.get(url, timeout=7)

        if r.status_code == 200:
            data = r.json()
            if data.get("extract"):
                return data["extract"]

        # 2️⃣ búsqueda alternativa
        search_api = (
            "https://es.wikipedia.org/w/api.php"
            "?action=query"
            "&list=search"
            f"&srsearch={entidad_url}"
            "&format=json"
        )

        rs = requests.get(search_api, timeout=7).json()
        resultados = rs.get("query", {}).get("search", [])

        if resultados:
            nuevo_titulo = quote(resultados[0]["title"])
            r2 = requests.get(
                f"https://es.wikipedia.org/api/rest_v1/page/summary/{nuevo_titulo}",
                timeout=7
            )

            if r2.status_code == 200:
                return r2.json().get("extract")

        return None

    except Exception as e:
        print("Wikipedia error:", e)
        return None

# ======================================================
# CONSTRUCCIÓN DE RESPUESTA
# ======================================================

def construir_respuesta(intencion, entidad, informacion):

    if not informacion:
        return (
            f"No encontré información clara sobre «{entidad}».\n\n"
            "Puedes intentar formularlo de otra forma 😊"
        )

    iconos = {
        "fecha": "📅",
        "lugar": "📍",
        "persona": "👤",
        "causa": "⚔️",
        "consecuencia": "📉",
        "descripcion": "📖"
    }

    icono = iconos.get(intencion, "📚")

    return f"{icono} **{entidad}**\n\n{informacion}"

# ======================================================
# FUNCIÓN PRINCIPAL (LA QUE IMPORTA MAIN.PY)
# ======================================================

def pensar(texto_usuario):

    memoria = cargar_json(MEMORIA_APRENDIZAJE, {})

    entidad = extraer_entidad(texto_usuario)
    intencion = detectar_intencion(texto_usuario)

    # 🧠 memoria local
    if entidad in memoria:
        informacion = memoria[entidad]
    else:
        informacion = buscar_wikipedia(entidad)
        if informacion:
            memoria[entidad] = informacion
            guardar_json(MEMORIA_APRENDIZAJE, memoria)

    return construir_respuesta(intencion, entidad, informacion)
