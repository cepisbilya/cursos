"""
Descarga actividades con plazo abierto de los 6 CEPs de Sevilla
y guarda data/actividades.json
"""
import json
import os
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://secretariavirtual.juntadeandalucia.es"
SEARCH_URL = f"{BASE_URL}/secretariavirtual/consultaCEP/buscar/"

CENTROS_SV = {
    "5265": "CEP Sevilla",
    "5266": "CEP Castilleja de la Cuesta",
    "5267": "CEP Osuna - Écija",
    "5268": "CEP Mairena del Alcor",
    "5269": "CEP Lebrija",
    "5270": "CEP Lora del Río",
}

DATA_DIR = "data"


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
        "estado": "6",   # Solo "Abierto plazo solicitudes"
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
        enlace = fila.find("a", href=True)
        url = enlace["href"] if enlace else ""
        if url.startswith("/"):
            url = BASE_URL + url

        actividades.append({
            "Código":     a.get("Código", ""),
            "Título":     a.get("Título", ""),
            "CEP":        cep_nombre,
            "Modalidad":  a.get("Modalidad", ""),
            "Dirigido a": a.get("Dirigido a", ""),
            "Inicio":     a.get("Inicio", ""),
            "Fin":        a.get("Fin", ""),
            "Estado":     "Abierto plazo solicitudes",
            "URL":        url,
        })

    return actividades


def main():
    print("=== Scraper CEP Isbilya — solo plazo abierto ===\n")
    s = crear_sesion()
    todas = {}
    errores = 0

    for centro_id, cep_nombre in CENTROS_SV.items():
        try:
            html = buscar_sv(s, centro_id)
            lista = parsear_sv(html, cep_nombre)
            for act in lista:
                cod = act.get("Código", "")
                if cod:
                    todas[cod] = act
            print(f"  ✅ {cep_nombre}: {len(lista)} actividades")
        except Exception as e:
            print(f"  ❌ {cep_nombre}: {e}")
            errores += 1

    actividades = list(todas.values())
    print(f"\nTotal: {len(actividades)} actividades con plazo abierto")

    if errores == len(CENTROS_SV):
        print("⚠️  Todos los centros fallaron. No se sobreescribe actividades.json.")
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    datos = {
        "generado": datetime.now(timezone.utc).isoformat(),
        "total": len(actividades),
        "actividades": actividades,
    }
    with open(os.path.join(DATA_DIR, "actividades.json"), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

    print(f"Guardado en {DATA_DIR}/actividades.json")


if __name__ == "__main__":
    main()
