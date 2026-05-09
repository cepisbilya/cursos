let datos = [];
let pagina = 0;
const TAM_PAGINA = 15;

async function cargarDatos() {
  cargarFechaActualizacion();

  const res = await fetch("actividades.json");
  datos = await res.json();

  datos.sort((a, b) => new Date(b.inicio) - new Date(a.inicio));

  // Después (funciona con DD/MM/YYYY):
function parseFecha(str) {
  if (!str) return 0;
  const [d, m, y] = str.split("/");
  return new Date(`${y}-${m}-${d}`).getTime() || 0;
}
datos.sort((a, b) => parseFecha(b.inicio) - parseFecha(a.inicio));

  aplicarFiltros();
  activarScrollInfinito();
}

async function cargarFechaActualizacion() {
  try {
    const res = await fetch("ultima_actualizacion.txt");
    const texto = await res.text();
    document.getElementById("ultimaActualizacion").textContent = texto.trim();
  } catch {
    document.getElementById("ultimaActualizacion").textContent = "—";
  }
}

function aplicarFiltros() {
  const q = document.getElementById("buscador").value.toLowerCase();
  const cep = document.getElementById("filtroCEP").value;

  let filtrados = datos.filter(x =>
    (x.titulo.toLowerCase().includes(q) || x.cep.toLowerCase().includes(q)) &&
    (cep === "TODOS" || x.cep === cep)
  );

  window.listaFiltrada = filtrados;
  pagina = 0;

  document.getElementById("contenedor").innerHTML = "";
  cargarPagina();

  document.getElementById("totalCursos").textContent = filtrados.length;
}

function cargarPagina() {
  const inicio = pagina * TAM_PAGINA;
  const fin = inicio + TAM_PAGINA;
  const trozo = window.listaFiltrada.slice(inicio, fin);

  trozo.forEach(a => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <h3>${a.titulo}</h3>

      <div class="meta">
        <strong>📍 CEP:</strong> ${a.cep}<br>
        <strong>🔢 Código:</strong> ${a.codigo || "—"}<br>
        <strong>📚 Modalidad:</strong> ${a.modalidad || "—"}<br>
        <strong>📌 Lugar:</strong> ${a.lugar || "—"}<br>
        <strong>🗓 Inicio:</strong> ${a.inicio || "—"}<br>
        <strong>🗓 Fin:</strong> ${a.fin || "—"}<br>
        <strong>📝 Inscripción:</strong> ${a.inicio_inscripcion || "—"} → ${a.fin_inscripcion || "—"}<br>
        <strong>⏱ Horas:</strong> ${a.horas || "—"}
      </div>

      <span class="badge ${a.estado.includes("ABIERTO") ? "abierto" : "cerrado"}">
        ${a.estado}
      </span>

      <a class="btn-actividad" href="${a.url}" target="_blank">
        Ver actividad →
      </a>
    `;

    document.getElementById("contenedor").appendChild(card);
  });

  pagina++;
}

function activarScrollInfinito() {
  window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
      cargarPagina();
    }
  });
}

document.getElementById("buscador").addEventListener("input", aplicarFiltros);
document.getElementById("filtroCEP").addEventListener("change", aplicarFiltros);

cargarDatos();
