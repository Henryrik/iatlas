# ======================================================
# CEREBRO.PY — VERSIÓN DEFINITIVA ESTABLE
# ======================================================

import requests
import json
import os
import re
from urllib.parse import quote

MEMORIA_APRENDIZAJE = "data/conocimiento_propio.json"

# ======================================================
# MAPA REAL DE ENTIDADES WIKIPEDIA
# ======================================================

ENTIDADES = {
    "inca": "Imperio inca",
    "incas": "Imperio inca",
    "imperio inca": "Imperio inca",
    "incaico": "Imperio inca",

    "maya": "Civilización maya",
    "mayas": "Civilización maya",
    "cultura maya": "Civilización maya",

    "romano": "Imperio romano",
    "roma": "Imperio romano",

    "egipto": "Antiguo Egipto",
    "egipcio": "Antiguo Egipto",
    "egipto antiguo": "Antiguo Egipto",
}

# ======================================================
# JSON
# ======================================================

def cargar_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default


def guardar_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ======================================================
# EXTRACCIÓN REAL DE ENTIDAD
# ======================================================

def extraer_entidad(texto):
    t = texto.lower()

    # buscar coincidencias reales
    for clave in ENTIDADES:
        if clave in t:
            return ENTIDADES[clave]

    # respaldo
    palabras = re.findall(r"[a-záéíóúñ]+", t)
    return " ".join(palabras[-3:])

# ======================================================
# WIKIPEDIA REAL
# ======================================================

def buscar_wikipedia(titulo):
    try:
        url = (
            "https://es.wikipedia.org/api/rest_v1/page/summary/"
            + quote(titulo.replace(" ", "_"))
        )

        r = requests.get(url, timeout=8)

        if r.status_code != 200:
            return None

        return r.json().get("extract")

    except:
        return None

# ======================================================
# CEREBRO
# ======================================================

def pensar(texto_usuario):

    memoria = cargar_json(MEMORIA_APRENDIZAJE, {})

    entidad = extraer_entidad(texto_usuario)

    if entidad in memoria:
        return "🧠 (memoria)\n\n" + memoria[entidad]

    info = buscar_wikipedia(entidad)

    if info:
        memoria[entidad] = info
        guardar_json(MEMORIA_APRENDIZAJE, memoria)
        return info

    return f"No encontré información sobre «{entidad}»."
