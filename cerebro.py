import requests, json, os, re
from googlesearch import search
import trafilatura

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
MEMORIA_APRENDIZAJE = os.path.join(DATA_DIR, "conocimiento_propio.json")

# 🛡️ Identificación para evitar bloqueos
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def extraer_entidad(texto):
    t = texto.lower()
    t = re.sub(r"[¿?¡!]", "", t)
    # Mejoramos la limpieza para detectar cuando el usuario pide "más"
    basura = ["sabes", "historia", "de", "los", "las", "el", "la", "sobre", "que", "dime", "cuentame", "extiendete", "mas", "cuéntame", "extiéndete"]
    palabras = [p for p in t.split() if p not in basura]
    return " ".join(palabras).strip()

def buscar_en_internet(tema, extensa=False):
    """Explora la web y extrae contenido mucho más amplio"""
    try:
        # Si el usuario pide extenderse, usamos palabras clave más potentes
        query = f"{tema} historia completa detalles" if extensa else f"{tema} historia resumen"
        urls = list(search(query, num_results=3, lang="es"))
        
        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                # Extraemos con formato y tablas si es posible
                texto = trafilatura.extract(r.text, include_comments=False, include_tables=True)
                if texto and len(texto) > 400:
                    # Si es extensa, devolvemos hasta 3000 caracteres, si no, 800
                    limite = 3000 if extensa else 800
                    return f"{texto[:limite]}...\n\n(Fuente: {url})"
    except Exception as e:
        print(f"Error de exploración: {e}")
    return None

def pensar(texto_usuario):
    # Cargar memoria local
    if os.path.exists(MEMORIA_APRENDIZAJE):
        with open(MEMORIA_APRENDIZAJE, "r", encoding="utf-8") as f:
            memoria = json.load(f)
    else: memoria = {}

    # Detectar si el usuario quiere más información
    quiere_mas = any(p in texto_usuario.lower() for p in ["mas", "extiendete", "detalle", "profundiza"])
    entidad = extraer_entidad(texto_usuario)
    
    if not entidad: return "Hola Henry, ¿sobre qué imperio o cultura quieres profundizar hoy?"

    # Lógica de búsqueda profunda
    if entidad in memoria and not quiere_mas:
        respuesta = memoria[entidad]
    else:
        # Intentar Wikipedia primero (solo si no es un pedido de extensión profunda)
        respuesta = None
        if not quiere_mas:
            try:
                wiki_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{entidad.replace(' ', '_')}"
                res = requests.get(wiki_url, headers=HEADERS, timeout=7).json()
                respuesta = res.get("extract")
            except: respuesta = None

        # 🚀 Si Wikipedia no basta o piden "más", navegar por la web real de forma extensa
        if not respuesta or quiere_mas:
            respuesta = buscar_en_internet(entidad, extensa=quiere_mas)

    if respuesta:
        memoria[entidad] = respuesta
        with open(MEMORIA_APRENDIZAJE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, ensure_ascii=False, indent=2)
        
        titulo = f"📚 INVESTIGACIÓN DETALLADA: {entidad.upper()}" if quiere_mas else f"🌐 CONSULTA: {entidad.upper()}"
        return f"**{titulo}**\n\n{respuesta}"
    
    return f"Henry, busqué información extensa sobre '{entidad}', pero los sitios están protegidos. ¿Intentamos con otro tema?"