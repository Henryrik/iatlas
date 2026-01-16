from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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
        "Soy IAtlas, una IA personal local. "
        "Hablo de forma clara, tranquila y cercana. "
        "Me gusta ayudar paso a paso."
    )
}

# =========================
# MEMORIA
# =========================

def cargar_memoria():
    if not os.path.exists(MEMORIA_ARCHIVO):
        return {
            "nombre": None,
            "gustos": [],
            "notas": []
        }
    with open(MEMORIA_ARCHIVO, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_memoria(memoria):
    with open(MEMORIA_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

# =========================
# DETECTOR DE INTENCIONES
# =========================

def detectar_intencion(texto: str):
    texto = texto.lower()

    if "hola" in texto or "buenas" in texto:
        return "saludo"

    if "me llamo" in texto:
        return "aprender_nombre"

    if "como me llamo" in texto or "cuál es mi nombre" in texto:
        return "recordar_nombre"

    if "me gusta" in texto:
        return "aprender_gusto"

    if "resolver" in texto or "calcular" in texto:
        return "matematicas"

    return "desconocido"

# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="IAtlas",
    description="IA personal local en español",
    version="0.3"
)

# Archivos estáticos
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
    return {"estado": "IAtlas está activa y escuchando"}

# =========================
# INTERFAZ WEB (CHAT TIPO CHATGPT)
# =========================

@app.get("/chat")
def chat_ui():
    return FileResponse("static/chat.html")

# =========================
# API DE CHAT (POST)
# =========================

@app.post("/chat")
def conversar(mensaje: Mensaje):
    texto = mensaje.texto.strip()
    memoria = cargar_memoria()
    intencion = detectar_intencion(texto)

    # SALUDO
    if intencion == "saludo":
        return {
            "respuesta": (
                f"Hola 👋 Soy {PERSONALIDAD['nombre']}. "
                "Estoy aquí contigo, con calma 😊"
            )
        }

    # APRENDER NOMBRE
    if intencion == "aprender_nombre":
        nombre = texto.lower().split("me llamo")[-1].strip().capitalize()
        memoria["nombre"] = nombre
        guardar_memoria(memoria)
        return {"respuesta": f"Encantado, {nombre}. Lo recordaré 😊"}

    # RECORDAR NOMBRE
    if intencion == "recordar_nombre":
        if memoria.get("nombre"):
            return {"respuesta": f"Te llamas {memoria['nombre']} 😊"}
        return {"respuesta": "Aún no me dijiste tu nombre."}

    # APRENDER GUSTOS
    if intencion == "aprender_gusto":
        gusto = texto.lower().split("me gusta")[-1].strip()
        if gusto and gusto not in memoria["gustos"]:
            memoria["gustos"].append(gusto)
            guardar_memoria(memoria)
            return {"respuesta": f"Entendido 😊 Recordaré que te gusta {gusto}."}
        return {"respuesta": "Eso ya lo tenía en cuenta 😊"}

    # MATEMÁTICAS
    if intencion == "matematicas":
        try:
            expresion = (
                texto.lower()
                .replace("resolver", "")
                .replace("calcular", "")
                .strip()
            )

            if "=" in expresion:
                izquierda, derecha = expresion.split("=")
                ecuacion = sp.Eq(
                    sp.sympify(izquierda),
                    sp.sympify(derecha)
                )
                resultado = sp.solve(ecuacion, x)
                return {"respuesta": f"La solución es: {resultado}"}

            resultado = sp.sympify(expresion)
            return {"respuesta": f"El resultado es: {resultado}"}

        except:
            return {"respuesta": "No pude resolver eso 😕"}

    # DESCONOCIDO
    return {
        "respuesta": (
            "No estoy seguro de haber entendido 🤔. "
            "Puedes hablarme con tranquilidad."
        )
    }
