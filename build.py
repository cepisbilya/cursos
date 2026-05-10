"""
Genera docs/index.html desde data/actividades.json
Tarjetas estilo CEP Isbilya (como la imagen enviada)
- 2 tarjetas por fila en escritorio
- 1 tarjeta por fila en móvil
- Iconos alineados
- Badges ABIERTO/CERRADO
- Filtro CEP dinámico
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
    "CEP Sevilla": "CEP Sevilla",
    "CEP Castilleja de la Cuesta": "CEP Castilleja",
    "CEP Osuna - Écija": "CEP Osuna",
    "CEP Mairena del Alcor": "CEP Mairena",
    "CEP Lebrija": "CEP Lebrija",
    "CEP Lora del Río": "CEP Lora del Río",
}


def fecha_sort(fecha_str):
    if not fecha_str:
        return "00000000"
    p = fecha_str.split("/")
    return (p[2] + p[1] + p[0]) if len(p) == 3 else "00000000"


def v(val):
    return val.strip() if val and val.strip() else "—"


def card_html(a):
    url = a.get("URL", "")
    btn = (
        f'<a class="btn-ver" href="{url}" target="_blank" rel="noopener">Ver actividad →</a>'
        if url else ""
    )

    estado = a.get("Estado", "").upper()
    badge = ""
    if "ABIERTO" in estado:
        badge = '<span class="badge abierto">ABIERTO PLAZO SOLICITUDES</span>'
    elif "CERRADO" in estado:
        badge = '<span class="badge cerrado">PLAZO CERRADO</span>'

    insc_ini = v(a.get("Inicio inscripción", ""))
    insc_fin = v(a.get("Fin inscripción", ""))
    insc = f"{insc_ini} → {insc_fin}" if insc_ini != "—" or insc_fin != "—" else "—"

    return f"""
    <div class="card" data-cep="{a.get('CEP','')}">
      <h3>{a.get('Título','')}</h3>

      <div class="meta">
        <div class="row"><span class="icon">📍</span><span class="label">CEP</span><span>{v(a.get('CEP',''))}</span></div>
        <div class="row"><span class="icon">🧾</span><span class="label">Código</span><span>{v(a.get('Código',''))}</span></div>
        <div class="row"><span class="icon">📚</span><span class="label">Modalidad</span><span>{v(a.get('Modalidad',''))}</span></div>
        <div class="row"><span class="icon">📌</span><span class="label">Lugar</span><span>{v(a.get('Lugar',''))}</span></div>
        <div class="row"><span class="icon">📅</span><span class="label">Inicio</span><span>{v(a.get('Inicio',''))}</span></div>
        <div class="row"><span class="icon">📅</span><span class="label">Fin</span><span>{v(a.get('Fin',''))}</span></div>
        <div class="row"><span class="icon">🖋️</span><span class="label">Inscripción</span><span>{insc}</span></div>
        <div class="row"><span class="icon">⏱️</span><span class="label">Horas</span><span>{v(a.get('Horas',''))}</span></div>
      </div>

      {badge}
      {btn}
    </div>
    """


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

    dt = (
        datetime.fromisoformat(generado)
        .replace(tzinfo=timezone.utc)
        .astimezone(ZoneInfo("Europe/Madrid"))
        .strftime("%d/%m/%Y %H:%M")
    )

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
    header img {{ height: 48px; border-radius: 8px; }}
    header .titulo {{ flex: 1; }}

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

    #contenedor {{
      max-width: 1100px;
      margin: 1.5rem auto;
      padding: 0 1.5rem;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1rem;
    }}

    /* === TARJETAS NUEVAS === */

    .card {{
      background: white;
      border-radius: 12px;
      padding: 1.2rem 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 0.9rem;
      border: 1px solid #e5e7eb;
    }}

    .card h3 {{
      font-size: 1rem;
      font-weight: 700;
      color: #1a1a2e;
      margin-bottom: 0.4rem;
    }}

    .meta {{
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
      font-size: 0.85rem;
    }}

    .row {{
      display: grid;
      grid-template-columns: 22px 90px 1fr;
      align-items: center;
      gap: 0.3rem;
    }}

    .icon {{ font-size: 1rem; }}

    .label {{
      font-weight: 600;
      color: #475569;
      text-transform: uppercase;
      font-size: 0.75rem;
    }}

    .badge {{
      padding: 0.35rem 0.6rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      width: fit-content;
    }}

    .badge.abierto {{
      background: #d1fae5;
      color: #065f46;
    }}

    .badge.cerrado {{
      background: #fee2e2;
      color: #991b1b;
    }}

    .btn-ver {{
      align-self: flex-end;
      font-size: 0.85rem;
      font-weight: 600;
      color: white;
      background: #065f46;
      padding: 0.45rem 0.9rem;
      border-radius: 6px;
      text-decoration: none;
      transition: opacity 0.15s;
    }}

    .btn-ver:hover {{ opacity: 0.8; }}

    /* === MÓVIL === */
    @media (max-width: 700px) {{
      #contenedor {{
        grid-template-columns: 1fr;
        padding: 0 1rem;
      }}

      .card {{
        padding: 1rem;
      }}

      .row {{
        grid-template-columns: 20px 80px 1fr;
      }}

      .label {{
        font-size: 0.7rem;
      }}
    }}
  </style>
</head>

<body>

  <header>
    <img src="logo_isbilya.png" alt="Logo IES Isbilya">
    <div class="titulo">
      <h1>IES Isbilya · Actividades CEP</h1>
    </div>
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
