import requests, json, os, re
from googlesearch import search
import trafilatura

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
MEMORIA_APRENDIZAJE = os.path.join(DATA_DIR, "conocimiento_propio.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extraer_entidad(texto):
    t = texto.lower()
    t = re.sub(r"[¿?¡!]", "", t)
    basura = ["sabes", "historia", "de", "los", "las", "el", "la", "sobre", "que", "dime", "cuentame", "extiendete", "mas", "todo", "detallado"]
    palabras = [p for p in t.split() if p not in basura]
    return " ".join(palabras).strip()

def formatear_respuesta(texto, entidad):
    """Crea un resumen con puntos clave rápido y limpio"""
    frases = [f.strip() for f in texto.split('.') if len(f.strip()) > 45]
    
    puntos = ""
    for f in frases[:5]: # Solo los 5 puntos más importantes para ser rápidos
        puntos += f"🔹 {f}.\n"
        
    return f"🏛️ **ARCHIVO IATLAS: {entidad.upper()}**\n\n" \
           f"✅ **RESUMEN EJECUTIVO:**\n{puntos}\n" \
           f"📜 **DETALLE:**\n{texto[:1200]}..."

def buscar_rapido_y_profundo(tema):
    """Busca en la mejor fuente disponible sin saturar el servidor"""
    try:
        query = f"{tema} historia detallada resumen"
        # Reducimos a los 2 mejores resultados para mayor velocidad
        urls = list(search(query, num_results=2, lang="es"))
        
        for url in urls:
            try:
                r = requests.get(url, headers=HEADERS, timeout=8) # Timeout más corto
                if r.status_code == 200:
                    contenido = trafilatura.extract(r.text, include_tables=True)
                    if contenido and len(contenido) > 500:
                        return contenido
            except: continue
    except Exception as e:
        print(f"Error: {e}")
    return None

def pensar(texto_usuario):
    if os.path.exists(MEMORIA_APRENDIZAJE):
        with open(MEMORIA_APRENDIZAJE, "r", encoding="utf-8") as f:
            memoria = json.load(f)
    else: memoria = {}

    entidad = extraer_entidad(texto_usuario)
    if not entidad or len(entidad) < 3:
        return "Hola Henry. ¿Qué imperio o evento histórico investigamos hoy?"

    # Intentar buscar información
    info = buscar_rapido_y_profundo(entidad)

    if info:
        respuesta = formatear_respuesta(info, entidad)
        # Guardamos un resumen en memoria
        memoria[entidad] = info[:1000]
        with open(MEMORIA_APRENDIZAJE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
        return respuesta
    
    return f"Henry, la información sobre '{entidad}' es difícil de acceder ahora mismo. ¿Podrías intentar con un nombre más común (ej: 'Cultura Inca')?"