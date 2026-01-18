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
    # Limpieza masiva de ruido para encontrar el núcleo del tema
    basura = ["sabes", "historia", "de", "los", "las", "el", "la", "sobre", "que", "dime", "cuentame", "extiendete", "mas", "todo", "detallado", "como", "ocurrio", "disuelva", "desaparecio"]
    palabras = [p for p in t.split() if p not in basura]
    return " ".join(palabras).strip()

def formatear_erudito(texto, entidad):
    """Crea una estructura de reporte ejecutivo con puntos clave"""
    # Limpieza de saltos de línea excesivos
    texto_limpio = re.sub(r'\n+', '\n', texto).strip()
    parrafos = [p for p in texto_limpio.split('.') if len(p.strip()) > 40]
    
    # Construcción de Puntos Clave
    puntos_clave = ""
    for i, p in enumerate(parrafos[:6]):
        puntos_clave += f"🔹 {p.strip()}.\n"

    return f"🏛️ **ARCHIVO HISTÓRICO: {entidad.upper()}**\n\n" \
           f"✅ **RESUMEN EJECUTIVO (Puntos Clave):**\n{puntos_clave}\n" \
           f"📜 **CRÓNICA DETALLADA:**\n{texto_limpio[:4000]}..."

def investigacion_profunda(tema):
    """Navega por múltiples sitios para extraer conocimiento sin límites"""
    try:
        # Búsqueda ampliada para evitar bloqueos
        consultas = [f"{tema} historia completa detallada", f"por que desaparecio {tema}", f"cronologia de {tema}"]
        conocimiento_acumulado = ""
        
        for q in consultas:
            urls = list(search(q, num_results=3, lang="es"))
            for url in urls:
                try:
                    r = requests.get(url, headers=HEADERS, timeout=15)
                    if r.status_code == 200:
                        contenido = trafilatura.extract(r.text, include_tables=True, include_comments=False)
                        if contenido and len(contenido) > 500:
                            conocimiento_acumulado += f"\n{contenido}\n"
                            if len(conocimiento_acumulado) > 6000: break
                except: continue
            if len(conocimiento_acumulado) > 3000: break
            
        return conocimiento_acumulado if conocimiento_acumulado else None
    except Exception as e:
        print(f"Error en gran archivo: {e}")
        return None

def pensar(texto_usuario):
    if os.path.exists(MEMORIA_APRENDIZAJE):
        with open(MEMORIA_APRENDIZAJE, "r", encoding="utf-8") as f:
            memoria = json.load(f)
    else: memoria = {}

    entidad = extraer_entidad(texto_usuario)
    if not entidad or len(entidad) < 3: 
        return "Hola Henry. Soy IAtlas, tu historiador personal. ¿Qué civilización quieres que investigue a fondo?"

    # Iniciamos búsqueda sin límites
    info_total = investigacion_profunda(entidad)

    if info_total:
        respuesta_formateada = formatear_erudito(info_total, entidad)
        
        # Guardar aprendizaje
        memoria[entidad] = info_total[:2000]
        with open(MEMORIA_APRENDIZAJE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
            
        return respuesta_formateada
    
    return f"Henry, he rastreado los archivos sobre '{entidad}' pero los sitios están inaccesibles ahora. Intenta con un término más general como 'Imperio Inca' o 'Antiguo Egipto'."