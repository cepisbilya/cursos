import json
from scraper_cep import obtener_actividades, CENTROS

CEPS_OBJETIVO = ["5265", "5266", "5267", "5268", "5269", "5270"]

def normalizar(a):
    return {
        "codigo": a.get("Código", ""),
        "titulo": a.get("Título", ""),
        "cep": a.get("CEP", ""),
        "modalidad": a.get("Modalidad", ""),
        "inicio": a.get("Inicio", ""),
        "fin": a.get("Fin", ""),
        "estado": a.get("Estado", ""),
        "url": a.get("URL", ""),
        "lugar": a.get("Lugar", ""),
        "lat": None,
        "lon": None,
    }

def generar_json(ruta_salida="actividades.json"):
    todas = []
    for cep_id in CEPS_OBJETIVO:
        print(f"Scrapeando {CENTROS[cep_id]}...")
        actividades = obtener_actividades({"centro": cep_id})
        for a in actividades:
            todas.append(normalizar(a))

    with open(ruta_salida, "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)

    print(f"✔ Generado {ruta_salida} con {len(todas)} actividades.")

if __name__ == "__main__":
    generar_json()
