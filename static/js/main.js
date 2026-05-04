/**
 * main.js — Restaurante de Don José
 * Frontend logic — fetch API communication with Flask backend
 */

// ── State ──────────────────────────────────────────────────
let reservaEditandoId = null;

// ── SVG Icon helpers ───────────────────────────────────────
const icons = {
  check: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 8 6.5 11.5 13 4"/></svg>`,
  x:     `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><line x1="3" y1="3" x2="13" y2="13"/><line x1="13" y1="3" x2="3" y2="13"/></svg>`,
  info:  `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><line x1="8" y1="7.5" x2="8" y2="11"/></svg>`,
  edit:  `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><path d="M11.7 2.3a1 1 0 0 1 2 2L4 13l-3.5 1 1-3.5L11.7 2.3z"/></svg>`,
  trash: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="2 4 14 4"/><path d="M5 4V2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 .5.5V4"/><rect x="3" y="4" width="10" height="10" rx="1.5"/><line x1="6.5" y1="7" x2="6.5" y2="11"/><line x1="9.5" y1="7" x2="9.5" y2="11"/></svg>`,
  user:  `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="5.5" r="3"/><path d="M2 14c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/></svg>`,
  nodata:`<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><line x1="5.5" y1="5.5" x2="10.5" y2="10.5"/><line x1="10.5" y1="5.5" x2="5.5" y2="10.5"/></svg>`,
  clock: `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="6.5"/><path d="M8 5v3l2 2"/></svg>`,
};

// ── Init ───────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  setFechaHoy();
  actualizarStats();
  cargarReservas();

  // Navigation
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => navegarA(btn.dataset.section));
  });

  // Form submit
  document.getElementById("form-reserva").addEventListener("submit", (e) => {
    e.preventDefault();
    crearReserva();
  });

  // Live search
  document.getElementById("buscador").addEventListener("input", (e) => {
    cargarReservas(e.target.value.trim());
  });

  // Edit modal form
  document.getElementById("form-editar").addEventListener("submit", (e) => {
    e.preventDefault();
    guardarEdicion();
  });

  // Modal close buttons
  document.getElementById("btn-cancelar-modal").addEventListener("click", cerrarModal);
  const btn2 = document.getElementById("btn-cancelar-modal-2");
  if (btn2) btn2.addEventListener("click", cerrarModal);
  document.getElementById("modal-overlay").addEventListener("click", (e) => {
    if (e.target === document.getElementById("modal-overlay")) cerrarModal();
  });

  // Date in topbar
  document.getElementById("fecha-hoy").textContent = formatearFechaHumana(new Date());
});

// ── Navigation ─────────────────────────────────────────────
function navegarA(seccion) {
  document.querySelectorAll(".section").forEach((s) => s.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach((b) => b.classList.remove("active"));
  document.getElementById(`sec-${seccion}`).classList.add("active");
  document.querySelector(`[data-section="${seccion}"]`).classList.add("active");
  if (seccion === "mesas")           cargarMesas();
  if (seccion === "disponibilidad")  cargarDisponibilidad();
}

// ── Date helpers ───────────────────────────────────────────
function setFechaHoy() {
  document.getElementById("fecha").value = new Date().toISOString().split("T")[0];
}

function formatearFechaHumana(d) {
  return d.toLocaleDateString("es-CO", { day: "numeric", month: "long", year: "numeric" });
}

// ── Toast ──────────────────────────────────────────────────
function mostrarToast(msg, tipo = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${tipo}`;
  const iconMap = { success: icons.check, error: icons.x, info: icons.info };
  toast.innerHTML = (iconMap[tipo] || "") + `<span>${msg}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "toastIn 0.22s reverse forwards";
    setTimeout(() => toast.remove(), 220);
  }, 3500);
}

// ── Stats ──────────────────────────────────────────────────
async function actualizarStats() {
  try {
    const res  = await fetch("/mesas/stats");
    const data = await res.json();
    document.getElementById("stat-reservas").textContent   = data.reservas_hoy;
    document.getElementById("stat-total").textContent      = data.total_mesas;
    document.getElementById("stat-libres").textContent     = data.mesas_libres;
    document.getElementById("stat-comensales").textContent = data.comensales_hoy;
  } catch { /* silencioso */ }
}

// ── Reservas ───────────────────────────────────────────────
async function cargarReservas(query = "") {
  const url = query ? `/reservas/?q=${encodeURIComponent(query)}` : "/reservas/";
  try {
    const res     = await fetch(url);
    const reservas = await res.json();
    renderizarTabla(reservas);
  } catch {
    mostrarToast("Error al cargar reservas.", "error");
  }
}

function renderizarTabla(reservas) {
  const tbody = document.getElementById("tabla-reservas");
  if (!reservas.length) {
    tbody.innerHTML = `<tr><td colspan="7">
      <div class="empty-state">
        <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="24" cy="24" r="20"/>
          <path d="M16 18v4a6 6 0 0 0 6 6h4a6 6 0 0 0 6-6v-4"/>
          <line x1="24" y1="28" x2="24" y2="36"/><line x1="19" y1="34" x2="29" y2="34"/>
        </svg>
        <p>No hay reservas registradas.</p>
      </div>
    </td></tr>`;
    return;
  }

  tbody.innerHTML = reservas.map((r) => `
    <tr>
      <td class="td-id">#${String(r.id).padStart(3, "0")}</td>
      <td class="td-name">${escHtml(r.nombre_cliente)}</td>
      <td class="td-num">${r.cantidad_personas}</td>
      <td class="td-num">${r.fecha}</td>
      <td class="td-num">${r.hora}</td>
      <td><span class="badge-mesa">Mesa ${r.mesa_asignada}</span></td>
      <td>
        <div class="acciones">
          <button class="btn btn-icon btn-edit" onclick="abrirModalEditar(${r.id})" title="Editar reserva">${icons.edit}</button>
          <button class="btn btn-icon btn-delete" onclick="eliminarReserva(${r.id}, '${escHtml(r.nombre_cliente)}')" title="Cancelar reserva">${icons.trash}</button>
        </div>
      </td>
    </tr>
  `).join("");
}

async function crearReserva() {
  const nombre   = document.getElementById("nombre").value.trim();
  const personas = parseInt(document.getElementById("personas").value);
  const fecha    = document.getElementById("fecha").value;
  const hora     = document.getElementById("hora").value;

  try {
    const res  = await fetch("/reservas/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre_cliente: nombre, cantidad_personas: personas, fecha, hora }),
    });
    const data = await res.json();
    if (!res.ok) { mostrarToast(data.error || "Error al crear la reserva.", "error"); return; }
    mostrarToast(`Reserva para ${nombre} confirmada — Mesa ${data.mesa_asignada}`, "success");
    document.getElementById("form-reserva").reset();
    setFechaHoy();
    cargarReservas();
    actualizarStats();
  } catch {
    mostrarToast("Error de conexion con el servidor.", "error");
  }
}

async function eliminarReserva(id, nombre) {
  if (!confirm(`Cancelar la reserva de ${nombre}?`)) return;
  try {
    const res  = await fetch(`/reservas/${id}`, { method: "DELETE" });
    const data = await res.json();
    if (!res.ok) { mostrarToast(data.error || "Error al cancelar.", "error"); return; }
    mostrarToast(`Reserva de ${nombre} cancelada.`, "info");
    cargarReservas(document.getElementById("buscador").value.trim());
    actualizarStats();
    if (document.getElementById("sec-mesas").classList.contains("active")) cargarMesas();
  } catch {
    mostrarToast("Error de conexion.", "error");
  }
}

// ── Modal editar ───────────────────────────────────────────
async function abrirModalEditar(id) {
  try {
    const res = await fetch(`/reservas/${id}`);
    const r   = await res.json();
    if (!res.ok) { mostrarToast("Reserva no encontrada.", "error"); return; }
    reservaEditandoId = id;
    document.getElementById("edit-nombre").value   = r.nombre_cliente;
    document.getElementById("edit-personas").value = r.cantidad_personas;
    document.getElementById("edit-fecha").value    = r.fecha;
    document.getElementById("edit-hora").value     = r.hora;
    document.getElementById("modal-overlay").classList.add("open");
  } catch {
    mostrarToast("Error al cargar la reserva.", "error");
  }
}

function cerrarModal() {
  document.getElementById("modal-overlay").classList.remove("open");
  reservaEditandoId = null;
}

async function guardarEdicion() {
  if (!reservaEditandoId) return;
  const nombre   = document.getElementById("edit-nombre").value.trim();
  const personas = parseInt(document.getElementById("edit-personas").value);
  const fecha    = document.getElementById("edit-fecha").value;
  const hora     = document.getElementById("edit-hora").value;

  try {
    const res  = await fetch(`/reservas/${reservaEditandoId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre_cliente: nombre, cantidad_personas: personas, fecha, hora }),
    });
    const data = await res.json();
    if (!res.ok) { mostrarToast(data.error || "Error al guardar.", "error"); return; }
    mostrarToast(`Reserva #${reservaEditandoId} actualizada — Mesa ${data.mesa_asignada}`, "success");
    cerrarModal();
    cargarReservas(document.getElementById("buscador").value.trim());
    actualizarStats();
  } catch {
    mostrarToast("Error de conexion.", "error");
  }
}

// ── Mesas ──────────────────────────────────────────────────
async function cargarMesas() {
  try {
    const res   = await fetch("/mesas/");
    const mesas = await res.json();
    const grid  = document.getElementById("mesas-grid");

    grid.innerHTML = mesas.map((m) => `
      <div class="mesa-card ${m.disponible ? "libre" : "ocupada"}">
        <div class="mesa-num">Mesa ${m.id}</div>
        <div class="mesa-cap">
          <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 10c0-2.2 1.8-3.5 4-3.5s4 1.3 4 3.5"/><circle cx="6" cy="4" r="2"/>
          </svg>
          Capacidad: ${m.capacidad} personas
        </div>
        <div class="mesa-estado">
          ${m.disponible
            ? '<span class="badge-libre">Libre</span>'
            : '<span class="badge-ocupada">Ocupada</span>'}
        </div>
        ${!m.disponible && m.reserva_cliente
          ? `<div class="mesa-reserva">
               <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round">
                 <circle cx="6" cy="6" r="5"/><path d="M6 4v2l1.5 1.5"/>
               </svg>
               ${escHtml(m.reserva_cliente)} &mdash; ${m.reserva_hora}
             </div>`
          : ""}
      </div>
    `).join("");
  } catch {
    mostrarToast("Error al cargar mesas.", "error");
  }
}

// ── Disponibilidad ─────────────────────────────────────────
async function cargarDisponibilidad() {
  try {
    const res  = await fetch("/mesas/stats");
    const data = await res.json();
    document.getElementById("disp-libres").textContent   = data.mesas_libres;
    document.getElementById("disp-ocupadas").textContent = data.mesas_ocupadas;
  } catch {
    mostrarToast("Error al cargar disponibilidad.", "error");
  }
}

async function consultarMesasParaPersonas() {
  const personas = parseInt(document.getElementById("consulta-personas").value);
  if (!personas || personas < 1) {
    mostrarToast("Ingresa un numero valido de personas.", "error");
    return;
  }

  try {
    const res   = await fetch(`/mesas/disponibles?personas=${personas}`);
    const mesas = await res.json();
    const el    = document.getElementById("resultado-consulta");

    if (!mesas.length) {
      el.innerHTML = `
        <div class="resultado-empty">
          ${icons.nodata}
          No hay mesas disponibles para ${personas} personas.
        </div>`;
      return;
    }

    el.innerHTML = `
      <div class="resultado-ok">
        <p>Mesas disponibles para ${personas} personas</p>
        <div class="resultado-mesas">
          ${mesas.map((m) => `
            <div class="resultado-mesa-item">
              <strong>Mesa ${m.id}</strong>
              <span>Capacidad: ${m.capacidad}</span>
            </div>
          `).join("")}
        </div>
      </div>`;
  } catch {
    mostrarToast("Error al consultar mesas.", "error");
  }
}

// ── Utils ──────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
