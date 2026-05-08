// Ruta correcta del JSON (todo está en el raíz)
const ENDPOINT_ACTIVIDADES = "actividades.json";

// Inicializar mapa
const map = L.map("map").setView([37.39, -5.99], 8);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap"
}).addTo(map);

// Variables globales
let actividades = [];
let marcadores = [];
const capaMarcadores = L.layerGroup().addTo(map);

// Elementos del DOM
const buscador = document.getElementById("buscador");
const checkCEPs = Array.from(document.querySelectorAll(".filtro-cep"));
const listaActividades = document.getElementById("listaActividades");
const btnReset = document.getElementById("btnReset");

// Cargar actividades
async function cargarActividades() {
  try {
    const resp = await fetch(ENDPOINT_ACTIVIDADES);
    if (!resp.ok) throw new Error("No se pudo cargar actividades.json");

    const datos = await resp.json();

    // Normalización del CEP para que coincida con los filtros
    actividades = datos.map(a => ({
      ...a,
      cep: (a.cep || "")
        .toUpperCase()
        .replace("CEP DE ", "")
        .replace("CEP ", "")
        .trim()
    }));

    pintarTodo();
  } catch (e) {
    console.error("Error cargando datos:", e);
    listaActividades.innerHTML = "<p>Error cargando datos.</p>";
  }
}

// Pintar lista + marcadores
function pintarTodo() {
  capaMarcadores.clearLayers();
  marcadores = [];
  listaActividades.innerHTML = "";

  const texto = buscador.value.trim().toLowerCase();
  const cepsActivos = checkCEPs
    .filter(c => c.checked)
    .map(c => c.value.toUpperCase());

  const filtradas = actividades.filter(a => {
    if (!cepsActivos.includes(a.cep)) return false;

    if (texto) {
      const blob = (a.titulo + " " + a.codigo).toLowerCase();
      if (!blob.includes(texto)) return false;
    }

    return true;
  });

  filtradas.forEach(a => {
    // Marcador en el mapa
    if (a.lat && a.lon) {
      const marker = L.marker([a.lat, a.lon]).addTo(capaMarcadores);
      marker.bindPopup(`
        <strong>${a.titulo}</strong><br>
        <span>${a.lugar || ""}</span><br>
        <span><b>CEP:</b> ${a.cep}</span><br>
        <span><b>Inicio:</b> ${a.inicio}</span><br>
        <span><b>Fin:</b> ${a.fin}</span><br>
        <span><b>Estado:</b> ${a.estado}</span><br>
        <a href="${a.url}" target="_blank" rel="noopener">Ver ficha</a>
      `);
      marcadores.push({ id: a.codigo, marker });
    }

    // Tarjeta en la lista
    const div = document.createElement("div");
    div.className = "item-actividad";
    div.dataset.id = a.codigo;
    div.innerHTML = `
      <h3>${a.titulo}</h3>
      <div class="meta">
        <span class="cep">${a.cep}</span><br>
        <span>${a.inicio}${a.fin ? " - " + a.fin : ""}</span><br>
        ${a.lugar ? `<span>${a.lugar}</span><br>` : ""}
        ${a.estado ? `<span>${a.estado}</span>` : ""}
      </div>
    `;
    listaActividades.appendChild(div);
  });

  if (filtradas.length === 0) {
    listaActividades.innerHTML = "<p>No hay actividades con los filtros actuales.</p>";
  }
}

// Eventos
buscador.addEventListener("input", pintarTodo);
checkCEPs.forEach(c => c.addEventListener("change", pintarTodo));
btnReset.addEventListener("click", () => {
  buscador.value = "";
  checkCEPs.forEach(c => (c.checked = true));
  pintarTodo();
});

// Iniciar
cargarActividades();