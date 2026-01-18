# ======================================================
# CEREBRO.PY — NÚCLEO DE PENSAMIENTO DE IATLAS
# ======================================================

import requests
import json
import os
import re

# ------------------------------------------------------
# ARCHIVOS
# ------------------------------------------------------

MEMORIA_APRENDIZAJE = "conocimiento_propio.json"

# ------------------------------------------------------
# MAPA SEMÁNTICO
# ------------------------------------------------------

MAPA_ENTIDADES = {
    "inca": "Imperio inca",
    "incas": "Imperio inca",
    "maya": "Civilización maya",
    "mayas": "Civilización maya",
    "romano": "Imperio romano",
    "roma": "Imperio romano",
    "egipto": "Antiguo Egipto",
    "egipcios": "Antiguo Egipto",
    "grecia": "Antigua Grecia",
    "griegos": "Antigua Grecia",
    "edad media": "Edad Media",
    "napoleon": "Napoleón Bonaparte"
}

# ------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------

def cargar_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ------------------------------------------------------
# INTENCIÓN HUMANA
# ------------------------------------------------------

def detectar_intencion(texto):
    t = texto.lower()

    if any(p in t for p in ["cuando", "cuándo", "año", "fecha"]):
        return "fecha"

    if any(p in t for p in ["donde", "dónde", "ubicacion"]):
        return "lugar"

    if any(p in t for p in ["por que", "por qué", "causa"]):
        return "causa"

    if any(p in t for p in ["consecuencia", "resultado"]):
        return "consecuencia"

    if any(p in t for p in ["quien", "quién"]):
        return "persona"

    if any(p in t for p in ["como", "cómo"]):
        return "proceso"

    return "descripcion"


# ------------------------------------------------------
# EXTRACCIÓN DE ENTIDAD
# ------------------------------------------------------

def extraer_entidad(texto):
    t = texto.lower()

    for palabra, entidad in MAPA_ENTIDADES.items():
        if palabra in t:
            return entidad

    # limpieza general
    t = re.sub(r"[^\w\s]", "", t)

    basura = {
        "historia","de","los","las","el","la","sobre",
        "que","qué","cuando","cuándo","en","un","una"
    }

    palabras = [p for p in t.split() if p not in basura]

    return " ".join(palabras)


# ------------------------------------------------------
# WIKIPEDIA
# ------------------------------------------------------

def buscar_wikipedia(entidad):
    try:
        url = (
            "https://es.wikipedia.org/w/api.php"
            "?action=query"
            "&list=search"
            "&srsearch=" + entidad +
            "&format=json"
        )

        r = requests.get(url, timeout=6).json()
        resultados = r.get("query", {}).get("search", [])

        if not resultados:
            return None

        titulo = resultados[0]["title"]

        resumen = requests.get(
            "https://es.wikipedia.org/api/rest_v1/page/summary/"
            + titulo.replace(" ", "_"),
            timeout=6
        ).json()

        return resumen.get("extract")

    except:
        return None


# ------------------------------------------------------
# CONSTRUCTOR DE RESPUESTA
# ------------------------------------------------------

def construir_respuesta(intencion, entidad, informacion):

    if not informacion:
        return f"No encontré información confiable sobre {entidad}."

    if intencion == "fecha":
        return f"📅 Sobre las fechas de {entidad}:\n\n{informacion}"

    if intencion == "causa":
        return f"⚠️ Las causas relacionadas con {entidad} fueron:\n\n{informacion}"

    if intencion == "consecuencia":
        return f"📉 Las consecuencias históricas de {entidad}:\n\n{informacion}"

    if intencion == "persona":
        return f"👤 Información sobre {entidad}:\n\n{informacion}"

    if intencion == "proceso":
        return f"⚙️ Así se desarrolló {entidad}:\n\n{informacion}"

    return informacion


# ------------------------------------------------------
# FUNCIÓN PRINCIPAL (PENSAR)
# ------------------------------------------------------

def pensar(texto_usuario):

    memoria = cargar_json(MEMORIA_APRENDIZAJE, {})

    intencion = detectar_intencion(texto_usuario)
    entidad = extraer_entidad(texto_usuario)

    # ¿ya aprendido?
    if entidad in memoria:
        info = memoria[entidad]
    else:
        info = buscar_wikipedia(entidad)
        if info:
            memoria[entidad] = info
            guardar_json(MEMORIA_APRENDIZAJE, memoria)

    return construir_respuesta(intencion, entidad, info)
