import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://secretariavirtual.juntadeandalucia.es"
SEARCH_URL = f"{BASE_URL}/secretariavirtual/consultaCEP/buscar/"

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
    s.get(BASE_URL + "/secretariavirtual/consultaCEP/", timeout=15)
    return s

def buscar_sv(session, centro_id):
    payload = {
        "centro": centro_id,
        "modalidad": "-1",
        "_modalidad": "1",
        "dirigido": "-1",
        "estado": "6",   # Abierto plazo solicitudes
        "fechaI": "",
        "fechaF": "",
        "titulo": "",
        "codigoEdicion": "",
        "descriptor": "-1",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": BASE_URL + "/secretariavirtual/consultaCEP/",
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
            url = BASE_URL + url

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

def extraer_detalle(url):
    """Extrae SOLO los campos necesarios: código, modalidad, lugar,
    fechas actividad, fechas inscripción y horas totales."""
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        detalle = {}

        # Todas las listas de datos están en <ul class="list-group">
        listas = soup.find_all("ul", class_="list-group")

        for ul in listas:
            for li in ul.find_all("li", class_="list-group-item"):
                texto = li.get_text(" ", strip=True)

                if texto.startswith("Código:"):
                    detalle["codigo"] = texto.replace("Código:", "").strip()

                if texto.startswith("Modalidad:"):
                    detalle["modalidad"] = texto.replace("Modalidad:", "").strip()

                if texto.startswith("Lugar de realización:"):
                    detalle["lugar"] = texto.replace("Lugar de realización:", "").strip()

                if texto.startswith("Fecha actividad:"):
                    fechas = texto.replace("Fecha actividad:", "").strip()
                    if "hasta" in fechas:
                        ini, fin = fechas.split("hasta")
                        detalle["inicio"] = ini.strip()
                        detalle["fin"] = fin.strip()

                if texto.startswith("Fecha inscripción:"):
                    fechas = texto.replace("Fecha inscripción:", "").strip()
                    if "hasta" in fechas:
                        ini, fin = fechas.split("hasta")
                        detalle["inicio_inscripcion"] = ini.strip()
                        detalle["fin_inscripcion"] = fin.strip()

                if texto.startswith("Horas totales:"):
                    detalle["horas"] = texto.replace("Horas totales:", "").strip()

        return detalle

    except Exception as e:
        print("Error en detalle:", e)
        return {}

def main():
    s = crear_sesion()
    actividades = []

    for centro_id, nombre in CENTROS_SV.items():
        try:
            html = buscar_sv(s, centro_id)
            lista = parsear_sv(html, nombre)

            # Añadir detalle a cada actividad
            for act in lista:
                detalle = extraer_detalle(act["url"])
                act.update(detalle)

            actividades.extend(lista)

        except Exception as e:
            print(f"Error SV {nombre}: {e}")

    with open("actividades.json", "w", encoding="utf-8") as f:
        json.dump(actividades, f, ensure_ascii=False, indent=2)

    print(f"Scraper SV final: {len(actividades)} cursos abiertos encontrados (con detalle).")

if __name__ == "__main__":
    main()
