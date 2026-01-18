# ======================================================
# IATLAS — MAIN SERVER (CUERPO FINAL)
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

    except Exception as e:
        print("[MEMORIA ERROR]", e)
        return default


def guardar_json(path, data):
    try:
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        print("[MEMORIA WRITE ERROR]", e)

# ======================================================
# DETECTOR DE INTENCIÓN (LIVIANO)
# ======================================================

def detectar_intencion(texto: str):
    t = texto.lower()

    if any(p in t for p in ["hola", "hey", "buenas", "saludos"]):
        return "saludo"

    if "me llamo" in t or "mi nombre es" in t:
        return "nombre"

    if "me gusta" in t:
        return "gusto"

    if any(p in t for p in ["resolver", "calcular", "cuanto es", "cuánto es"]):
        return "matematicas"

    return "pensar"

# ======================================================
# FASTAPI
# ======================================================

app = FastAPI(title="IAtlas", version="5.1")

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

# ======================================================
# ENDPOINTS
# ======================================================

@app.get("/chat")
def chat_ui():
    return FileResponse("static/chat.html")


@app.post("/chat")
def chat(m: Mensaje):

    texto = m.texto.strip()

    if not texto:
        return {"respuesta": "Dime algo para empezar 😊"}

    memoria = cargar_json(
        MEMORIA_ARCHIVO,
        {"nombre": None, "gustos": []}
    )

    intencion = detectar_intencion(texto)

    # --------------------------------------------------
    # SALUDO
    # --------------------------------------------------

    if intencion == "saludo":
        nombre = memoria.get("nombre")
        if nombre:
            return {"respuesta": f"Hola 👋 {nombre}, me alegra verte de nuevo."}
        return {"respuesta": "Hola 👋 Soy IAtlas."}

    # --------------------------------------------------
    # NOMBRE
    # --------------------------------------------------

    if intencion == "nombre":
        nombre = texto.lower().split()[-1].capitalize()
        memoria["nombre"] = nombre
        guardar_json(MEMORIA_ARCHIVO, memoria)
        return {"respuesta": f"Encantado {nombre} 😊. Lo recordaré."}

    # --------------------------------------------------
    # GUSTOS
    # --------------------------------------------------

    if intencion == "gusto":
        gusto = texto.lower().split("me gusta")[-1].strip()
        if gusto and gusto not in memoria["gustos"]:
            memoria["gustos"].append(gusto)
            guardar_json(MEMORIA_ARCHIVO, memoria)
        return {"respuesta": f"Perfecto 👍 recordaré que te gusta {gusto}."}

    # --------------------------------------------------
    # MATEMÁTICAS
    # --------------------------------------------------

    if intencion == "matematicas":
        try:
            expr = (
                texto.lower()
                .replace("resolver", "")
                .replace("calcular", "")
                .replace("cuanto es", "")
                .replace("cuánto es", "")
                .replace("?", "")
                .strip()
            )

            resultado = sp.sympify(expr)
            return {"respuesta": f"El resultado es {resultado}."}

        except Exception:
            return {
                "respuesta":
                "No pude resolver esa operación 😕. Ejemplo válido: 2+2"
            }

    # --------------------------------------------------
    # 🧠 TODO LO DEMÁS → CEREBRO
    # --------------------------------------------------

    try:
        respuesta = pensar(texto)
        return {"respuesta": respuesta}
    except Exception as e:
        print("[CEREBRO ERROR]", e)
        return {
            "respuesta":
            "Tuve un problema al procesar eso 😕. Intenta formularlo de otra manera."
        }
