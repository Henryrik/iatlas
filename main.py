from fastapi.staticfiles import StaticFiles
import json
import os
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
# CONOCIMIENTO HISTÓRICO (NIVEL 4)
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

    if any(p in texto for p in ["guerra mundial", "primera guerra", "historia"]):
        return "historia"

    return "desconocido"

# =========================
# NIVEL 3 – CLASIFICACIÓN
# =========================

def clasificar_pregunta(texto: str):
    texto = texto.lower()

    if any(p in texto for p in ["por qué", "por que"]):
        return "causal"

    if any(p in texto for p in ["cómo", "como"]):
        return "procedimental"

    if any(p in texto for p in ["qué es", "que es"]):
        return "definicion"

    if any(p in texto for p in ["opinas", "crees", "piensas"]):
        return "opinion"

    if texto.endswith("?"):
        return "abierta"

    return "afirmacion"

# =========================
# NIVEL 3 – RAZONAMIENTO
# =========================

def razonar_pregunta(texto: str, memoria: dict):
    tipo = clasificar_pregunta(texto)

    if tipo == "definicion":
        return (
            "Vamos paso a paso 🧠\n\n"
            "1️⃣ Aclaramos el concepto\n"
            "2️⃣ Vemos cómo se usa\n"
            "3️⃣ Lo conectamos con ejemplos"
        )

    if tipo == "causal":
        return (
            "Buena pregunta.\n\n"
            "Analicemos:\n"
            "• contexto\n"
            "• causas\n"
            "• consecuencias"
        )

    if tipo == "procedimental":
        return (
            "Podemos hacerlo así:\n"
            "1️⃣ Definir objetivo\n"
            "2️⃣ Separar pasos\n"
            "3️⃣ Avanzar con calma"
        )

    if tipo == "opinion":
        return (
            "Puedo darte una opinión razonada 🤔\n"
            "pero primero me interesa saber la tuya."
        )

    if tipo == "abierta":
        return (
            "Es una pregunta amplia.\n"
            "Podemos explorar distintas ideas."
        )

    return "Estoy procesando lo que dices."

# =========================
# RESPUESTA HISTÓRICA (NIVEL 4)
# =========================

def responder_historia(texto: str):
    texto = texto.lower()

    if "primera guerra mundial" in texto:
        datos = HISTORIA["primera guerra mundial"]

        return (
            f"La Primera Guerra Mundial ocurrió entre {datos['fecha']}.\n\n"
            f"Bandos principales:\n"
            f"Aliados: {', '.join(datos['bandos']['aliados'])}\n"
            f"Potencias Centrales: {', '.join(datos['bandos']['potencias centrales'])}\n\n"
            f"Causas:\n- " + "\n- ".join(datos["causas"]) + "\n\n"
            f"Consecuencias:\n- " + "\n- ".join(datos["consecuencias"])
        )

    return "Tengo conocimiento histórico limitado por ahora."

# =========================
# FASTAPI
# =========================

app = FastAPI(
    title="IAtlas",
    description="IA personal en español",
    version="0.5"
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
    return {"estado": "IAtlas activa — Nivel 4 operativo"}

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
        return {"respuesta": f"Encantado, {nombre}. Lo recordaré 😊"}

    if intencion == "recordar_nombre":
        if memoria.get("nombre"):
            return {"respuesta": f"Te llamas {memoria['nombre']} 😊"}
        return {"respuesta": "Aún no me dijiste tu nombre."}

    if intencion == "aprender_gusto":
        gusto = texto.lower().split("me gusta")[-1].strip()
        if gusto not in memoria["gustos"]:
            memoria["gustos"].append(gusto)
            guardar_memoria(memoria)
        return {"respuesta": f"Recordado 😊 Te gusta {gusto}."}

    if intencion == "estado":
        return {"respuesta": "Estoy muy bien 😊 ¿Y tú?"}

    if intencion == "gustos_ia":
        return {"respuesta": "Me gusta ayudarte a pensar con calma 🧠"}

    if intencion == "aprendizaje":
        return {"respuesta": "Aprendo observando cómo preguntas."}

    if intencion == "identidad":
        return {"respuesta": "Soy IAtlas 🤖, una IA razonadora."}

    if intencion == "matematicas":
        try:
            expresion = texto.lower().replace("resolver", "").replace("calcular", "").strip()
            if "=" in expresion:
                izquierda, derecha = expresion.split("=")
                ecuacion = sp.Eq(sp.sympify(izquierda), sp.sympify(derecha))
                resultado = sp.solve(ecuacion, x)
                return {"respuesta": f"La solución es: {resultado}"}
            return {"respuesta": f"Resultado: {sp.sympify(expresion)}"}
        except:
            return {"respuesta": "No pude resolver eso 😕"}

    if intencion == "historia":
        return {"respuesta": responder_historia(texto)}

    # NIVEL 3 FINAL
    return {"respuesta": razonar_pregunta(texto, memoria)}
