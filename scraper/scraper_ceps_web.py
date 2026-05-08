import requests
from bs4 import BeautifulSoup
import json
import re

CEPS = {
    "SEVILLA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-sevilla/convocatorias-abiertas",
    "CASTILLEJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-castilleja/convocatorias-abiertas",
    "OSUNA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-osuna/convocatorias-abiertas",
    "MAIRENA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-mairena/convocatorias-abiertas",
    "LEBRIJA": "https://www.juntadeandalucia.es/educacion/portales/web/cep-lebrija/convocatorias-abiertas",
    "LORA DEL RÍO": "https://www.juntadeandalucia.es/educacion/portales/web/cep-loradelrio/convocatorias-abiertas"
}

def scrape_cep(nombre, url):
    print(f"Scraping CEP {nombre}…")

    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    actividades = []

    # 1) Buscar enlaces a cursos (muy fiable)
    enlaces = soup.select("a[href*='/actividad/'], a[href*='actividad'], a[href*='formacion']")
    enlaces = list({a["href"]: a for a in enlaces}.values())  # eliminar duplicados

    for a in enlaces:
        titulo = a.get_text(strip=True)
        if len(titulo) < 5:
            continue

        url_curso = a["href"]
        if url_curso.startswith("/"):
            url_curso = "https://www.juntadeandalucia.es" + url_curso

        # 2) Buscar fechas en el texto cercano
        bloque = a.find_parent()
        texto = bloque.get_text(" ", strip=True).upper() if bloque else titulo.upper()

        fechas = re.findall(r"\d{2}/\d{2}/\d{4}", texto)
        inicio = fechas[0] if len(fechas) >= 1 else ""
        fin = fechas[1] if len(fechas) >= 2 else ""

        estado = "ABIERTO" if "ABIERTO" in texto or "PLAZO" in texto else "DESCONOCIDO"

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

def main():
    todas = []

    for nombre, url in CEPS.items():
        todas.extend(scrape_cep(nombre, url))

    with open("actividades_web.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)

    print(f"Scraper Web CEPs: {len(todas)} cursos encontrados.")

if __name__ == "__main__":
    main()
