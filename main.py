# ======================================================
# IATLAS — CEREBRO HISTÓRICO HÍBRIDO v4.1
# Estable para Render + Aprendizaje Persistente
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
# CONFIGURACIÓN
# ======================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MEMORIA_ARCHIVO = os.path.join(DATA_DIR, "memoria.json")
CONOCIMIENTO_ARCHIVO = os.path.join(DATA_DIR, "conocimiento_propio.json")

CONTEXTO = {"ultimo_tema": None}

# ======================================================
# MAPA SEMÁNTICO
# ======================================================

MAPA_HISTORICO = {
    "inca": "Imperio inca",
    "incas": "Imperio inca",
    "maya": "Civilización maya",
    "mayas": "Civilización maya",
    "romano": "Imperio romano",
    "roma": "Imperio romano",
    "egipto": "Antiguo Egipto",
    "grecia": "Antigua Grecia",
    "edad media": "Edad Media",
    "napoleon": "Napoleón Bonaparte",
}

# ======================================================
# JSON SEGURO PARA RENDER
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
        print(f"[JSON ERROR] {path}: {e}")
        return default


def guardar_json(path, data):
    try:
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp, path)
    except Exception as e:
        print(f"[JSON WRITE ERROR] {path}: {e}")

# ======================================================
# INTENCIÓN
# ======================================================

def detectar_intencion(texto: str):
    t = texto.lower()

    if any(p in t for p in ["hola", "buenas", "hey"]):
        return "saludo"

    if "me llamo" in t:
        return "nombre"

    if "me gusta" in t:
        return "gusto"

    if any(p in t for p in ["resolver", "calcular"]):
        return "matematicas"

    if any(p in t for p in [
        "inca", "maya", "romano", "egipto",
        "historia", "imperio", "edad"
    ]):
        return "historia"

    return "general"

# ======================================================
# SEMÁNTICA
# ======================================================

def extraer_tema(texto: str):
    t = texto.lower()

    if any(p in t for p in ["más", "continua", "sigue"]) and CONTEXTO["ultimo_tema"]:
        return CONTEXTO["ultimo_tema"]

    t = re.sub(r"[^\w\s]", "", t)

    stopwords = [
        "historia","de","los","las","el","la","sobre","acerca",
        "que","qué","por","favor","háblame","hablame",
        "quien","quién","fue","era","sabes","cuentame","dime"
    ]

    for w in stopwords:
        t = re.sub(rf"\b{w}\b", "", t)

    tema = " ".join(t.split())

    tema = MAPA_HISTORICO.get(tema, tema)

    if tema:
        CONTEXTO["ultimo_tema"] = tema

    return tema

# ======================================================
# WIKIPEDIA
# ======================================================

def buscar_wikipedia(tema):
    try:
        url = (
            "https://es.wikipedia.org/w/api.php"
            "?action=query&list=search&srsearch="
            + tema + "&format=json"
        )

        r = requests.get(url, timeout=8).json()
        resultados = r.get("query", {}).get("search", [])

        if not resultados:
            return None

        titulo = resultados[0]["title"]

        resumen = requests.get(
            "https://es.wikipedia.org/api/rest_v1/page/summary/"
            + titulo.replace(" ", "_"),
            timeout=8
        ).json()

        return resumen.get("extract")

    except:
        return None

# ======================================================
# RESUMEN
# ======================================================

def resumir(texto, max_len=500):
    texto = texto.replace("\n", " ")
    return texto[:max_len] + "..."

# ======================================================
# CEREBRO PRINCIPAL
# ======================================================

def conocimiento_historico(texto_usuario):

    conocimiento = cargar_json(CONOCIMIENTO_ARCHIVO, {})

    tema = extraer_tema(texto_usuario)

    # 🧠 ya aprendido
    if tema in conocimiento:
        return f"🧠 (memoria)\n\n{conocimiento[tema]}"

    info = buscar_wikipedia(tema)

    if info:
        resumen = resumir(info)
        conocimiento[tema] = resumen
        guardar_json(CONOCIMIENTO_ARCHIVO, conocimiento)
        return resumen

    return (
        f"No encontré información clara sobre «{tema}».\n"
        "¿Puedes darme un poco más de contexto?"
    )

# ======================================================
# FASTAPI
# ======================================================

app = FastAPI(title="IAtlas", version="4.1")

if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Mensaje(BaseModel):
    texto: str

@app.get("/chat")
def chat_ui():
    return FileResponse("static/chat.html")

@app.post("/chat")
def chat(m: Mensaje):

    texto = m.texto.strip()
    memoria = cargar_json(MEMORIA_ARCHIVO, {"nombre": None, "gustos": []})

    intencion = detectar_intencion(texto)

    if intencion == "saludo":
        return {"respuesta": "Hola 👋 Soy IAtlas."}

    if intencion == "nombre":
        nombre = texto.split()[-1].capitalize()
        memoria["nombre"] = nombre
        guardar_json(MEMORIA_ARCHIVO, memoria)
        return {"respuesta": f"Mucho gusto {nombre} 😊"}

    if intencion == "gusto":
        gusto = texto.split("me gusta")[-1].strip()
        memoria["gustos"].append(gusto)
        guardar_json(MEMORIA_ARCHIVO, memoria)
        return {"respuesta": f"Lo recordaré: te gusta {gusto}."}

    if intencion == "matematicas":
        try:
            expr = texto.replace("resolver", "").replace("calcular", "")
            return {"respuesta": str(sp.sympify(expr))}
        except:
            return {"respuesta": "No pude resolver eso."}

    if intencion == "historia":
        return {"respuesta": conocimiento_historico(texto)}

    return {"respuesta": "¿Qué te gustaría aprender hoy?"}
