import requests
from bs4 import BeautifulSoup
import json

CEPS = {
    "SEVILLA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-sevilla/convocatorias-abiertas",
    "CASTILLEJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-castilleja/convocatorias-abiertas",
    "OSUNA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-osuna/convocatorias-abiertas",
    "MAIRENA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-mairena/convocatorias-abiertas",
    "LEBRIJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-lebrija/convocatorias-abiertas",
    "LORA DEL RÍO": "https://www.juntadeandalucia.es/educacion/portales/web/cep-loradelrio/convocatorias-abiertas"
}

def scrape_cep(nombre, url):
    print(f"Scraping {nombre}...")

    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    actividades = []

    tarjetas = soup.select(".asset-full-content, .asset-content, .portlet-body .journal-content-article")
    if not tarjetas:
        print(f"⚠ No se encontraron tarjetas en {nombre}")
        return []

    for t in tarjetas:
        titulo_el = t.find("h2") or t.find("h3")
        if not titulo_el:
            continue

        titulo = titulo_el.get_text(strip=True)

        # Buscar enlace
        enlace = titulo_el.find("a")
        url_curso = enlace["href"] if enlace else ""

        # Buscar fechas y estado dentro del texto
        texto = t.get_text(" ", strip=True).upper()

        inicio = ""
        fin = ""
        estado = ""

        # Detectar fechas
        import re
        fechas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
        if len(fechas) >= 1:
            inicio = fechas[0]
        if len(fechas) >= 2:
            fin = fechas[1]

        # Detectar estado
        if "ABIERTO" in texto:
            estado = "ABIERTO"
        elif "CERRADO" in texto:
            estado = "CERRADO"
        else:
            estado = "DESCONOCIDO"

        actividades.append({
            "titulo": titulo,
            "cep": nombre,
            "inicio": inicio,
            "fin": fin,
            "estado": estado,
            "url": url_curso
        })

    return actividades

def main():
    todas = []

    for nombre, url in CEPS.items():
        actividades = scrape_cep(nombre, url)
        todas.extend(actividades)

    with open("actividades.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)

    print(f"Guardado actividades.json con {len(todas)} cursos.")

if __name__ == "__main__":
    main()
