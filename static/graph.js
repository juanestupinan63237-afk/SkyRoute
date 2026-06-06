/**
 * graph.js — Motor de visualización del grafo aéreo
 * Renderiza nodos (aeropuertos) y aristas (rutas) sobre un canvas HTML5.
 * Soporta pan, zoom, hover tooltip y resaltado de rutas.
 */

class GraphRenderer {
  constructor(canvasId) {
    this.canvas  = document.getElementById(canvasId);
    this.ctx     = this.canvas.getContext('2d');
    this.nodes   = [];       // { id, x, y, isHub, name, city, country, ... }
    this.edges   = [];       // { origin, destination, distance, aircraft, isBlocked }
    this.positions = {};     // iataId -> {x, y}

    // Estado de cámara
    this.offsetX = 0;
    this.offsetY = 0;
    this.scale   = 1;
    this.minScale = 0.25;
    this.maxScale = 3;

    // Interacción
    this.dragging    = false;
    this.lastMouse   = { x: 0, y: 0 };
    this.hoveredNode = null;
    this.highlightedRoute = [];   // array de iataIds a resaltar
    this.blockedEdges = new Set();// "orig->dest"

    this._bindEvents();
    this._resize();
    window.addEventListener('resize', () => this._resize());
  }

  // ──────────────────────────────────────────
  // Carga de datos
  // ──────────────────────────────────────────
  loadGraph(nodes, edges) {
    this.nodes = nodes;
    this.edges = edges;
    this._autoLayout();
    this.fitToScreen();
    this.render();
  }

  _autoLayout() {
    // Distribución en círculo con hubs al centro
    const hubs      = this.nodes.filter(n => n.isHub);
    const secondary = this.nodes.filter(n => !n.isHub);
    const W = this.canvas.width;
    const H = this.canvas.height;
    const cx = W / 2, cy = H / 2;

    // Hubs en círculo interior
    hubs.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / hubs.length - Math.PI / 2;
      const r = Math.min(W, H) * 0.25;
      n.x = cx + r * Math.cos(angle);
      n.y = cy + r * Math.sin(angle);
    });

    // Secundarios en círculo exterior
    secondary.forEach((n, i) => {
      const angle = (2 * Math.PI * i) / secondary.length - Math.PI / 2;
      const r = Math.min(W, H) * 0.42;
      n.x = cx + r * Math.cos(angle);
      n.y = cy + r * Math.sin(angle);
    });

    // Guardar posiciones
    this.nodes.forEach(n => { this.positions[n.id] = { x: n.x, y: n.y }; });
  }

  fitToScreen() {
    this.offsetX = 0;
    this.offsetY = 0;
    this.scale   = 1;
  }

  // ──────────────────────────────────────────
  // Render principal
  // ──────────────────────────────────────────
  render() {
    const ctx = this.ctx;
    const W = this.canvas.width;
    const H = this.canvas.height;

    ctx.clearRect(0, 0, W, H);
    ctx.save();
    ctx.translate(this.offsetX, this.offsetY);
    ctx.scale(this.scale, this.scale);

    this._drawEdges();
    this._drawNodes();

    ctx.restore();
    requestAnimationFrame(() => this.render());
  }

  _drawEdges() {
    const ctx = this.ctx;
    this.edges.forEach(edge => {
      const src = this.positions[edge.origin];
      const dst = this.positions[edge.destination];
      if (!src || !dst) return;

      const isBlocked   = edge.isBlocked || this.blockedEdges.has(`${edge.origin}->${edge.destination}`);
      const isHighlighted = this._isHighlightedEdge(edge.origin, edge.destination);

      ctx.beginPath();
      ctx.moveTo(src.x, src.y);
      ctx.lineTo(dst.x, dst.y);

      if (isBlocked) {
        ctx.strokeStyle = '#f85149';
        ctx.lineWidth   = 2;
        ctx.setLineDash([6, 4]);
      } else if (isHighlighted) {
        ctx.strokeStyle = '#ffa657';
        ctx.lineWidth   = 3;
        ctx.setLineDash([]);
      } else {
        ctx.strokeStyle = '#30363d';
        ctx.lineWidth   = 1;
        ctx.setLineDash([]);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Flecha de dirección
      this._drawArrow(ctx, src, dst, isBlocked ? '#f85149' : isHighlighted ? '#ffa657' : '#444');

      // Etiqueta de distancia (solo si hay zoom suficiente)
      if (this.scale > 0.7) {
        const mx = (src.x + dst.x) / 2;
        const my = (src.y + dst.y) / 2;
        ctx.save();
        ctx.font      = `${10 / this.scale}px JetBrains Mono, monospace`;
        ctx.fillStyle = '#8b949e';
        ctx.textAlign = 'center';
        ctx.fillText(`${edge.distance}km`, mx, my - 4);
        ctx.restore();
      }
    });
  }

  _drawArrow(ctx, src, dst, color) {
    const dx = dst.x - src.x;
    const dy = dst.y - src.y;
    const len = Math.sqrt(dx*dx + dy*dy);
    if (len < 1) return;
    const ux = dx / len, uy = dy / len;
    const nodeR = 16;
    const ax = dst.x - ux * (nodeR + 6);
    const ay = dst.y - uy * (nodeR + 6);
    const angle = Math.atan2(uy, ux);
    const aSize = 6;

    ctx.save();
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(ax, ay);
    ctx.lineTo(ax - aSize * Math.cos(angle - 0.4), ay - aSize * Math.sin(angle - 0.4));
    ctx.lineTo(ax - aSize * Math.cos(angle + 0.4), ay - aSize * Math.sin(angle + 0.4));
    ctx.closePath();
    ctx.fill();
    ctx.restore();
  }

  _drawNodes() {
    const ctx = this.ctx;
    this.nodes.forEach(node => {
      const pos = this.positions[node.id];
      if (!pos) return;
      const r = node.isHub ? 18 : 13;
      const isHovered = this.hoveredNode && this.hoveredNode.id === node.id;

      // Glow on hover
      if (isHovered) {
        ctx.shadowColor = node.isHub ? '#58a6ff' : '#7ee787';
        ctx.shadowBlur  = 16;
      }

      // Círculo
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, r, 0, 2 * Math.PI);
      ctx.fillStyle = node.isHub ? '#1c3a5e' : '#1c3a2e';
      ctx.fill();
      ctx.strokeStyle = node.isHub ? '#58a6ff' : '#7ee787';
      ctx.lineWidth   = isHovered ? 2.5 : 1.5;
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Código IATA
      ctx.font      = `bold ${node.isHub ? 9 : 8}px Space Grotesk, sans-serif`;
      ctx.fillStyle = '#e6edf3';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.id, pos.x, pos.y);

      // Nombre debajo
      if (this.scale > 0.55) {
        ctx.font      = `${7 / this.scale}px Space Grotesk, sans-serif`;
        ctx.fillStyle = '#8b949e';
        ctx.fillText(node.city || node.name, pos.x, pos.y + r + 10 / this.scale);
      }
    });
  }

  _isHighlightedEdge(origin, destination) {
    for (let i = 0; i < this.highlightedRoute.length - 1; i++) {
      if (this.highlightedRoute[i] === origin && this.highlightedRoute[i+1] === destination) return true;
    }
    return false;
  }

  // ──────────────────────────────────────────
  // Resaltado de rutas y bloqueos
  // ──────────────────────────────────────────
  highlightRoute(stops) {
    this.highlightedRoute = stops || [];
  }

  markBlocked(origin, destination) {
    this.blockedEdges.add(`${origin}->${destination}`);
  }

  unmarkBlocked(origin, destination) {
    this.blockedEdges.delete(`${origin}->${destination}`);
  }

  syncBlockedFromEdges(edges) {
    this.blockedEdges.clear();
    edges.forEach(e => {
      if (e.isBlocked) this.blockedEdges.add(`${e.origin}->${e.destination}`);
    });
  }

  // ──────────────────────────────────────────
  // Eventos (pan, zoom, hover, click)
  // ──────────────────────────────────────────
  _bindEvents() {
    const c = this.canvas;

    c.addEventListener('mousedown', e => {
      this.dragging  = true;
      this.lastMouse = { x: e.clientX, y: e.clientY };
    });
    c.addEventListener('mouseup',   () => { this.dragging = false; });
    c.addEventListener('mouseleave',() => { this.dragging = false; this.hoveredNode = null; });

    c.addEventListener('mousemove', e => {
      if (this.dragging) {
        this.offsetX += e.clientX - this.lastMouse.x;
        this.offsetY += e.clientY - this.lastMouse.y;
        this.lastMouse = { x: e.clientX, y: e.clientY };
      } else {
        const world = this._toWorld(e.offsetX, e.offsetY);
        this.hoveredNode = this._nodeAt(world.x, world.y);
        this._updateTooltip(e, this.hoveredNode);
      }
    });

    c.addEventListener('wheel', e => {
      e.preventDefault();
      const factor = e.deltaY < 0 ? 1.1 : 0.9;
      const newScale = Math.min(this.maxScale, Math.max(this.minScale, this.scale * factor));
      const rect = c.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      this.offsetX = mx - (mx - this.offsetX) * (newScale / this.scale);
      this.offsetY = my - (my - this.offsetY) * (newScale / this.scale);
      this.scale   = newScale;
    }, { passive: false });

    c.addEventListener('click', e => {
      const world = this._toWorld(e.offsetX, e.offsetY);
      const node  = this._nodeAt(world.x, world.y);
      if (node && this.onNodeClick) this.onNodeClick(node);
    });
  }

  _toWorld(sx, sy) {
    return {
      x: (sx - this.offsetX) / this.scale,
      y: (sy - this.offsetY) / this.scale
    };
  }

  _nodeAt(wx, wy) {
    return this.nodes.find(n => {
      const pos = this.positions[n.id];
      if (!pos) return false;
      const r = n.isHub ? 18 : 13;
      const dx = pos.x - wx, dy = pos.y - wy;
      return Math.sqrt(dx*dx + dy*dy) <= r;
    }) || null;
  }

  _updateTooltip(mouseEvent, node) {
    const tip = document.getElementById('airportTooltip');
    if (!node) { tip.classList.add('hidden'); return; }
    tip.classList.remove('hidden');
    document.getElementById('ttHeader').textContent = `${node.id} — ${node.name}`;
    document.getElementById('ttBody').innerHTML =
      `📍 ${node.city}, ${node.country}<br>` +
      `🏷 ${node.isHub ? 'Hub' : 'Secundario'}<br>` +
      `🛏 Alojamiento: $${node.accommodationCost}/noche<br>` +
      `🍽 Comida: $${node.foodCost}/comida<br>` +
      `🎯 Actividades: ${node.activities ? node.activities.length : 0}<br>` +
      `💼 Trabajos: ${node.jobs ? node.jobs.length : 0}`;
    const rect = this.canvas.getBoundingClientRect();
    let tx = mouseEvent.clientX - rect.left + 14;
    let ty = mouseEvent.clientY - rect.top  - 10;
    if (tx + 240 > rect.width)  tx -= 260;
    if (ty + 120 > rect.height) ty -= 140;
    tip.style.left = tx + 'px';
    tip.style.top  = ty + 'px';
  }

  // ──────────────────────────────────────────
  // Resize
  // ──────────────────────────────────────────
  _resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width  = rect.width;
    this.canvas.height = rect.height - 44; // toolbar height
    if (this.nodes.length) this._autoLayout();
  }
}
