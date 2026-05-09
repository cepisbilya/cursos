let datos = [];
let pagina = 0;
const TAM_PAGINA = 10;

async function cargarDatos() {
  const res = await fetch("actividades.json");
  datos = await res.json();

  datos.sort((a, b) => new Date(b.inicio) - new Date(a.inicio));

  aplicarFiltros();
  activarScrollInfinito();
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
        <strong>🗓 Inicio actividad:</strong> ${a.inicio || "—"}<br>
        <strong>🗓 Fin actividad:</strong> ${a.fin || "—"}<br>
        <strong>📝 Inicio inscripción:</strong> ${a.inicio_inscripcion || "—"}<br>
        <strong>📝 Fin inscripción:</strong> ${a.fin_inscripcion || "—"}<br>
        <strong>⏱ Horas totales:</strong> ${a.horas || "—"}
      </div>

      <span class="badge ${a.estado.includes("ABIERTO") ? "abierto" : "cerrado"}">
        ${a.estado}
      </span>

      <a class="btn-actividad" href="${a.url}" target="_blank">
        Ver actividad completa →
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
