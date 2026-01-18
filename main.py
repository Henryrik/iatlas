# =========================
# IMPORTS
# =========================

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import requests
import re
import json
import os
import sympy as sp

# =========================
# CONFIGURACIÓN GENERAL
# =========================

x = sp.symbols("x")
MEMORIA_ARCHIVO = "memoria.json"

PERSONALIDAD = {
    "nombre": "IAtlas",
    "tono": "amigable",
    "descripcion": (
        "Soy IAtlas, una IA personal. "
        "Hablo de forma clara, tranquila y cercana. "
        "Me gusta ayudar paso a paso."
    )
}

# =========================
# CONOCIMIENTO LOCAL
# =========================

HISTORIA = {
    "primera guerra mundial": {
        "fecha": "1914–1918",
        "bandos": {
            "aliados": ["Francia", "Reino Unido", "Rusia", "Estados Unidos", "Italia"],
            "potencias centrales": ["Alemania", "Imperio Austrohúngaro", "Imperio Otomano", "Bulgaria"]
        },
        "causas": [
            "Nacionalismo",
            "Imperialismo",
            "Militarismo",
            "Sistema de alianzas",
            "Asesinato del archiduque Francisco Fernando"
        ],
        "consecuencias": [
            "Más de 16 millones de muertos",
            "Caída de imperios europeos",
            "Tratado de Versalles",
            "Camino hacia la Segunda Guerra Mundial"
        ]
    }
}

# =========================
# MAPA SEMÁNTICO HISTÓRICO
# =========================

MAPA_HISTORICO = {
    "inca": "Imperio inca",
    "incas": "Imperio inca",
    "maya": "Civilización maya",
    "mayas": "Civilización maya",
    "romano": "Imperio romano",
    "roma": "Imperio romano",
    "egipto": "Antiguo Egipto",
    "egipcio": "Antiguo Egipto",
    "egipcia": "Antiguo Egipto",
    "grecia": "Antigua Grecia",
    "griego": "Antigua Grecia",
    "edad media": "Edad Media",
    "medieval": "Edad Media",
    "napoleon": "Napoleón Bonaparte",
    "napoleón": "Napoleón Bonaparte",
}

# =========================
# MEMORIA
# =========================

def cargar_memoria():
    if not os.path.exists(MEMORIA_ARCHIVO):
        return {"nombre": None, "gustos": [], "notas": []}
    with open(MEMORIA_ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_memoria(memoria):
    with open(MEMORIA_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

# =========================
# DETECTOR DE INTENCIÓN
# =========================

def detectar_intencion(texto: str):
    texto = texto.lower()

    if any(p in texto for p in ["hola", "buenas", "hey"]):
        return "saludo"
    if "me llamo" in texto:
        return "nombre"
    if "me gusta" in texto:
        return "gusto"
    if any(p in texto for p in ["resolver", "calcular"]):
        return "matematicas"
    if any(p in texto for p in ["historia", "imperio", "civilizacion", "inca", "maya", "romano", "egipto"]):
        return "historia"

    return "general"

# =========================
# RAZONAMIENTO NIVEL 3
# =========================

def razonar_pregunta(texto: str):
    if "por qué" in texto:
        return "Analicemos el contexto, las causas y las consecuencias."
    if "cómo" in texto:
        return "Te explico el proceso paso a paso."
    return "Podemos profundizar más si quieres."

# =========================
# EXTRACCIÓN DE TEMA
# =========================

def extraer_tema(texto: str):
    texto = texto.lower()
    basura = [
        "sabes","historia","de","los","las","el","la",
        "sobre","acerca","puedes","explicarme",
        "que","qué","en","un","una","por","favor"
    ]
    texto = re.sub(r"[^\w\s]", "", texto)
    palabras = [p for p in texto.split() if p not in basura]
    return " ".join(palabras)

# =========================
# WIKIPEDIA
# =========================

def buscar_wikipedia(tema: str):
    if not tema:
        return None

    if tema in MAPA_HISTORICO:
        tema = MAPA_HISTORICO[tema]

    url = "https://es.wikipedia.org/api/rest_v1/page/summary/" + tema.replace(" ", "_")

    try:
        r = requests.get(url, timeout=6)
        if r.status_code != 200:
            return None
        return r.json().get("extract")
    except:
        return None

# =========================
# SISTEMA HÍBRIDO FINAL
# =========================

def obtener_conocimiento_historico(texto: str):

    # primero local
    local = HISTORIA.get(texto.lower())
    if local:
        return local

    tema = extraer_tema(texto)
    info = buscar_wikipedia(tema)

    if info:
        return info

    return "No encontré información directa, pero puedo ayudarte a analizar el contexto histórico."

# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="IAtlas",
    description="IA híbrida histórica",
    version="1.2"
)

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
    return {"estado": "IAtlas híbrido operativo"}

# =========================
# CHAT
# =========================

@app.get("/chat")
def chat_ui():
    return FileResponse("static/chat.html")

@app.post("/chat")
def conversar(mensaje: Mensaje):

    texto = mensaje.texto.strip()
    memoria = cargar_memoria()
    intencion = detectar_intencion(texto)

    if intencion == "saludo":
        return {"respuesta": f"Hola 👋 Soy {PERSONALIDAD['nombre']} 😊"}

    if intencion == "nombre":
        nombre = texto.split("me llamo")[-1].strip().capitalize()
        memoria["nombre"] = nombre
        guardar_memoria(memoria)
        return {"respuesta": f"Encantado {nombre} 😊"}

    if intencion == "gusto":
        gusto = texto.split("me gusta")[-1].strip()
        memoria["gustos"].append(gusto)
        guardar_memoria(memoria)
        return {"respuesta": f"Perfecto 😊 recordaré que te gusta {gusto}."}

    if intencion == "matematicas":
        try:
            expr = texto.replace("resolver", "").replace("calcular", "")
            return {"respuesta": str(sp.sympify(expr))}
        except:
            return {"respuesta": "No pude resolverlo 😕"}

    if intencion == "historia":
        return {"respuesta": obtener_conocimiento_historico(texto)}

    return {"respuesta": razonar_pregunta(texto)}
