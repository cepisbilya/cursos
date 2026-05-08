import requests
from bs4 import BeautifulSoup
import json
import re

# -----------------------------
# 1. SECRETARÍA VIRTUAL (SV)
# -----------------------------

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
        estado = a.get("Estado", "").upper()

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


# -----------------------------
# 2. WEBS DE LOS CEPS
# -----------------------------

CEPS_WEB = {
    "SEVILLA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-sevilla/convocatorias-abiertas",
    "CASTILLEJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-castilleja/convocatorias-abiertas",
    "OSUNA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-osuna/convocatorias-abiertas",
    "MAIRENA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-mairena/convocatorias-abiertas",
    "LEBRIJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-lebrija/convocatorias-abiertas",
    "LORA DEL RÍO": "https://www.juntadeandalucia.es/educacion/portales/web/cep-loradelrio/convocatorias-abiertas"
}

def scrape_web(nombre, url):
    print(f"Scraping web CEP {nombre}...")

    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    actividades = []

    tarjetas = soup.select(".asset-full-content, .asset-content, .portlet-body .journal-content-article")
    if not tarjetas:
        return []

    for t in tarjetas:
        titulo_el = t.find("h2") or t.find("h3")
        if not titulo_el:
            continue

        titulo = titulo_el.get_text(strip=True)
        enlace = titulo_el.find("a")
        url_curso = enlace["href"] if enlace else ""

        texto = t.get_text(" ", strip=True).upper()

        fechas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
        inicio = fechas[0] if len(fechas) >= 1 else ""
        fin = fechas[1] if len(fechas) >= 2 else ""

        estado = "ABIERTO" if "ABIERTO" in texto else "DESCONOCIDO"

        actividades.append({
            "titulo": titulo,
            "cep": nombre,
            "inicio": inicio,
            "fin": fin,
            "estado": estado,
            "url": url_curso,
            "fuente": "WEB"
        })

    return actividades


# -----------------------------
# 3. FUSIÓN DE RESULTADOS
# -----------------------------

def fusionar(sv, web):
    fusion = {}

    for a in web + sv:
        clave = (a["titulo"].upper(), a["cep"])
        if clave not in fusion:
            fusion[clave] = a
        else:
            # Si existe en SV, priorizar SV
            if a["fuente"] == "SV":
                fusion[clave] = a

    return list(fusion.values())


# -----------------------------
# 4. MAIN
# -----------------------------

def main():
    # 1. Secretaría Virtual
    s = crear_sesion()
    actividades_sv = []
    for centro_id, nombre in CENTROS_SV.items():
        html = buscar_sv(s, centro_id)
        actividades_sv.extend(parsear_sv(html, nombre))

    # 2. Webs de los CEPs
    actividades_web = []
    for nombre, url in CEPS_WEB.items():
        actividades_web.extend(scrape_web(nombre, url))

    # 3. Fusionar
    actividades = fusionar(actividades_sv, actividades_web)

    # 4. Guardar JSON
    with open("actividades.json", "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)

    print(f"Guardado actividades.json con {len(actividades)} cursos híbridos.")

if __name__ == "__main__":
    main()
