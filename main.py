# ======================================================
# IATLAS — CEREBRO HISTÓRICO HÍBRIDO REAL
# ======================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import requests
import json
import os
import re
import sympy as sp

# ======================================================
# CONFIGURACIÓN GENERAL
# ======================================================

x = sp.symbols("x")
MEMORIA_ARCHIVO = "memoria.json"

PERSONALIDAD = {
    "nombre": "IAtlas",
    "descripcion": "IA histórica con razonamiento híbrido"
}

# ======================================================
# MAPA SEMÁNTICO (CEREBRO)
# ======================================================

MAPA_HISTORICO = {
    "inca": "Imperio inca",
    "incas": "Imperio inca",
    "imperio inca": "Imperio inca",

    "maya": "Civilización maya",
    "mayas": "Civilización maya",

    "romano": "Imperio romano",
    "roma": "Imperio romano",
    "imperio romano": "Imperio romano",

    "egipto": "Antiguo Egipto",
    "egipcio": "Antiguo Egipto",
    "egipcia": "Antiguo Egipto",

    "grecia": "Antigua Grecia",
    "griego": "Antigua Grecia",

    "edad media": "Edad Media",
    "medieval": "Edad Media",

    "napoleon": "Napoleón Bonaparte",
    "napoleón": "Napoleón Bonaparte"
}

# ======================================================
# HISTORIA LOCAL (MEMORIA BASE)
# ======================================================

HISTORIA_LOCAL = {
    "primera guerra mundial": (
        "La Primera Guerra Mundial ocurrió entre 1914 y 1918.\n\n"
        "Causas:\n"
        "- Nacionalismo\n- Imperialismo\n- Militarismo\n- Sistema de alianzas\n\n"
        "Consecuencias:\n"
        "- Más de 16 millones de muertos\n"
        "- Caída de imperios\n"
        "- Tratado de Versalles\n"
        "- Origen de la Segunda Guerra Mundial"
    )
}

# ======================================================
# MEMORIA PERSONAL
# ======================================================

def cargar_memoria():
    if not os.path.exists(MEMORIA_ARCHIVO):
        return {"nombre": None, "gustos": []}
    with open(MEMORIA_ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_memoria(memoria):
    with open(MEMORIA_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

# ======================================================
# INTENCIONES
# ======================================================

def detectar_intencion(texto: str):
    t = texto.lower()

    if any(p in t for p in ["hola", "hey", "buenas"]):
        return "saludo"

    if "me llamo" in t:
        return "nombre"

    if "me gusta" in t:
        return "gusto"

    if any(p in t for p in ["resolver", "calcular"]):
        return "matematicas"

    if any(p in t for p in [
        "inca", "maya", "romano", "egipto", "grecia",
        "imperio", "civilizacion", "historia"
    ]):
        return "historia"

    return "general"

# ======================================================
# EXTRACCIÓN HUMANA DE TEMA
# ======================================================

def extraer_tema(texto: str):
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)

    basura = {
        "historia","de","los","las","el","la",
        "sobre","acerca","puedes","explicame",
        "que","qué","en","un","una","por","favor",
        "sabes","hablame","háblame"
    }

    palabras = [p for p in texto.split() if p not in basura]
    tema = " ".join(palabras)

    return MAPA_HISTORICO.get(tema, tema)

# ======================================================
# WIKIPEDIA REAL (SEARCH + SUMMARY)
# ======================================================

def buscar_wikipedia(tema: str):

    try:
        search_url = (
            "https://es.wikipedia.org/w/api.php"
            "?action=query"
            "&list=search"
            "&srsearch=" + tema +
            "&format=json"
        )

        r = requests.get(search_url, timeout=8)
        data = r.json()

        resultados = data.get("query", {}).get("search", [])
        if not resultados:
            return None

        titulo = resultados[0]["title"]

        summary_url = (
            "https://es.wikipedia.org/api/rest_v1/page/summary/"
            + titulo.replace(" ", "_")
        )

        r2 = requests.get(summary_url, timeout=8)
        if r2.status_code != 200:
            return None

        return r2.json().get("extract")

    except:
        return None

# ======================================================
# CEREBRO HÍBRIDO FINAL
# ======================================================

def conocimiento_historico(texto: str):

    texto_l = texto.lower()

    # 1️⃣ memoria local
    for clave in HISTORIA_LOCAL:
        if clave in texto_l:
            return HISTORIA_LOCAL[clave]

    # 2️⃣ interpretar tema humano
    tema = extraer_tema(texto)

    # 3️⃣ buscar conocimiento externo
    info = buscar_wikipedia(tema)

    if info:
        return info

    # 4️⃣ razonamiento final
    return (
        f"No encontré información directa sobre «{tema}».\n\n"
        "Pero puedo ayudarte a analizar su contexto histórico, "
        "época, ubicación y relevancia si quieres."
    )

# ======================================================
# FASTAPI
# ======================================================

app = FastAPI(title="IAtlas", version="3.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensaje(BaseModel):
    texto: str

@app.get("/")
def inicio():
    return {"estado": "IAtlas con cerebro histórico activo"}

@app.get("/chat")
def chat_ui():
    return FileResponse("static/chat.html")

@app.post("/chat")
def chat(mensaje: Mensaje):

    texto = mensaje.texto.strip()
    memoria = cargar_memoria()
    intencion = detectar_intencion(texto)

    if intencion == "saludo":
        return {"respuesta": "Hola 👋 Soy IAtlas 😊"}

    if intencion == "nombre":
        nombre = texto.split("me llamo")[-1].strip().capitalize()
        memoria["nombre"] = nombre
        guardar_memoria(memoria)
        return {"respuesta": f"Encantado {nombre} 😊"}

    if intencion == "gusto":
        gusto = texto.split("me gusta")[-1].strip()
        memoria["gustos"].append(gusto)
        guardar_memoria(memoria)
        return {"respuesta": f"Perfecto 😊 recordaré que te gusta {gusto}"}

    if intencion == "matematicas":
        try:
            expr = texto.replace("resolver", "").replace("calcular", "")
            return {"respuesta": str(sp.sympify(expr))}
        except:
            return {"respuesta": "No pude resolverlo 😕"}

    if intencion == "historia":
        return {"respuesta": conocimiento_historico(texto)}

    return {"respuesta": "¿Sobre qué tema te gustaría aprender?"}
