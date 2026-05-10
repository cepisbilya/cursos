"""
Genera docs/index.html desde data/actividades.json
- Sin borde/sombra izquierda en las tarjetas
- 2 tarjetas por fila
- Campos: CEP, Código, Modalidad, Lugar, Inicio, Fin, Inscripción, Horas
- Filtro CEP solo muestra los que tienen cursos
- Fecha de actualización solo en la barra de controles
"""
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DATA_DIR = "data"
DOCS_DIR = "docs"

CEP_ORDEN = [
    "CEP Sevilla",
    "CEP Castilleja de la Cuesta",
    "CEP Osuna - Écija",
    "CEP Mairena del Alcor",
    "CEP Lebrija",
    "CEP Lora del Río",
]

CEP_LABELS = {
    "CEP Sevilla":               "CEP Sevilla",
    "CEP Castilleja de la Cuesta": "CEP Castilleja",
    "CEP Osuna - Écija":         "CEP Osuna",
    "CEP Mairena del Alcor":     "CEP Mairena",
    "CEP Lebrija":               "CEP Lebrija",
    "CEP Lora del Río":          "CEP Lora del Río",
}


def fecha_sort(fecha_str):
    if not fecha_str:
        return "00000000"
    p = fecha_str.split("/")
    return (p[2] + p[1] + p[0]) if len(p) == 3 else "00000000"


def v(val):
    """Devuelve el valor o '—' si está vacío."""
    return val.strip() if val and val.strip() else "—"


def card_html(a):
    url = a.get("URL", "")
    btn = (f'<a class="btn-actividad" href="{url}" target="_blank" rel="noopener">'
           f'Ver actividad →</a>') if url else ""

    insc_ini = v(a.get("Inicio inscripción", ""))
    insc_fin = v(a.get("Fin inscripción", ""))
    if insc_ini != "—" or insc_fin != "—":
        insc = f"{insc_ini} → {insc_fin}"
    else:
        insc = "—"

    return f"""    <div class="card" data-cep="{a.get('CEP','')}">
      <h3>{a.get('Título','')}</h3>
      <div class="meta">
        <div class="meta-row"><span class="meta-icon">📍</span><span><strong>CEP:</strong> {v(a.get('CEP',''))}</span></div>
        <div class="meta-row"><span class="meta-icon">🔢</span><span><strong>Código:</strong> {v(a.get('Código',''))}</span></div>
        <div class="meta-row"><span class="meta-icon">📚</span><span><strong>Modalidad:</strong> {v(a.get('Modalidad',''))}</span></div>
        <div class="meta-row"><span class="meta-icon">📌</span><span><strong>Lugar:</strong> {v(a.get('Lugar',''))}</span></div>
        <div class="meta-row"><span class="meta-icon">📅</span><span><strong>Inicio:</strong> {v(a.get('Inicio',''))}</span></div>
        <div class="meta-row"><span class="meta-icon">📅</span><span><strong>Fin:</strong> {v(a.get('Fin',''))}</span></div>
        <div class="meta-row"><span class="meta-icon">📝</span><span><strong>Inscripción:</strong> {insc}</span></div>
        <div class="meta-row"><span class="meta-icon">⏱</span><span><strong>Horas:</strong> {v(a.get('Horas',''))}</span></div>
      </div>
      <div class="card-footer">
        <span class="badge-abierto">ABIERTO PLAZO SOLICITUDES</span>
        {btn}
      </div>
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
    actividades_ord = sorted(
        actividades,
        key=lambda a: fecha_sort(a.get("Inicio", "")),
        reverse=True
    )
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
  <link rel="icon" type="image/png" href="logo_isbilya.png">
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
    header .titulo {{ flex: 1; }}
    header h1 {{ font-size: 1.2rem; font-weight: 700; }}
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
      margin-left: auto;
    }}

    #contenedor {{
      max-width: 1100px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
    }}

    /* ── Tarjeta estilo imagen de referencia ── */
    .card {{
      background: white;
      border-radius: 8px;
      padding: 1rem 1.1rem 0.9rem;
      border: 1px solid #d1d5db;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      transition: box-shadow 0.15s;
    }}
    .card:hover {{
      box-shadow: 0 3px 10px rgba(0,0,0,0.10);
    }}
    .card h3 {{
      font-size: 0.95rem;
      font-weight: 700;
      line-height: 1.4;
      color: #1a1a2e;
      padding-bottom: 0.55rem;
      border-bottom: 1px solid #e5e7eb;
    }}
    .meta {{
      display: flex;
      flex-direction: column;
      gap: 0.28rem;
      font-size: 0.82rem;
      color: #374151;
    }}
    .meta-row {{
      display: flex;
      align-items: baseline;
      gap: 0.4rem;
    }}
    .meta-icon {{
      font-size: 0.9rem;
      flex-shrink: 0;
      width: 1.2rem;
      text-align: center;
    }}
    .card-footer {{
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-top: 0.3rem;
      padding-top: 0.6rem;
      border-top: 1px solid #e5e7eb;
      flex-wrap: wrap;
    }}
    .badge-abierto {{
      font-size: 0.7rem;
      font-weight: 700;
      color: #166534;
      background: #dcfce7;
      border: 1px solid #bbf7d0;
      padding: 0.2rem 0.55rem;
      border-radius: 4px;
      letter-spacing: 0.02em;
    }}
    .btn-actividad {{
      font-size: 0.82rem;
      font-weight: 600;
      color: white;
      background: #166534;
      text-decoration: none;
      padding: 0.3rem 0.75rem;
      border-radius: 5px;
      transition: background 0.15s;
    }}
    .btn-actividad:hover {{
      background: #14532d;
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

    @media (max-width: 700px) {{
      #contenedor {{
        grid-template-columns: 1fr;
        padding: 0 1rem;
      }}
      header {{ padding: 0.75rem 1rem; }}
      header img {{ height: 36px; }}
      header h1 {{ font-size: 1rem; }}
      .controles {{ padding: 0.6rem 1rem; }}
      .stats {{ display: none; }}
    }}
  </style>
</head>
<body>

  <header>
    <img src="logo_isbilya.png" alt="Logo IES Isbilya">
    <div class="titulo">
      <h1>IES Isbilya · Actividades CEP</h1>
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
      <strong id="totalCursos">{total}</strong> actividades · Actualizado: <strong>{dt}</strong>
    </span>
  </div>

  <div id="contenedor">
    {cards}
    <p id="sin-resultados">No hay actividades con los filtros seleccionados.</p>
  </div>

  <footer>
    Datos de la Secretaría Virtual de la Junta de Andalucía · Actualización automática cada hora
  </footer>

  <script>
    function aplicarFiltros() {{
      const q   = document.getElementById('buscador').value.toLowerCase();
      const cep = document.getElementById('filtroCEP').value;
      const cards = document.querySelectorAll('.card');
      let visibles = 0;
      cards.forEach(card => {{
        const ok = (cep === 'TODOS' || card.dataset.cep === cep)
                && (!q || card.textContent.toLowerCase().includes(q));
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
