async function cargarDatos() {
  const res = await fetch("actividades.json");
  const datos = await res.json();

  // Ordenar por fecha de inicio descendente
  datos.sort((a, b) => new Date(b.inicio) - new Date(a.inicio));

  renderizar(datos);
  actualizarContadores(datos);

  // Buscador
  document.getElementById("buscador").addEventListener("input", e => {
    const q = e.target.value.toLowerCase();
    const filtrados = datos.filter(x =>
      x.titulo.toLowerCase().includes(q) ||
      x.cep.toLowerCase().includes(q)
    );
    renderizar(filtrados);
    actualizarContadores(filtrados);
  });
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
  document.getElementById("cursosAbiertos").textContent =
    lista.filter(x => x.estado.includes("ABIERTO")).length;
  document.getElementById("cursosCerrados").textContent =
    lista.filter(x => !x.estado.includes("ABIERTO")).length;
}

cargarDatos();
