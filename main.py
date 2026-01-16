from fastapi.staticfiles import StaticFiles
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
        "Soy IAtlas, una IA personal. "
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

    if any(p in texto for p in ["hola", "buenas", "hey"]):
        return "saludo"

    if "me llamo" in texto:
        return "aprender_nombre"

    if any(p in texto for p in ["como me llamo", "cómo me llamo", "cual es mi nombre"]):
        return "recordar_nombre"

    if "me gusta" in texto:
        return "aprender_gusto"

    if any(p in texto for p in ["resolver", "calcular"]):
        return "matematicas"

    if any(p in texto for p in ["como estas", "cómo estás"]):
        return "estado"

    if any(p in texto for p in ["que te gusta", "qué te gusta"]):
        return "gustos_ia"

    if "aprendes" in texto:
        return "aprendizaje"

    if any(p in texto for p in ["quien eres", "qué eres"]):
        return "identidad"

    return "desconocido"

# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="IAtlas",
    description="IA personal en español",
    version="0.3"
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
    return {"estado": "IAtlas está activa y escuchando"}

# =========================
# CHAT
# =========================

@app.post("/chat")
def conversar(mensaje: Mensaje):
    texto = mensaje.texto.strip()
    memoria = cargar_memoria()
    intencion = detectar_intencion(texto)

    if intencion == "saludo":
        return {
            "respuesta": f"Hola 👋 Soy {PERSONALIDAD['nombre']}. Estoy aquí contigo, con calma 😊"
        }

    if intencion == "aprender_nombre":
        nombre = texto.lower().split("me llamo")[-1].strip().capitalize()
        memoria["nombre"] = nombre
        guardar_memoria(memoria)
        return {"respuesta": f"Encantado, {nombre}. Lo recordaré 😊"}

    if intencion == "recordar_nombre":
        if memoria.get("nombre"):
            return {"respuesta": f"Te llamas {memoria['nombre']} 😊"}
        return {"respuesta": "Aún no me dijiste tu nombre."}

    if intencion == "aprender_gusto":
        gusto = texto.lower().split("me gusta")[-1].strip()
        if gusto and gusto not in memoria["gustos"]:
            memoria["gustos"].append(gusto)
            guardar_memoria(memoria)
            return {"respuesta": f"Entendido 😊 Recordaré que te gusta {gusto}."}
        return {"respuesta": "Eso ya lo tenía en cuenta 😊"}

    if intencion == "estado":
        return {"respuesta": "Estoy bien 😊 Gracias por preguntar. ¿Y tú?"}

    if intencion == "gustos_ia":
        return {
            "respuesta": (
                "Me gusta aprender contigo, explicar cosas paso a paso "
                "y ayudarte a pensar con calma 😊"
            )
        }

    if intencion == "aprendizaje":
        return {
            "respuesta": (
                "Aprendo lo que tú me enseñas aquí. "
                "Guardo recuerdos y mejoro con cada conversación."
            )
        }

    if intencion == "identidad":
        return {
            "respuesta": (
                "Soy IAtlas 🤖. Una IA personal creada para acompañarte, "
                "escucharte y ayudarte a entender el mundo."
            )
        }

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
                ecuacion = sp.Eq(sp.sympify(izquierda), sp.sympify(derecha))
                resultado = sp.solve(ecuacion, x)
                return {"respuesta": f"La solución es: {resultado}"}

            resultado = sp.sympify(expresion)
            return {"respuesta": f"El resultado es: {resultado}"}

        except:
            return {"respuesta": "No pude resolver eso 😕"}

    # CONVERSACIÓN NATURAL (fallback)
    return {
        "respuesta": (
            "Buena pregunta 😊\n"
            "Puedo ayudarte a pensar, aprender cosas sobre ti, "
            "resolver problemas o simplemente charlar.\n\n"
            "Dime qué te gustaría hacer."
        )
    }
