import requests
from bs4 import BeautifulSoup
import json

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
        "estado": "1",   # SOLO “Abierto plazo solicitudes”
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

        # Por seguridad, filtramos otra vez por “ABIERTO”
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

def main():
    s = crear_sesion()
    actividades = []

    for centro_id, nombre in CENTROS_SV.items():
        try:
            html = buscar_sv(s, centro_id)
            actividades.extend(parsear_sv(html, nombre))
        except Exception as e:
            print(f"Error SV {nombre}: {e}")

    with open("actividades.json", "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)

    print(f"Scraper SV final: {len(actividades)} cursos abiertos encontrados.")

if __name__ == "__main__":
    main()
