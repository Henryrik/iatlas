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
    basura = ["sabes", "historia", "de", "los", "las", "el", "la", "sobre", "que", "dime", "cuentame", "extiendete", "mas", "cuéntame", "extiéndete", "todo", "detallado"]
    palabras = [p for p in t.split() if p not in basura]
    return " ".join(palabras).strip()

def formatear_respuesta_total(texto, entidad):
    """Estructura una respuesta de nivel enciclopédico"""
    # Dividimos en párrafos para detectar puntos clave de forma natural
    parrafos = [p for p in texto.split('\n') if len(p.strip()) > 50]
    
    resumen_puntos = ""
    for i, p in enumerate(parrafos[:8]): # Extraemos hasta 8 puntos clave del contenido real
        resumen_puntos += f"🔹 {p[:150]}...\n"

    return f"🏛️ **ENCICLOPEDIA IATLAS: {entidad.upper()}**\n\n" \
           f"🧐 **ANÁLISIS DE PUNTOS CLAVE:**\n{resumen_puntos}\n" \
           f"📜 **CRÓNICA COMPLETA:**\n{texto}"

def buscar_en_internet_sin_limites(tema):
    """Busca en múltiples fuentes y combina el conocimiento"""
    try:
        # Buscamos fuentes académicas y detalladas
        query = f"{tema} historia profunda cronología completa detalles"
        urls = list(search(query, num_results=5, lang="es"))
        
        conocimiento_acumulado = ""
        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                # Extraemos TODO el texto disponible sin límites estrictos
                texto = trafilatura.extract(r.text, include_comments=False, include_tables=True, include_links=False)
                if texto and len(texto) > 600:
                    conocimiento_acumulado += f"\n--- Fuente: {url} ---\n{texto}\n"
                    if len(conocimiento_acumulado) > 8000: break # Límite de seguridad para el servidor
        
        return conocimiento_acumulado if conocimiento_acumulado else None
    except Exception as e:
        print(f"Error en investigación profunda: {e}")
        return None

def pensar(texto_usuario):
    if os.path.exists(MEMORIA_APRENDIZAJE):
        with open(MEMORIA_APRENDIZAJE, "r", encoding="utf-8") as f:
            memoria = json.load(f)
    else: memoria = {}

    entidad = extraer_entidad(texto_usuario)
    if not entidad: return "Hola Henry. El conocimiento no tiene límites. ¿Qué civilización o evento exploramos hoy?"

    # Siempre busca información fresca si el usuario pide "todo" o detalle
    info_texto = buscar_en_internet_sin_limites(entidad)

    if info_texto:
        respuesta_final = formatear_respuesta_total(info_texto, entidad)
        
        # Guardamos en memoria para aprendizaje continuo
        memoria[entidad] = info_texto[:5000] # Guardamos un fragmento grande en JSON
        with open(MEMORIA_APRENDIZAJE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
        
        return respuesta_final
    
    return f"Henry, la historia de '{entidad}' es vasta, pero los archivos digitales están protegidos en este momento. Intentemos con un término relacionado."