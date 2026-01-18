# ======================================================
# CEREBRO.PY — NÚCLEO COGNITIVO DEFINITIVO
# ======================================================

import requests
import json
import os
import re
from urllib.parse import quote

MEMORIA_APRENDIZAJE = "data/conocimiento_propio.json"

# ======================================================
# UTILIDADES
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
# SEMÁNTICA
# ======================================================

def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r"[¿?¡!]", "", texto)

    basura = [
        "sabes", "sobre", "historia", "de", "los", "las",
        "el", "la", "que", "quien", "cuentame",
        "háblame", "hablame", "dime"
    ]

    for b in basura:
        texto = re.sub(rf"\b{b}\b", "", texto)

    return " ".join(texto.split())


# ======================================================
# BUSCADOR REAL DE WIKIPEDIA
# ======================================================

def buscar_wikipedia(entidad):
    try:
        # 🔎 Paso 1: preguntarle a Wikipedia el título correcto
        search_url = (
            "https://es.wikipedia.org/w/api.php"
            "?action=opensearch"
            f"&search={quote(entidad)}"
            "&limit=1&format=json"
        )

        resultado = requests.get(search_url, timeout=8).json()

        if not resultado[1]:
            return None

        titulo_real = resultado[1][0]

        # 📘 Paso 2: pedir resumen oficial
        summary_url = (
            "https://es.wikipedia.org/api/rest_v1/page/summary/"
            + quote(titulo_real)
        )

        r = requests.get(summary_url, timeout=8)

        if r.status_code != 200:
            return None

        return r.json().get("extract")

    except Exception as e:
        print("ERROR WIKI:", e)
        return None


# ======================================================
# RESPUESTA INTELIGENTE
# ======================================================

def pensar(texto_usuario):

    memoria = cargar_json(MEMORIA_APRENDIZAJE, {})

    entidad = limpiar_texto(texto_usuario)

    # 🧠 ya aprendido
    if entidad in memoria:
        return "🧠 (memoria)\n\n" + memoria[entidad]

    info = buscar_wikipedia(entidad)

    if info:
        memoria[entidad] = info
        guardar_json(MEMORIA_APRENDIZAJE, memoria)
        return info

    return (
        f"No pude encontrar información clara sobre «{entidad}».\n\n"
        "Puedes intentar por ejemplo:\n"
        "• imperio inca\n"
        "• civilización maya\n"
        "• imperio romano\n"
        "• antiguo egipto"
    )
