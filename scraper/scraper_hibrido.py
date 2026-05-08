import requests
import json
import re
from bs4 import BeautifulSoup

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
# 2) SCRAPER AJAX DE LOS CEPS
# ============================================

CEPS_AJAX = {
    "SEVILLA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-sevilla/actividades-formativas?p_p_id=buscador_WAR_buscadorportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscador",
    "CASTILLEJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-castilleja/actividades-formativas?p_p_id=buscador_WAR_buscadorportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscador",
    "OSUNA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-osuna/actividades-formativas?p_p_id=buscador_WAR_buscadorportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscador",
    "MAIRENA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-mairena/actividades-formativas?p_p_id=buscador_WAR_buscadorportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscador",
    "LEBRIJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-lebrija/actividades-formativas?p_p_id=buscador_WAR_buscadorportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscador",
    "LORA DEL RÍO": "https://www.juntadeandalucia.es/educacion/portales/web/cep-loradelrio/actividades-formativas?p_p_id=buscador_WAR_buscadorportlet&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=buscador"
}

def scrape_ajax(nombre, url):
    print(f"Scraping AJAX CEP {nombre}…")

    r = requests.post(url, data={"estado": "Abierto plazo solicitudes"}, timeout=20)
    r.raise_for_status()

    try:
        data = r.json()
    except:
        return []

    actividades = []

    for item in data.get("data", []):
        actividades.append({
            "titulo": item.get("titulo", "").strip(),
            "cep": nombre,
            "inicio": item.get("fechaInicio", ""),
            "fin": item.get("fechaFin", ""),
            "estado": "ABIERTO PLAZO SOLICITUDES",
            "url": item.get("url", ""),
            "fuente": "CEP-AJAX"
        })

    return actividades


# ============================================
# 3) FUSIÓN DE RESULTADOS
# ============================================

def fusionar(sv, ajax):
    fusion = {}

    for a in ajax + sv:
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

    # 2. AJAX CEPs
    actividades_ajax = []
    for nombre, url in CEPS_AJAX.items():
        try:
            actividades_ajax.extend(scrape_ajax(nombre, url))
        except Exception as e:
            print(f"Error AJAX {nombre}: {e}")

    # 3. Fusionar
    actividades = fusionar(actividades_sv, actividades_ajax)

    # 4. Guardar JSON
    with open("actividades.json", "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)

    print(f"Scraper híbrido AJAX: {len(actividades)} cursos encontrados.")
    print(f"SV: {len(actividades_sv)} · AJAX: {len(actividades_ajax)}")

if __name__ == "__main__":
    main()
