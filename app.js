const ENDPOINT_ACTIVIDADES = "actividades.json";

// Normalización universal de CEPs
function normalizarCEP(cepRaw) {
  if (!cepRaw) return "";
  const t = cepRaw.toUpperCase();
  if (t.includes("SEVILLA")) return "SEVILLA";
  if (t.includes("CASTILLEJA")) return "CASTILLEJA";
  if (t.includes("OSUNA")) return "OSUNA";
  if (t.includes("MAIRENA")) return "MAIRENA";
  if (t.includes("LEBRIJA")) return "LEBRIJA";
  if (t.includes("LORA")) return "LORA DEL RÍO";
  return t.trim();
}

let actividades = [];
const lista = document.getElementById("listaActividades");

async function cargarActividades() {
  try {
    const resp = await fetch(ENDPOINT_ACTIVIDADES);
    const datos = await resp.json();

    actividades = datos
      .map(a => ({
        ...a,
        cep: normalizarCEP(a.cep),
        estado: (a.estado || "").toUpperCase()
      }))
      .filter(a => a.estado.includes("ABIERTO PLAZO SOLICITUDES"));

    pintarLista();
  } catch (e) {
    console.error(e);
    lista.innerHTML = "<p>Error cargando datos.</p>";
  }
}

function pintarLista() {
  lista.innerHTML = "";

  if (actividades.length === 0) {
    lista.innerHTML = "<p>No hay cursos con el plazo abierto.</p>";
    return;
  }

  actividades.forEach(a => {
    const div = document.createElement("div");
    div.className = "item-actividad";
    div.innerHTML = `
      <h3>${a.titulo}</h3>
      <div class="meta">
        <span><b>CEP:</b> ${a.cep}</span><br>
        <span><b>Inicio:</b> ${a.inicio}</span><br>
        <span><b>Fin:</b> ${a.fin}</span><br>
        <span><b>Estado:</b> ${a.estado}</span><br>
        <a href="${a.url}" target="_blank" rel="noopener">Apuntarse al curso</a>
      </div>
    `;
    lista.appendChild(div);
  });
}

cargarActividades();