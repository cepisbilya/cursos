import requests
from bs4 import BeautifulSoup
import json
import re

# ============================================
# 1) SECRETARÍA VIRTUAL (OFICIAL)
# ============================================

BASE_URL = "https://secretariavirtual.juntadeandalucia.es/secretariavirtual/consultaCEP"
SEARCH_URL = f"{BASE_URL}/buscar/"

CENTROS_SV = {
    "5265": "SEVILLA",
    "5266": "CASTILLEJA",
    "5267": "OSUNA",
    "5268": "MAIRENA",
    "5269": "LEBRIJA",
    "5270": "LORA DEL RÍO",
}

def crear_sesion():
    s = requests.Session()
    s.get(BASE_URL + "/", timeout=15)
    return s

def buscar_sv(session, centro_id):
    payload = {
        "centro": centro_id,
        "modalidad": "-1",
        "_modalidad": "1",
        "dirigido": "-1",
        "estado": "-1",
        "fechaI": "",
        "fechaF": "",
        "titulo": "",
        "codigoEdicion": "",
        "descriptor": "-1",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": BASE_URL + "/",
    }

    r = session.post(SEARCH_URL, data=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.text

def parsear_sv(html, cep_nombre):
    soup = BeautifulSoup(html, "html.parser")
    tabla = soup.find("table", id="tableCEP")
    if not tabla:
        return []

    cabeceras = [th.get_text(strip=True) for th in tabla.find("thead").find_all("th")]
    actividades = []

    for fila in tabla.find("tbody").find_all("tr"):
        celdas = [td.get_text(strip=True) for td in fila.find_all("td")]
        if not celdas:
            continue

        a = dict(zip(cabeceras, celdas))
        estado = (a.get("Estado", "") or "").upper()

        if "ABIERTO" not in estado:
            continue

        enlace = fila.find("a", href=True)
        url = enlace["href"] if enlace else ""
        if url.startswith("/"):
            url = "https://secretariavirtual.juntadeandalucia.es" + url

        actividades.append({
            "titulo": a.get("Título", ""),
            "cep": cep_nombre,
            "inicio": a.get("Inicio", ""),
            "fin": a.get("Fin", ""),
            "estado": estado,
            "url": url,
            "fuente": "SV"
        })

    return actividades


# ============================================
# 2) CEPS — SCRAPING HTML DE ACTIVIDADES-FORMATIVAS
# ============================================

CEPS_HTML = {
    "SEVILLA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-sevilla/actividades-formativas",
    "CASTILLEJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-castilleja-cuesta/actividades-formativas",
    "OSUNA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-osuna-ecija/actividades-formativas",
    "MAIRENA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-mairena-alcor/actividades-formativas",
    "LEBRIJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-lebrija/actividades-formativas",
    "LORA DEL RÍO": "https://www.juntadeandalucia.es/educacion/portales/web/cep-lora-rio/actividades-formativas"
}

PATRON_ACTIVIDAD = re.compile(r"/educacion/portales/web/cep-[a-z\-]+/actividad", re.IGNORECASE)

def scrape_cep_html(nombre, url):
    print(f"Scraping HTML CEP {nombre}…")

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    actividades = []
    vistos = set()

    # 1. Buscar cualquier enlace que apunte a una actividad
    enlaces = soup.find_all("a", href=True)

    for a in enlaces:
        href = a["href"]

        # Detectar cualquier patrón de actividad
        if not re.search(r"/actividad", href, re.IGNORECASE):
            continue

        # Evitar duplicados
        if href in vistos:
            continue
        vistos.add(href)

        # Construir URL absoluta
        url_curso = href
        if url_curso.startswith("/"):
            url_curso = "https://www.juntadeandalucia.es" + url_curso

        # Título
        titulo = a.get_text(strip=True)
        if len(titulo) < 4:
            continue

        # Buscar bloque padre para extraer fechas y estado
        bloque = a.find_parent()
        texto = bloque.get_text(" ", strip=True).upper() if bloque else titulo.upper()

        # Fechas
        fechas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
        inicio = fechas[0] if len(fechas) >= 1 else ""
        fin = fechas[1] if len(fechas) >= 2 else ""

        # Estado
        if "ABIERTO" in texto or "PLAZO" in texto:
            estado = "ABIERTO PLAZO SOLICITUDES"
        else:
            estado = "DESCONOCIDO"

        actividades.append({
            "titulo": titulo,
            "cep": nombre,
            "inicio": inicio,
            "fin": fin,
            "estado": estado,
            "url": url_curso,
            "fuente": "CEP-HTML"
        })

    return actividades



# ============================================
# 3) FUSIÓN DE RESULTADOS
# ============================================

def fusionar(sv, ceps_html):
    fusion = {}

    for a in ceps_html + sv:
        clave = (a["titulo"].upper(), a["cep"].upper())
        if clave not in fusion:
            fusion[clave] = a
        else:
            if a["fuente"] == "SV":
                fusion[clave] = a

    return list(fusion.values())


# ============================================
# 4) MAIN
# ============================================

def main():
    # 1. Secretaría Virtual
    s = crear_sesion()
    actividades_sv = []
    for centro_id, nombre in CENTROS_SV.items():
        try:
            html = buscar_sv(s, centro_id)
            actividades_sv.extend(parsear_sv(html, nombre))
        except Exception as e:
            print(f"Error SV {nombre}: {e}")

    # 2. CEPS HTML
    actividades_ceps = []
    for nombre, url in CEPS_HTML.items():
        try:
            actividades_ceps.extend(scrape_cep_html(nombre, url))
        except Exception as e:
            print(f"Error CEP HTML {nombre}: {e}")

    # 3. Fusionar
    actividades = fusionar(actividades_sv, actividades_ceps)

    # 4. Guardar JSON
    with open("actividades.json", "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)

    print(f"Scraper HTML híbrido: {len(actividades)} cursos encontrados.")
    print(f"SV: {len(actividades_sv)} · CEP-HTML: {len(actividades_ceps)}")

if __name__ == "__main__":
    main()
