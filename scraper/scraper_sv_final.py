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
    """Scrapea la ficha individual de la actividad con todos los campos posibles."""
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        detalle = {}

        # 1. Código y edición (aparecen en el encabezado)
        encabezado = soup.find("h3")
        if encabezado:
            texto = encabezado.get_text(" ", strip=True)
            if "Código" in texto:
                partes = texto.split(" - ")
                if len(partes) >= 2:
                    detalle["codigo"] = partes[0].replace("Código", "").strip()
                    detalle["edicion"] = partes[1].strip()

        # 2. Campos generales (Modalidad, Dirigido a, Lugar, Horas, etc.)
        bloques = soup.find_all("div", class_="col-md-12")
        for b in bloques:
            texto = b.get_text(" ", strip=True)

            if "Modalidad" in texto:
                detalle["modalidad"] = texto.replace("Modalidad", "").strip()

            if "Dirigido a" in texto:
                detalle["dirigido"] = texto.replace("Dirigido a", "").strip()

            if "Lugar" in texto:
                detalle["lugar"] = texto.replace("Lugar", "").strip()

            if "Horas" in texto:
                detalle["horas"] = texto.replace("Horas", "").strip()

            if "Plazas" in texto:
                detalle["plazas"] = texto.replace("Plazas", "").strip()

            if "Criterios de selección" in texto:
                detalle["criterios"] = texto.replace("Criterios de selección", "").strip()

            if "Observaciones" in texto:
                detalle["observaciones"] = texto.replace("Observaciones", "").strip()

        # 3. Descripción larga
        desc = soup.find("div", class_="descripcion")
        if desc:
            detalle["descripcion"] = desc.get_text(" ", strip=True)

        # 4. Ponentes
        ponentes = soup.find("div", id="ponentes")
        if ponentes:
            detalle["ponentes"] = ponentes.get_text(" ", strip=True)

        # 5. Sesiones (tabla)
        sesiones = []
        tabla_sesiones = soup.find("table", id="tablaSesiones")
        if tabla_sesiones:
            for fila in tabla_sesiones.find("tbody").find_all("tr"):
                celdas = [td.get_text(" ", strip=True) for td in fila.find_all("td")]
                if len(celdas) >= 3:
                    sesiones.append({
                        "fecha": celdas[0],
                        "hora_inicio": celdas[1],
                        "hora_fin": celdas[2]
                    })
        if sesiones:
            detalle["sesiones"] = sesiones

        # 6. Documentos adjuntos
        docs = []
        adjuntos = soup.find("div", id="documentos")
        if adjuntos:
            for a in adjuntos.find_all("a", href=True):
                docs.append({
                    "nombre": a.get_text(strip=True),
                    "url": BASE_URL + a["href"] if a["href"].startswith("/") else a["href"]
                })
        if docs:
            detalle["documentos"] = docs

        return detalle

    except Exception:
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
