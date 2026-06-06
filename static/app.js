/**
 * app.js — Lógica principal de SkyRoute Planner
 * Maneja toda la interacción del usuario con la API Flask.
 */

// ─────────────────────────────────────────────
// Configuración
// ─────────────────────────────────────────────
const API = '';   // mismo origen que Flask
let currentTravelerId = null;
let selectedJobId     = null;
let graphData         = { nodes: [], edges: [] };
const renderer = new GraphRenderer('graphCanvas');

// ─────────────────────────────────────────────
// Utilidades API
// ─────────────────────────────────────────────
async function api(method, path, body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res  = await fetch(API + path, opts);
  return res.json();
}

function log(msg, type = 'info') {
  const list  = document.getElementById('logList');
  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  const now   = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  entry.innerHTML = `<div class="log-time">${now}</div>${msg}`;
  list.prepend(entry);
  if (list.children.length > 80) list.lastChild.remove();
}

function setStatus(msg, cls = '') {
  const el = document.getElementById('apiStatus');
  el.textContent   = msg;
  el.className     = 'header-status ' + cls;
}

// ─────────────────────────────────────────────
// Carga inicial del grafo
// ─────────────────────────────────────────────
async function loadGraph() {
  try {
    const res = await api('GET', '/graph');
    if (!res.success) throw new Error(res.message);
    graphData = res.data;
    renderer.loadGraph(graphData.nodes, graphData.edges);
    populateSelects();
    setStatus(`✓ ${graphData.nodes.length} aeropuertos cargados`, 'ok');
    log(`Grafo cargado: ${graphData.nodes.length} nodos, ${graphData.edges.length} aristas`, 'success');
  } catch (e) {
    setStatus('Error de conexión', 'err');
    log(`Error cargando grafo: ${e.message}`, 'error');
  }
}

function populateSelects() {
  const selects = ['routeOrigin','routeDest','blockOrigin','blockDest','inOrigin'];
  selects.forEach(id => {
    const el = document.getElementById(id);
    const cur = el.value;
    // mantener solo el primer option placeholder
    while (el.options.length > 1) el.remove(1);
    graphData.nodes
      .sort((a,b) => a.id.localeCompare(b.id))
      .forEach(n => {
        const opt = new Option(`${n.id} — ${n.city}`, n.id);
        el.add(opt);
      });
    if (cur) el.value = cur;
  });
}

// Click en nodo del grafo
renderer.onNodeClick = (node) => {
  log(`🏛 <b>${node.id}</b> — ${node.name}, ${node.city}`, 'info');
};

// ─────────────────────────────────────────────
// Viajero
// ─────────────────────────────────────────────
document.getElementById('btnNewTraveler').onclick = () => {
  document.getElementById('formNewTraveler').classList.toggle('hidden');
};

document.getElementById('btnCreateTraveler').onclick = async () => {
  const name   = document.getElementById('inName').value.trim();
  const budget = parseFloat(document.getElementById('inBudget').value);
  const time   = parseFloat(document.getElementById('inTime').value);
  const origin = document.getElementById('inOrigin').value;
  if (!name || !budget || !time || !origin) { log('Completa todos los campos', 'warning'); return; }

  const tid = 'T' + Date.now().toString().slice(-5);
  const res = await api('POST', '/traveler', { id: tid, name, budget, timeAvailable: time, startAirport: origin });
  if (!res.success) { log(`Error: ${res.message}`, 'error'); return; }

  currentTravelerId = tid;
  document.getElementById('formNewTraveler').classList.add('hidden');
  log(`✈ Viajero <b>${name}</b> creado en ${origin}`, 'success');
  await refreshTraveler();
};

async function refreshTraveler() {
  if (!currentTravelerId) return;
  const res = await api('GET', `/traveler/${currentTravelerId}`);
  if (!res.success) { log(`Error: ${res.message}`, 'error'); return; }

  const d = res.data;
  renderTravelerInfo(d.travelerStatus, d.currentAirportInfo);
  renderFlights(d.flights);
  renderActivities(d.activities);
  renderJobs(d.jobs, d.travelerStatus.canWork);
  updateTransitPanel(d.travelerStatus);

  document.getElementById('optionsCard').style.display = 'flex';
  document.getElementById('currentIata').textContent = d.travelerStatus.currentAirport;
}

function renderTravelerInfo(status, airport) {
  const budgetPct = (status.budgetLeft / status.initialBudget * 100).toFixed(0);
  const budgetClass = budgetPct > 50 ? 'green' : budgetPct > 35 ? 'yellow' : 'red';
  document.getElementById('travelerInfo').innerHTML = `
    <div class="info-grid">
      <div class="info-kv"><span class="info-k">Nombre</span><span class="info-v">${status.name}</span></div>
      <div class="info-kv"><span class="info-k">Aeropuerto</span><span class="info-v">${status.currentAirport}</span></div>
      <div class="info-kv"><span class="info-k">Presupuesto</span><span class="info-v ${budgetClass}">$${status.budgetLeft.toFixed(0)}</span></div>
      <div class="info-kv"><span class="info-k">Tiempo</span><span class="info-v">${status.timeLeft.toFixed(1)}h</span></div>
      <div class="info-kv"><span class="info-k">Puede trabajar</span><span class="info-v ${status.canWork ? 'yellow' : 'green'}">${status.canWork ? 'Sí' : 'No'}</span></div>
      <div class="info-kv"><span class="info-k">Visitados</span><span class="info-v">${status.visitedAirports.length}</span></div>
    </div>
    ${status.visitedAirports.length ? `<div style="font-size:.72rem;color:var(--text-muted);margin-top:4px">📍 ${status.visitedAirports.join(' → ')}</div>` : ''}
  `;
}

function renderFlights(flights) {
  const list = document.getElementById('flightsList');
  list.innerHTML = '';
  if (!flights || !flights.length) { list.innerHTML = '<div class="info-empty">Sin vuelos disponibles</div>'; return; }
  flights.forEach(f => {
    const aircraft = document.getElementById('selAircraft').value;
    const opt = f.aircraftOptions.find(a => a.type === aircraft) || f.aircraftOptions[0];
    const item = document.createElement('div');
    item.className = `list-item${f.isBlocked ? ' blocked-item' : ''}`;
    item.innerHTML = `
      <div class="item-title">${f.destination} — ${f.destinationCity}</div>
      <div class="item-sub">${f.distanceKm} km · $${opt.cost} · ${(opt.timeMin/60).toFixed(1)}h${f.isBlocked ? ' · ⛔ BLOQUEADA' : ''}</div>
    `;
    if (!f.isBlocked) {
      item.onclick = () => startFlight(f.destination);
    }
    list.appendChild(item);
  });
}

function renderActivities(activities) {
  const list = document.getElementById('activitiesList');
  list.innerHTML = '';
  if (!activities || !activities.length) { list.innerHTML = '<div class="info-empty">Sin actividades</div>'; return; }
  activities.forEach(a => {
    const item = document.createElement('div');
    item.className = 'list-item';
    item.innerHTML = `
      <div class="item-title">${a.isImportant ? '⚠️' : '🎯'} ${a.name}</div>
      <div class="item-sub">${a.duration} min · $${a.price} USD${a.isImportant ? ' · Obligatoria' : ''}</div>
    `;
    item.onclick = () => doActivity(a.id);
    list.appendChild(item);
  });
}

function renderJobs(jobs, canWork) {
  const list    = document.getElementById('jobsList');
  const jobForm = document.getElementById('jobForm');
  list.innerHTML = '';
  if (!canWork) {
    list.innerHTML = '<div class="info-empty">Solo disponible si presupuesto &lt; 35%</div>';
    jobForm.classList.add('hidden');
    return;
  }
  if (!jobs || !jobs.length) { list.innerHTML = '<div class="info-empty">Sin trabajos disponibles</div>'; return; }
  jobs.forEach(j => {
    const item = document.createElement('div');
    item.className = 'list-item';
    item.innerHTML = `
      <div class="item-title">💼 ${j.name}</div>
      <div class="item-sub">$${j.rate}/hora · máx ${j.maxHours}h</div>
    `;
    item.onclick = () => {
      selectedJobId = j.id;
      document.getElementById('inJobHours').max = j.maxHours;
      document.getElementById('inJobHours').placeholder = `Horas (máx ${j.maxHours})`;
      jobForm.classList.remove('hidden');
      list.querySelectorAll('.list-item').forEach(el => el.style.borderColor = '');
      item.style.borderColor = 'var(--primary)';
    };
    list.appendChild(item);
  });
}

// ─────────────────────────────────────────────
// Acciones de vuelo / actividad / trabajo
// ─────────────────────────────────────────────
async function startFlight(destination) {
  if (!currentTravelerId) return;
  const aircraft  = document.getElementById('selAircraft').value;
  const criterion = document.getElementById('selCriterion').value;
  const res = await api('POST', `/traveler/${currentTravelerId}/fly`, { destination, aircraftType: aircraft, criterion });
  if (!res.success) { log(`Error vuelo: ${res.message}`, 'error'); return; }
  log(`✈ Vuelo iniciado → <b>${destination}</b> (${aircraft}, por ${criterion})`, 'info');
  await refreshTraveler();
}

async function doActivity(activityId) {
  if (!currentTravelerId) return;
  const res = await api('POST', `/traveler/${currentTravelerId}/activity`, { activityId });
  if (!res.success) { log(`Error actividad: ${res.message}`, 'error'); return; }
  log(`🎯 Actividad realizada — presupuesto: $${res.data.budgetLeft}`, 'success');
  await refreshTraveler();
}

document.getElementById('btnConfirmJob').onclick = async () => {
  if (!currentTravelerId || !selectedJobId) return;
  const hours = parseFloat(document.getElementById('inJobHours').value);
  if (!hours || hours <= 0) { log('Ingresa las horas a trabajar', 'warning'); return; }
  const res = await api('POST', `/traveler/${currentTravelerId}/job`, { jobId: selectedJobId, hours });
  if (!res.success) { log(`Error trabajo: ${res.message}`, 'error'); return; }
  log(`💼 Trabajo realizado ${hours}h — presupuesto: $${res.data.budgetLeft}`, 'success');
  selectedJobId = null;
  document.getElementById('jobForm').classList.add('hidden');
  await refreshTraveler();
};

// Actualizar lista de vuelos cuando cambia aeronave
document.getElementById('selAircraft').onchange = async () => {
  if (currentTravelerId) await refreshTraveler();
};

// ─────────────────────────────────────────────
// Panel tránsito
// ─────────────────────────────────────────────
function updateTransitPanel(status) {
  const panel = document.getElementById('transitPanel');
  if (!status.inTransit) { panel.classList.add('hidden'); return; }
  panel.classList.remove('hidden');
}

document.getElementById('btnTick').onclick     = () => tickTime(0.5);
document.getElementById('btnTickHour').onclick  = () => tickTime(1.0);

async function tickTime(hours) {
  if (!currentTravelerId) return;
  const res = await api('POST', `/traveler/${currentTravelerId}/tick`, { timeStepHours: hours });
  if (!res.success) { log(`Error tick: ${res.message}`, 'error'); return; }
  const d = res.data;
  const pct = (d.progress * 100).toFixed(0);
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('transitPct').textContent   = `${pct}% — ${d.hoursProgress.toFixed(1)}h / ${d.hoursTotal.toFixed(1)}h`;
  if (!d.inTransit) {
    log(`🛬 Aterrizó en <b>${d.currentAirport}</b>`, 'success');
  } else {
    log(`⏱ Tick +${hours}h — progreso ${pct}%`, 'info');
  }
  await refreshTraveler();
}

document.getElementById('btnInterrupt').onclick = async () => {
  const res_status = await api('GET', `/traveler/${currentTravelerId}`);
  if (!res_status.success) return;
  const flight = res_status.data.travelerStatus;
  if (!flight.inTransit) { log('No hay vuelo en curso', 'warning'); return; }

  // Obtener origen/destino del vuelo actual desde el backend
  const travRes = await api('GET', `/traveler/${currentTravelerId}`);
  const inFlight = travRes.data?.travelerStatus?.inTransit;
  if (!inFlight) { log('No hay vuelo activo para interrumpir', 'warning'); return; }

  // Pedir al usuario que confirme
  const orig = prompt('Código IATA de origen de la ruta a bloquear:');
  const dest = prompt('Código IATA de destino de la ruta a bloquear:');
  if (!orig || !dest) return;

  const res = await api('POST', '/route/block', {
    travelerId: currentTravelerId,
    origin: orig.toUpperCase(),
    destination: dest.toUpperCase()
  });
  if (!res.success) { log(`Error bloqueo: ${res.message}`, 'error'); return; }
  renderer.markBlocked(orig.toUpperCase(), dest.toUpperCase());
  log(`⛔ Ruta <b>${orig}→${dest}</b> bloqueada${res.data.recalculated ? ' — Ruta recalculada: ' + res.data.newRoute.join('→') : ''}`, 'warning');
  if (res.data.newRoute?.length) renderer.highlightRoute(res.data.newRoute);
  await refreshTraveler();
};

// ─────────────────────────────────────────────
// Calcular ruta (R2)
// ─────────────────────────────────────────────
document.getElementById('btnCalcRoute').onclick = async () => {
  const origin    = document.getElementById('routeOrigin').value;
  const dest      = document.getElementById('routeDest').value;
  const criterion = document.getElementById('routeCriterion').value;
  const excludeSecondary = document.getElementById('excludeSecondary').checked;
  if (!origin || !dest) { log('Selecciona origen y destino', 'warning'); return; }

  const res = await api('POST', '/route/calculate', { origin, destination: dest, criterion, excludeSecondary });
  const box = document.getElementById('routeResult');
  box.classList.remove('hidden');

  if (!res.success) {
    box.innerHTML = `<span style="color:var(--danger)">${res.message}</span>`;
    return;
  }
  const d = res.data;
  renderer.highlightRoute(d.stops);

  const stopsHtml = d.stops.map((s, i) =>
    `<span class="route-stop">${s}</span>${i < d.stops.length-1 ? '<span class="route-arrow">→</span>' : ''}`
  ).join('');

  box.innerHTML = `
    <div class="route-stops">${stopsHtml}</div>
    <div style="font-size:.75rem;color:var(--text-muted)">
      Criterio: <b>${criterion}</b> · Total: <b>${d.totalCost.toFixed(2)}</b> · ${d.totalStops} paradas
    </div>
    <table class="report-table" style="margin-top:6px">
      <tr><th>Tramo</th><th>Distancia</th><th>Costo</th><th>Aeronave</th></tr>
      ${d.segments.map(s => `<tr><td>${s.from}→${s.to}</td><td>${s.distance}km</td><td>$${s.cost}</td><td>${s.aircraft||'-'}</td></tr>`).join('')}
    </table>
  `;
  log(`🗺 Ruta <b>${origin}→${dest}</b> por ${criterion}: ${d.stops.join('→')} ($${d.totalCost.toFixed(0)})`, 'success');
};

// ─────────────────────────────────────────────
// Bloquear / desbloquear ruta (R4)
// ─────────────────────────────────────────────
document.getElementById('btnBlock').onclick = async () => {
  const orig = document.getElementById('blockOrigin').value;
  const dest = document.getElementById('blockDest').value;
  if (!orig || !dest) { log('Selecciona origen y destino para bloquear', 'warning'); return; }
  const tid  = currentTravelerId || 'NONE';
  const res  = await api('POST', '/route/block', { travelerId: tid, origin: orig, destination: dest });
  const box  = document.getElementById('blockResult');
  box.classList.remove('hidden');
  if (!res.success) { box.innerHTML = `<span style="color:var(--danger)">${res.message}</span>`; return; }
  renderer.markBlocked(orig, dest);
  box.innerHTML = `⛔ Ruta ${orig}→${dest} bloqueada${res.data.recalculated ? '<br>Nueva ruta: ' + res.data.newRoute.join('→') : ''}`;
  log(`⛔ Ruta <b>${orig}→${dest}</b> bloqueada`, 'warning');
  if (res.data.recalculated) renderer.highlightRoute(res.data.newRoute);
};

document.getElementById('btnUnblock').onclick = async () => {
  const orig = document.getElementById('blockOrigin').value;
  const dest = document.getElementById('blockDest').value;
  if (!orig || !dest) { log('Selecciona origen y destino para desbloquear', 'warning'); return; }
  const res = await api('POST', '/route/unblock', { origin: orig, destination: dest });
  if (!res.success) { log(`Error: ${res.message}`, 'error'); return; }
  renderer.unmarkBlocked(orig, dest);
  log(`✅ Ruta <b>${orig}→${dest}</b> desbloqueada`, 'success');
  document.getElementById('blockResult').classList.add('hidden');
};

// ─────────────────────────────────────────────
// Reporte final (R5)
// ─────────────────────────────────────────────
document.getElementById('btnReport').onclick = async () => {
  if (!currentTravelerId) { log('Sin viajero activo', 'warning'); return; }
  const res = await api('GET', `/traveler/${currentTravelerId}/report`);
  if (!res.success) { log(`Error reporte: ${res.message}`, 'error'); return; }
  renderReport(res.data);
  document.getElementById('reportModal').classList.remove('hidden');
};

document.getElementById('btnCloseReport').onclick = () => {
  document.getElementById('reportModal').classList.add('hidden');
};

function renderReport(data) {
  const t   = data.traveler;
  const box = document.getElementById('reportContent');
  box.innerHTML = `
    <div class="report-section">
      <h4>Resumen del viajero</h4>
      <div class="report-grid">
        <div class="report-kv"><div class="report-k">Nombre</div><div class="report-v">${t.name}</div></div>
        <div class="report-kv"><div class="report-k">Presupuesto inicial</div><div class="report-v">$${t.initial_budget}</div></div>
        <div class="report-kv"><div class="report-k">Total gastado</div><div class="report-v yellow">$${t.total_spent}</div></div>
        <div class="report-kv"><div class="report-k">Total ganado</div><div class="report-v green">$${t.total_earned}</div></div>
        <div class="report-kv"><div class="report-k">Saldo final</div><div class="report-v green">$${t.final_balance}</div></div>
        <div class="report-kv"><div class="report-k">Tiempo restante</div><div class="report-v">${t.time_left_hours}h</div></div>
      </div>
    </div>

    ${data.destinations.length ? `
    <div class="report-section">
      <h4>Destinos visitados (${data.destinations.length})</h4>
      <table class="report-table">
        <tr><th>IATA</th><th>Ciudad</th><th>País</th><th>Hub</th></tr>
        ${data.destinations.map(d => `<tr><td><b>${d.iata_code}</b></td><td>${d.city}</td><td>${d.country}</td><td>${d.is_hub ? '✓' : ''}</td></tr>`).join('')}
      </table>
    </div>` : ''}

    ${data.flights.length ? `
    <div class="report-section">
      <h4>Vuelos realizados</h4>
      <table class="report-table">
        <tr><th>Origen</th><th>Destino</th><th>Horas</th></tr>
        ${data.flights.map(f => `<tr><td>${f.origin}</td><td>${f.destination}</td><td>${f.hours}h</td></tr>`).join('')}
      </table>
    </div>` : ''}

    ${data.activities.length ? `
    <div class="report-section">
      <h4>Actividades realizadas</h4>
      <table class="report-table">
        <tr><th>Nombre</th><th>Duración</th><th>Costo</th></tr>
        ${data.activities.map(a => `<tr><td>${a.name}</td><td>${a.duration_minutes} min</td><td>$${a.price_usd}</td></tr>`).join('')}
      </table>
    </div>` : ''}

    ${data.jobs.length ? `
    <div class="report-section">
      <h4>Trabajos realizados</h4>
      <table class="report-table">
        <tr><th>ID</th><th>Horas</th><th>Ingreso</th></tr>
        ${data.jobs.map(j => `<tr><td>${j.job_id}</td><td>${j.hours_worked}h</td><td class="green">$${j.earned_usd}</td></tr>`).join('')}
      </table>
    </div>` : ''}
  `;
}

// ─────────────────────────────────────────────
// Tabs sidebar
// ─────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(btn => {
  btn.onclick = () => {
    const tabId = btn.dataset.tab;
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
    btn.classList.add('active');
    document.getElementById('tab' + tabId.charAt(0).toUpperCase() + tabId.slice(1)).classList.remove('hidden');
  };
});

// Centrar grafo
document.getElementById('btnFitGraph').onclick = () => renderer.fitToScreen();

// ─────────────────────────────────────────────
// Init
// ─────────────────────────────────────────────
loadGraph();
