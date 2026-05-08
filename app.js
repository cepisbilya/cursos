async function cargarDatos() {
  const res = await fetch("actividades.json");
  const datos = await res.json();

  // Ordenar por fecha de inicio descendente
  datos.sort((a, b) => new Date(b.inicio) - new Date(a.inicio));

  // Estado inicial
  let filtrados = [...datos];

  renderizar(filtrados);
  actualizarContadores(filtrados);

  const buscador = document.getElementById("buscador");
  const filtroCEP = document.getElementById("filtroCEP");

  function aplicarFiltros() {
    const q = buscador.value.toLowerCase();
    const cep = filtroCEP.value;

    filtrados = datos.filter(x => {
      const coincideTexto =
        x.titulo.toLowerCase().includes(q) ||
        x.cep.toLowerCase().includes(q);

      const coincideCEP =
        cep === "TODOS" || x.cep === cep;

      return coincideTexto && coincideCEP;
    });

    renderizar(filtrados);
    actualizarContadores(filtrados);
  }

  // Buscador
  buscador.addEventListener("input", aplicarFiltros);

  // Filtro por CEP
  filtroCEP.addEventListener("change", aplicarFiltros);
}


function renderizar(lista) {
  const cont = document.getElementById("contenedor");
  cont.innerHTML = "";

  lista.forEach(a => {
    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
      <h3>${a.titulo}</h3>
      <div class="meta">
        <strong>CEP:</strong> ${a.cep}<br>
        <strong>Inicio:</strong> ${a.inicio}<br>
        <strong>Fin:</strong> ${a.fin}
      </div>
      <span class="badge ${a.estado.includes("ABIERTO") ? "abierto" : "cerrado"}">
        ${a.estado}
      </span>
      <br><br>
      <a href="${a.url}" target="_blank">Ver actividad →</a>
    `;

    cont.appendChild(card);
  });
}

function actualizarContadores(lista) {
  document.getElementById("totalCursos").textContent = lista.length;
}

cargarDatos();
