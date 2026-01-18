import requests, json, os, re
from googlesearch import search
import trafilatura

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
MEMORIA_APRENDIZAJE = os.path.join(DATA_DIR, "conocimiento_propio.json")

# 🛡️ ESTO ES LO QUE FALTA: La identificación para que no nos bloqueen
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extraer_entidad(texto):
    t = texto.lower()
    t = re.sub(r"[¿?¡!]", "", t)
    # Limpiamos palabras que confunden al buscador
    basura = ["sabes", "historia", "de", "los", "las", "el", "la", "sobre", "que", "dime", "cuentame"]
    palabras = [p for p in t.split() if p not in basura]
    return " ".join(palabras).strip()

def buscar_en_internet(tema):
    """Explora la web usando una identidad humana para evitar bloqueos"""
    try:
        # Buscamos en Google
        query = f"{tema} historia resumen"
        urls = list(search(query, num_results=3, lang="es"))
        
        for url in urls:
            # Usamos los HEADERS de identificación aquí
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                texto = trafilatura.extract(r.text)
                if texto and len(texto) > 300:
                    return f"{texto[:800]}...\n\n(Fuente: {url})"
    except Exception as e:
        print(f"Error de exploración: {e}")
    return None

def pensar(texto_usuario):
    # Cargar memoria local
    if os.path.exists(MEMORIA_APRENDIZAJE):
        with open(MEMORIA_APRENDIZAJE, "r", encoding="utf-8") as f:
            memoria = json.load(f)
    else: memoria = {}

    entidad = extraer_entidad(texto_usuario)
    if not entidad: return "Hola Henry, ¿qué tema investigamos hoy?"

    if entidad in memoria:
        respuesta = memoria[entidad]
    else:
        # 1. Intentar Wikipedia con identificación
        try:
            wiki_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{entidad.replace(' ', '_')}"
            res = requests.get(wiki_url, headers=HEADERS, timeout=7).json()
            respuesta = res.get("extract")
        except: respuesta = None

        # 2. Si Wikipedia falla, navegar por la web real
        if not respuesta:
            respuesta = buscar_en_internet(entidad)

    if respuesta:
        memoria[entidad] = respuesta
        with open(MEMORIA_APRENDIZAJE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
        return f"🌐 **Consulta para: {entidad.upper()}**\n\n{respuesta}"
    
    return f"Lo siento, Henry. Busqué en la web pero los sitios están protegiendo su información. Intenta con 'Incas' o 'Cultura Maya'."