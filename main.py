from fastapi.staticfiles import StaticFiles
import json
import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sympy as sp
from fastapi.responses import FileResponse

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
# CONOCIMIENTO LOCAL (Nivel 4)
# =========================

HISTORIA = {
    "primera guerra mundial": {
        "fecha": "1914–1918",
        "bandos": {
            "aliados": [
                "Francia",
                "Reino Unido",
                "Rusia",
                "Estados Unidos",
                "Italia"
            ],
            "potencias centrales": [
                "Alemania",
                "Imperio Austrohúngaro",
                "Imperio Otomano",
                "Bulgaria"
            ]
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
            "Inestabilidad política en Europa",
            "Camino hacia la Segunda Guerra Mundial"
        ]
    }
}

# =========================
# MEMORIA PERSONAL
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
# DETECTOR DE INTENCIONES
# =========================

def detectar_intencion(texto: str):
    texto = texto.lower()

    if any(p in texto for p in ["hola", "buenas", "hey"]):
        return "saludo"

    if "me llamo" in texto:
        return "aprender_nombre"

    if "me gusta" in texto:
        return "aprender_gusto"

    if any(p in texto for p in ["resolver", "calcular"]):
        return "matematicas"

    if any(p in texto for p in ["quien eres", "qué eres"]):
        return "identidad"

    if "historia" in texto or "guerra" in texto:
        return "historia"

    return "general"

# =========================
# NIVEL 3 – RAZONAMIENTO
# =========================

def razonar_pregunta(texto: str):
    texto = texto.lower()

    if "por qué" in texto:
        return (
            "Para entenderlo mejor analicemos:\n"
            "• contexto histórico\n"
            "• causas principales\n"
            "• consecuencias\n"
        )

    if "cómo" in texto:
        return (
            "Podemos explicarlo paso a paso:\n"
            "1️⃣ Situación inicial\n"
            "2️⃣ Desarrollo\n"
            "3️⃣ Resultado"
        )

    return "Podemos profundizar más si quieres."

# =========================
# HISTORIA LOCAL
# =========================

def responder_historia_local(texto: str):
    texto = texto.lower()

    if "primera guerra mundial" in texto:
        d = HISTORIA["primera guerra mundial"]
        return (
            f"La Primera Guerra Mundial ocurrió entre {d['fecha']}.\n\n"
            f"Aliados: {', '.join(d['bandos']['aliados'])}\n"
            f"Potencias Centrales: {', '.join(d['bandos']['potencias centrales'])}\n\n"
            f"Causas:\n- " + "\n- ".join(d["causas"]) + "\n\n"
            f"Consecuencias:\n- " + "\n- ".join(d["consecuencias"])
        )

    return None

# =========================
# WIKIPEDIA (CONOCIMIENTO TEMPORAL)
# =========================

def buscar_wikipedia(tema: str):
    url = "https://es.wikipedia.org/api/rest_v1/page/summary/" + tema.replace(" ", "_")

    try:
        r = requests.get(url, timeout=6)
        if r.status_code != 200:
            return None

        data = r.json()
        return data.get("extract")

    except:
        return None

# =========================
# SISTEMA HÍBRIDO
# =========================

def obtener_conocimiento_historico(texto: str):

    # 1️⃣ memoria local
    local = responder_historia_local(texto)
    if local:
        return local

    # 2️⃣ búsqueda externa
    externo = buscar_wikipedia(texto)
    if externo:
        return externo

    return (
        "No encontré información directa, "
        "pero puedo ayudarte a analizar el contexto histórico."
    )

# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="IAtlas",
    description="IA híbrida histórica",
    version="1.0"
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
    return {"estado": "IAtlas híbrido activo"}

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

    if intencion == "aprender_nombre":
        nombre = texto.lower().split("me llamo")[-1].strip().capitalize()
        memoria["nombre"] = nombre
        guardar_memoria(memoria)
        return {"respuesta": f"Encantado {nombre}, lo recordaré 😊"}

    if intencion == "aprender_gusto":
        gusto = texto.lower().split("me gusta")[-1].strip()
        memoria["gustos"].append(gusto)
        guardar_memoria(memoria)
        return {"respuesta": f"Entendido 😊 Te gusta {gusto}."}

    if intencion == "matematicas":
        try:
            expr = texto.replace("resolver", "").replace("calcular", "")
            return {"respuesta": str(sp.sympify(expr))}
        except:
            return {"respuesta": "No pude resolverlo 😕"}

    if intencion == "historia":
        return {"respuesta": obtener_conocimiento_historico(texto)}

    return {"respuesta": razonar_pregunta(texto)}
