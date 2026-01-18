# ======================================================
# IATLAS — CEREBRO HISTÓRICO HÍBRIDO v3.1 (ACTUALIZADO)
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
# CONFIGURACIÓN Y ESTADO GLOBAL
# ======================================================

x = sp.symbols("x")
MEMORIA_ARCHIVO = "memoria.json"
# Esta variable permite que la IA recuerde el tema anterior en la misma sesión
CONTEXTO = {"ultimo_tema": None}

PERSONALIDAD = {
    "nombre": "IAtlas",
    "descripcion": "IA histórica con razonamiento híbrido"
}

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
# GESTIÓN DE MEMORIA DE ARCHIVO
# ======================================================

def cargar_memoria():
    if not os.path.exists(MEMORIA_ARCHIVO):
        return {"nombre": None, "gustos": []}
    with open(MEMORIA_ARCHIVO, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"nombre": None, "gustos": []}

def guardar_memoria(memoria):
    with open(MEMORIA_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

# ======================================================
# LÓGICA DE PROCESAMIENTO (CEREBRO)
# ======================================================

def detectar_intencion(texto: str):
    t = texto.lower()
    
    # Saludos
    if any(p in t for p in ["hola", "hey", "buenas", "saludos"]):
        return "saludo"

    # Identificación personal
    if any(p in t for p in ["me llamo", "mi nombre es"]):
        return "nombre"

    # Preferencias
    if "me gusta" in t:
        return "gusto"

    # Matemáticas
    if any(p in t for p in ["resolver", "calcular", "cuanto es", "cuánto es"]):
        return "matematicas"

    # Historia (Incluye palabras clave de seguimiento)
    palabras_historia = [
        "inca", "maya", "romano", "egipto", "grecia", "imperio", 
        "civilizacion", "historia", "quien fue", "cuéntame", "dime más"
    ]
    if any(p in t for p in palabras_historia):
        return "historia"

    return "general"

def extraer_tema(texto: str):
    t_original = texto.lower()
    
    # Gestión de contexto: si el usuario pide "más" y ya hablábamos de algo
    palabras_continuacion = ["más", "mas", "continua", "sigue", "háblame más"]
    if any(p in t_original for p in palabras_continuacion) and CONTEXTO["ultimo_tema"]:
        return CONTEXTO["ultimo_tema"]

    # Limpieza de texto para encontrar el núcleo del tema
    texto_limpio = re.sub(r"[^\w\s]", "", t_original)
    basura = {
        "historia","de","los","las","el","la", "sobre","acerca","puedes",
        "explicame","que","qué","en","un","una","por","favor","sabes",
        "hablame","háblame", "quien", "quién", "fue", "era"
    }

    palabras = [p for p in texto_limpio.split() if p not in basura]
    tema_candidato = " ".join(palabras)

    # Buscar en el mapa semántico o devolver el tema limpio
    tema_final = MAPA_HISTORICO.get(tema_candidato, tema_candidato)
    
    # Actualizar contexto para la próxima pregunta
    if tema_final:
        CONTEXTO["ultimo_tema"] = tema_final
        
    return tema_final

def buscar_wikipedia(tema: str):
    if not tema: return None
    try:
        search_url = f"https://es.wikipedia.org/w/api.php?action=query&list=search&srsearch={tema}&format=json"
        r = requests.get(search_url, timeout=8)
        data = r.json()

        resultados = data.get("query", {}).get("search", [])
        if not resultados:
            return None

        titulo = resultados[0]["title"]
        summary_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{titulo.replace(' ', '_')}"

        r2 = requests.get(summary_url, timeout=8)
        if r2.status_code == 200:
            return r2.json().get("extract")
    except:
        return None
    return None

def conocimiento_historico(texto: str):
    texto_l = texto.lower()

    # 1. Verificar Memoria Local
    for clave in HISTORIA_LOCAL:
        if clave in texto_l:
            return HISTORIA_LOCAL[clave]

    # 2. Extraer tema (con gestión de contexto)
    tema = extraer_tema(texto)

    # 3. Buscar en Wikipedia
    info = buscar_wikipedia(tema)
    if info:
        return info

    return (
        f"No encontré información detallada sobre «{tema}».\n\n"
        "¿Podrías darme más detalles o preguntar sobre otra época?"
    )

# ======================================================
# API (FASTAPI)
# ======================================================

app = FastAPI(title="IAtlas", version="3.1")

# Asegúrate de tener la carpeta 'static' creada
if not os.path.exists("static"):
    os.makedirs("static")

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
    return {"estado": "IAtlas v3.1 activo", "contexto_actual": CONTEXTO["ultimo_tema"]}

@app.get("/chat")
def chat_ui():
    return FileResponse("static/chat.html")

@app.post("/chat")
def chat(mensaje: Mensaje):
    texto = mensaje.texto.strip()
    if not texto:
        return {"respuesta": "Dime algo para empezar."}

    memoria = cargar_memoria()
    intencion = detectar_intencion(texto)

    if intencion == "saludo":
        nombre_usuario = memoria.get("nombre")
        saludo = f"¡Hola! Soy IAtlas 👋"
        if nombre_usuario:
            saludo += f", qué bueno verte de nuevo, {nombre_usuario}."
        return {"respuesta": saludo}

    if intencion == "nombre":
        # Intenta extraer el nombre después de "me llamo" o "es"
        nombre = texto.lower().split("llamo")[-1].replace("me ", "").strip().capitalize()
        memoria["nombre"] = nombre
        guardar_memoria(memoria)
        return {"respuesta": f"Mucho gusto, {nombre}. He guardado tu nombre en mi memoria. 😊"}

    if intencion == "gusto":
        gusto = texto.lower().split("me gusta")[-1].strip()
        if gusto not in memoria["gustos"]:
            memoria["gustos"].append(gusto)
            guardar_memoria(memoria)
        return {"respuesta": f"Anotado. Recordaré que te gusta '{gusto}'."}

    if intencion == "matematicas":
        try:
            # Limpiar la cadena para Sympy
            expr = texto.lower().replace("resolver", "").replace("calcular", "").replace("cuanto es", "").replace("?", "").strip()
            resultado = sp.sympify(expr)
            return {"respuesta": f"El resultado de {expr} es {resultado}."}
        except:
            return {"respuesta": "No pude procesar esa operación matemática. Asegúrate de usar números y símbolos claros (ej: 2+2)."}

    if intencion == "historia":
        return {"respuesta": conocimiento_historico(texto)}

    return {"respuesta": "¿Te gustaría que hablemos de historia, o prefieres que resuelva algún cálculo?"}