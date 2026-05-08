import requests
from bs4 import BeautifulSoup

BASE_URL = "https://secretariavirtual.juntadeandalucia.es/secretariavirtual/consultaCEP"
SEARCH_URL = f"{BASE_URL}/buscar/"

CENTROS = {
    "5265": "CEP Sevilla",
    "5266": "CEP Castilleja de la Cuesta",
    "5267": "CEP Osuna - Écija",
    "5268": "CEP Mairena del Alcor",
    "5269": "CEP Lebrija",
    "5270": "CEP Lora del Río",
}

def crear_sesion():
    s = requests.Session()
    s.get(BASE_URL + "/", timeout=15)
    return s

def buscar_actividades(session, filtros=None):
    payload = {
        "centro": "-1",
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
    if filtros:
        payload.update(filtros)

    if all(payload.get(k) in ("-1", "") for k in ("centro", "estado", "titulo", "codigoEdicion")):
        raise ValueError("Aplica al menos un filtro: centro, estado, titulo o codigoEdicion")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": BASE_URL + "/",
    }

    r = session.post(SEARCH_URL, data=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.text

def parsear_actividades(html):
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
        enlace = fila.find("a", href=True)
        a["URL"] = enlace["href"] if enlace else ""
        actividades.append(a)

    return actividades

def obtener_actividades(filtros=None):
    s = crear_sesion()
    html = buscar_actividades(s, filtros)
    return parsear_actividades(html)
