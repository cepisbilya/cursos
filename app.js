// =====================================
//  CONFIGURACIÓN
// =====================================
const PAGE_SIZE = 10; // cursos por bloque para scroll infinito

let actividadesOriginal = [];
let actividadesFiltradas = [];
let actividadesAgrupadas = {};
let paginaActual = 0;

const contenedor = document.getElementById("contenedor");
const filtroCEP = document.getElementById("filtroCEP");
const buscador = document.getElementById("buscador");

// =====================================
//  CARGAR JSON
// =====================================
fetch("actividades.json")
  .then(r => r.json())
  .then(datos => {
    actividadesOriginal = datos.map(a => ({
      ...a,
      estado: (a.estado || "").toUpperCase(),
      cep: (a.cep || "").toUpperCase(),
      inicio: a.inicio || "",
      fin: a.fin || "",
      fuente: a.fuente || "WEB"
    }));

    aplicarFiltros();
    inicializarScroll();
  });

// =====================================
//  APLICAR FILTROS (CEP + BUSCADOR)
// =====================================
function aplicarFiltros() {
  const texto = buscador.value.toUpperCase();
  const cepSeleccionado = filtroCEP.value.toUpperCase();

  actividadesFiltradas = actividadesOriginal
    .filter(a => {
      const estado = a.estado;
      const abierto =
        estado.includes("ABIERTO") ||
        estado.includes("PLAZO") ||
        estado.includes("SOLICITUD");

      const coincideCEP =
        cepSeleccionado === "TODOS" || a.cep === cepSeleccionado;

      const coincideTexto =
        a.titulo.toUpperCase().includes(texto);

      return abierto && coincideCEP && coincideTexto;
    })
    .sort((a, b) => {
      const fa = a.inicio.split("/").reverse().join("-");
      const fb = b.inicio.split("/").reverse().join("-");
      return fa < fb ? 1 : -1;
    });

  agruparPorCEP();
  paginaActual = 0;
  contenedor.innerHTML = "";
  cargarMas();
}

// =====================================
//  AGRUPAR POR CEP
// =====================================
function agruparPorCEP() {
  actividadesAgrupadas = {};

  actividadesFiltradas.forEach(a => {
    if (!actividadesAgrupadas[a.cep]) {
      actividadesAgrupadas[a.cep] = [];
    }
    actividadesAgrupadas[a.cep].push(a);
  });
}

// =====================================
//  RENDERIZAR BLOQUES (SCROLL INFINITO)
// =====================================
function cargarMas() {
  const ceps = Object.keys(actividadesAgrupadas);

  let cursosMostrados = 0;
  let cursosNecesarios = PAGE_SIZE;

  for (const cep of ceps) {
    const lista = actividadesAgrupadas[cep];

    // Crear encabezado del CEP si no existe
    if (!document.getElementById("titulo-" + cep)) {
      const h2 = document.createElement("h2");
      h2.id = "titulo-" + cep;
      h2.textContent = "CEP " + cep;
      contenedor.appendChild(h2);
    }

    // Renderizar cursos de este CEP
    for (let i = 0; i < lista.length; i++) {
      const indexGlobal = cursosMostrados;

      if (indexGlobal >= paginaActual * PAGE_SIZE &&
          indexGlobal < (paginaActual + 1) * PAGE_SIZE) {
        renderCard(lista[i]);
      }

      cursosMostrados++;
      if (cursosMostrados >= (paginaActual + 1) * PAGE_SIZE) break;
    }
  }

  paginaActual++;
}

// =====================================
//  RENDERIZAR UNA TARJETA
// =====================================
function renderCard(a) {
  const card = document.createElement("div");
  card.className = "card";

  card.innerHTML = `
    <h3>${a.titulo}</h3>

    <p><strong>CEP:</strong> ${a.cep}</p>
    <p><strong>Inicio:</strong> ${a.inicio || "—"}</p>
    <p><strong>Fin:</strong> ${a.fin || "—"}</p>

    <p class="estado ${a.estado.includes("ABIERTO") ? "abierto" : "otro"}">
      <strong>Estado:</strong> ${a.estado}
    </p>

    <a class="btn" href="${a.url}" target="_blank" rel="noopener">
      Apuntarse al curso
    </a>

    <p class="fuente">Fuente: ${a.fuente}</p>
  `;

  contenedor.appendChild(card);
}

// =====================================
//  SCROLL INFINITO
// =====================================
function inicializarScroll() {
  window.addEventListener("scroll", () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 300) {
      cargarMas();
    }
  });
}

// =====================================
//  EVENTOS
// =====================================
filtroCEP.addEventListener("change", aplicarFiltros);
buscador.addEventListener("input", aplicarFiltros);
