# ======================================================
# IATLAS — MAIN SERVER (CUERPO)
# El cerebro vive en cerebro.py
# ======================================================

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from cerebro import pensar

import json
import os
import sympy as sp

# ======================================================
# CONFIGURACIÓN
# ======================================================

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MEMORIA_ARCHIVO = os.path.join(DATA_DIR, "memoria.json")

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

    except:
        return default


def guardar_json(path, data):
    try:
        temp = path + ".tmp"
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp, path)
    except:
        pass

# ======================================================
# INTENCIÓN SIMPLE
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

    return "pensar"

# ======================================================
# FASTAPI
# ======================================================

app = FastAPI(title="IAtlas", version="5.0")

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

    # 🧠 TODO LO DEMÁS → CEREBRO
    respuesta = pensar(texto)
    return {"respuesta": respuesta}
