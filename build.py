"""
Lee data/actividades.json y genera docs/index.html
con el diseño original de CEP Isbilya:
- Solo filtro por CEP (selector desplegable)
- Solo muestra actividades con plazo abierto
- Buscador de texto
- Cards con scroll infinito
"""
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DATA_DIR = "data"
DOCS_DIR = "docs"

CEP_LABELS = {
    "CEP Sevilla":               "CEP Sevilla",
    "CEP Castilleja de la Cuesta": "CEP Castilleja",
    "CEP Osuna - Écija":         "CEP Osuna",
    "CEP Mairena del Alcor":     "CEP Mairena",
    "CEP Lebrija":               "CEP Lebrija",
    "CEP Lora del Río":          "CEP Lora del Río",
}

CEP_ORDEN = list(CEP_LABELS.keys())


def fecha_sort(fecha_str):
    if not fecha_str:
        return "00000000"
    p = fecha_str.split("/")
    return (p[2] + p[1] + p[0]) if len(p) == 3 else "00000000"


def card_html(a):
    url = a.get("URL", "")
    btn = (f'<a class="btn-actividad" href="{url}" target="_blank" rel="noopener">'
           f'Ver actividad →</a>') if url else ""
    return f"""    <div class="card" data-cep="{a.get('CEP','')}">
      <h3>{a.get('Título','')}</h3>
      <div class="meta">
        <strong>📍 CEP:</strong> {a.get('CEP','')}<br>
        <strong>🔢 Código:</strong> {a.get('Código','') or '—'}<br>
        <strong>📚 Modalidad:</strong> {a.get('Modalidad','') or '—'}<br>
        <strong>👥 Dirigido a:</strong> {a.get('Dirigido a','') or '—'}<br>
        <strong>🗓 Inicio:</strong> {a.get('Inicio','') or '—'}<br>
        <strong>🗓 Fin:</strong> {a.get('Fin','') or '—'}
      </div>
      <span class="badge abierto">ABIERTO PLAZO SOLICITUDES</span>
      {btn}
    </div>"""


def opciones_cep_html(actividades):
    ceps_presentes = sorted(
        {a.get("CEP", "") for a in actividades if a.get("CEP")},
        key=lambda c: CEP_ORDEN.index(c) if c in CEP_ORDEN else 99
    )
    opts = '<option value="TODOS">Todos los CEPs</option>\n'
    for cep in ceps_presentes:
        label = CEP_LABELS.get(cep, cep)
        opts += f'        <option value="{cep}">{label}</option>\n'
    return opts


def generar_html(actividades, generado):
    actividades_ord = sorted(actividades, key=lambda a: fecha_sort(a.get("Inicio", "")), reverse=True)
    cards = "\n".join(card_html(a) for a in actividades_ord)
    opciones_cep = opciones_cep_html(actividades)
    total = len(actividades)

    dt = (datetime.fromisoformat(generado)
          .replace(tzinfo=timezone.utc)
          .astimezone(ZoneInfo("Europe/Madrid"))
          .strftime("%d/%m/%Y %H:%M"))

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Cursos CEP – IES Isbilya</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      background: #f0f4f8;
      color: #1a1a2e;
    }}

    header {{
      background: #1a1a2e;
      color: white;
      padding: 1rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }}
    header img {{
      height: 48px;
      border-radius: 8px;
    }}
    header .titulo {{
      flex: 1;
    }}
    header h1 {{
      font-size: 1.2rem;
      font-weight: 700;
    }}
    header p {{
      font-size: 0.78rem;
      opacity: 0.7;
      margin-top: 0.2rem;
    }}
    header a {{
      color: #7dd3fc;
      font-size: 0.82rem;
      text-decoration: none;
      border: 1px solid rgba(125,211,252,0.4);
      padding: 0.3rem 0.7rem;
      border-radius: 20px;
      transition: background 0.15s;
    }}
    header a:hover {{ background: rgba(125,211,252,0.15); }}

    .controles {{
      background: white;
      padding: 0.8rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
      border-bottom: 1px solid #e2e8f0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    .controles input[type="search"] {{
      flex: 1;
      min-width: 160px;
      padding: 0.45rem 0.75rem;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.9rem;
      outline-color: #1a1a2e;
    }}
    .controles select {{
      padding: 0.45rem 0.75rem;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.9rem;
      background: white;
      cursor: pointer;
      outline-color: #1a1a2e;
    }}
    .stats {{
      font-size: 0.78rem;
      color: #64748b;
      white-space: nowrap;
    }}

    #contenedor {{
      max-width: 1100px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1rem;
    }}

    .card {{
      background: white;
      border-radius: 10px;
      padding: 1.1rem;
      border-left: 4px solid #1a1a2e;
      box-shadow: 0 1px 4px rgba(0,0,0,0.07);
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      transition: transform 0.15s, box-shadow 0.15s;
    }}
    .card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0,0,0,0.12);
      border-left-color: #e76f51;
    }}
    .card h3 {{
      font-size: 0.92rem;
      line-height: 1.45;
      color: #1a1a2e;
    }}
    .meta {{
      font-size: 0.78rem;
      color: #64748b;
      line-height: 1.7;
    }}
    .badge {{
      display: inline-block;
      font-size: 0.68rem;
      font-weight: 700;
      padding: 0.2rem 0.6rem;
      border-radius: 20px;
      letter-spacing: 0.03em;
      align-self: flex-start;
    }}
    .badge.abierto {{
      background: #dcfce7;
      color: #166534;
    }}
    .btn-actividad {{
      align-self: flex-end;
      margin-top: auto;
      font-size: 0.82rem;
      font-weight: 600;
      color: #1a1a2e;
      text-decoration: none;
      padding: 0.35rem 0.8rem;
      border: 1.5px solid #1a1a2e;
      border-radius: 6px;
      transition: background 0.15s, color 0.15s;
    }}
    .btn-actividad:hover {{
      background: #1a1a2e;
      color: white;
    }}

    #sin-resultados {{
      display: none;
      grid-column: 1 / -1;
      text-align: center;
      padding: 3rem;
      color: #94a3b8;
      font-size: 0.95rem;
    }}

    footer {{
      text-align: center;
      padding: 2rem;
      font-size: 0.75rem;
      color: #94a3b8;
    }}

    @media (max-width: 600px) {{
      header {{ padding: 0.75rem 1rem; }}
      header img {{ height: 36px; }}
      header h1 {{ font-size: 1rem; }}
      .controles {{ padding: 0.6rem 1rem; }}
      #contenedor {{ padding: 0 1rem; margin-top: 1rem; }}
    }}
  </style>
</head>
<body>

  <header>
    <img src="logo_isbilya.png" alt="Logo IES Isbilya">
    <div class="titulo">
      <h1>IES Isbilya · Actividades CEP</h1>
      <p>Plazo abierto de solicitudes · Actualizado: {dt}</p>
    </div>
    <a href="https://educacionadistancia.juntadeandalucia.es/profesorado/" target="_blank" rel="noopener">
      Aula Virtual
    </a>
  </header>

  <div class="controles">
    <input type="search" id="buscador" placeholder="Buscar actividad..." oninput="aplicarFiltros()">
    <select id="filtroCEP" onchange="aplicarFiltros()">
      {opciones_cep}
    </select>
    <span class="stats">
      Total: <strong id="totalCursos">{total}</strong> &nbsp;·&nbsp;
      Actualizado: <strong>{dt}</strong>
    </span>
  </div>

  <div id="contenedor">
    {cards}
    <p id="sin-resultados">No hay actividades con los filtros seleccionados.</p>
  </div>

  <footer>
    Datos obtenidos de la Secretaría Virtual de la Junta de Andalucía · Actualización automática cada hora
  </footer>

  <script>
    function aplicarFiltros() {{
      const q   = document.getElementById('buscador').value.toLowerCase();
      const cep = document.getElementById('filtroCEP').value;
      const cards = document.querySelectorAll('.card');
      let visibles = 0;
      cards.forEach(card => {{
        const titulo = card.querySelector('h3').textContent.toLowerCase();
        const cardCep = card.dataset.cep;
        const ok = (cep === 'TODOS' || cardCep === cep) && (!q || titulo.includes(q) || card.textContent.toLowerCase().includes(q));
        card.style.display = ok ? '' : 'none';
        if (ok) visibles++;
      }});
      document.getElementById('totalCursos').textContent = visibles;
      document.getElementById('sin-resultados').style.display = visibles === 0 ? 'block' : 'none';
    }}
  </script>

</body>
</html>"""


def main():
    print("=== Generando sitio estático CEP Isbilya ===\n")

    ruta = os.path.join(DATA_DIR, "actividades.json")
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)

    actividades = datos["actividades"]
    generado    = datos["generado"]

    os.makedirs(DOCS_DIR, exist_ok=True)

    html = generar_html(actividades, generado)
    out = os.path.join(DOCS_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ {out} generado con {len(actividades)} actividades")


if __name__ == "__main__":
    main()
