import { renderDynamicChart, renderStaticChart } from './mlops-charts.js';

const API_BASE = location.origin + "/api";

const elProject = document.getElementById("projectSelect");
const elRunList = document.getElementById("runList");
const elStatus = document.getElementById("statusText");
const svg = document.getElementById("graph");
const elThemeToggle = document.getElementById("themeToggle");
// Dynamic charts elements
const elDynamicChartsContainer = document.getElementById("dynamicChartsContainer");
const elDynamicChartsGrid = document.getElementById("dynamicChartsGrid");
// Modal elements for chart preview
const elChartModal = document.getElementById("chartModal");
const elChartModalClose = document.getElementById("chartModalClose");
const elChartModalImage = document.getElementById("chartModalImage");
const elChartModalMessage = document.getElementById("chartModalMessage");

let graphData = { nodes: [], adj: {}, indeg: {} };
let positions = {}; // node -> {x,y}
let current = { project: null, runId: null };
let pollTimer = null;
let runPollTimer = null;
let tooltipEl = null;
let dynamicChartCleanups = []; // Cleanup functions for dynamic charts
let requestGen = 0; // Bump to invalidate in-flight async updates on project/run change
let lastStatusMap = {}; // Stable process status across polls to avoid flicker
let emptyStatusStreak = 0; // Count consecutive polls with empty process_status
let chartNodes = new Set(); // Nodes that should be rendered as squares (type: chart)
let runsCache = []; // Cached runs list for sidebar rendering
let dynamicChartsInitTimer = null; // Periodic attempt to (re)initialize dynamic charts
let dynamicChartsInitialized = false; // Set true once dynamic charts are rendered
let chartModalPollTimer = null; // Timer for auto-refreshing chart availability
let isModalOpen = false; // Track if chart modal is currently open
let chartCache = new Map(); // nodeName -> { blob, objectUrl }

// ---- Theme handling (light/dark) ----
function updateThemeToggleUI(theme) {
  if (!elThemeToggle) return;
  elThemeToggle.textContent = (theme === 'light') ? '☀️' : '🌙';
  elThemeToggle.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
  elThemeToggle.title = `Switch to ${theme === 'light' ? 'dark' : 'light'} mode`;
}

function applyChartTheme() {
  try {
    const cs = getComputedStyle(document.documentElement);
    const textColor = cs.getPropertyValue('--color-text').trim();
    const borderColor = cs.getPropertyValue('--color-border').trim();
    const gridColor = (cs.getPropertyValue('--color-border-2').trim()) || borderColor;
    if (window.Chart) {
      window.Chart.defaults.color = textColor;
      window.Chart.defaults.borderColor = borderColor;
      try { window.Chart.defaults.scale.grid.color = gridColor; } catch {}
      try { window.Chart.defaults.plugins.legend.labels.color = textColor; } catch {}
    }
  } catch {}
}

function applyTheme(theme) {
  const t = (theme === 'light') ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', t);
  try { localStorage.setItem('theme', t); } catch {}
  updateThemeToggleUI(t);
  applyChartTheme();
  // Re-render dynamic charts to adopt new theme defaults
  try { loadDynamicCharts(); } catch {}
}

// Initialize theme early
(() => {
  let t = null;
  try { t = (localStorage.getItem('theme') || '').toLowerCase(); } catch {}
  if (t !== 'light' && t !== 'dark') {
    t = 'dark'; // preserve current default look
  }
  applyTheme(t);
})();

if (elThemeToggle) {
  elThemeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
  });
}

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return await res.json();
}

// Chart pre-loading functions
async function preloadChartForNode(nodeName) {
  // Skip if already cached
  if (chartCache.has(nodeName)) {
    return;
  }
  
  if (!current.project || !current.runId) {
    return;
  }
  
  try {
    // Check if this node is cached and has a cached_run_id
    const nodeInfo = lastProcessInfo[nodeName] || {};
    const nodeStatus = (lastStatusMap[nodeName] || "pending").toLowerCase();
    const cachedRunId = (nodeStatus === "cached" && nodeInfo.cached_run_id) ? nodeInfo.cached_run_id : null;
    
    // Use cached run ID if available, otherwise current run ID
    const runIdToFetch = cachedRunId || current.runId;
    
    // Fetch chart data for the target run
    const url = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(runIdToFetch)}/charts`;
    const data = await fetchJSON(url);
    const charts = data.charts || {};
    
    // Look for chart items matching the node name
    let chartItem = null;
    for (const [chartName, chartInfo] of Object.entries(charts)) {
      if (chartName === nodeName && chartInfo.items && chartInfo.items.length > 0) {
        chartItem = chartInfo.items[0]; // Take the first item
        break;
      }
    }
    
    if (chartItem && chartItem.object_path) {
      // Chart is available, fetch and cache it
      console.log(`Pre-loading chart for ${nodeName} from run ${runIdToFetch}:`, chartItem);
      await cacheChartImage(nodeName, chartItem, runIdToFetch);
    }
  } catch (error) {
    console.error(`Error pre-loading chart for ${nodeName}:`, error);
  }
}

async function cacheChartImage(nodeName, chartItem, runIdToFetch) {
  try {
    const params = new URLSearchParams();
    if (chartItem.object_path) params.set('uri', chartItem.object_path);
    if (chartItem.cache_path) params.set('cache_path', chartItem.cache_path);
    
    // Use the provided runId or fallback to current.runId
    const targetRunId = runIdToFetch || current.runId;
    
    const fetchUrl = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(targetRunId)}/charts/fetch?` + params.toString();
    console.log(`Pre-fetching chart image for ${nodeName} from: ${fetchUrl}`);
    
    const resp = await fetch(fetchUrl);
    if (!resp.ok) {
      throw new Error(`Chart fetch failed: ${resp.status}`);
    }
    
    const blob = await resp.blob();
    const objectUrl = URL.createObjectURL(blob);
    
    // Store in cache
    chartCache.set(nodeName, { blob, objectUrl });
    console.log(`Chart for ${nodeName} cached successfully`);
  } catch (error) {
    console.error(`Error caching chart image for ${nodeName}:`, error);
  }
}

function clearChartCache() {
  // Revoke all object URLs to prevent memory leaks
  for (const [nodeName, { objectUrl }] of chartCache) {
    URL.revokeObjectURL(objectUrl);
  }
  chartCache.clear();
  console.log("Chart cache cleared");
}

// Helper functions for tooltips (defined early to avoid hoisting issues)
function fmt(ts) {
  if (!ts && ts !== 0) return "-";
  try {
    const d = new Date(ts * 1000);
    return d.toLocaleString();
  } catch { return "-"; }
}

function buildTooltipText(nodeName, info) {
  const status = (info && info.status) ? String(info.status).toLowerCase() : 'pending';
  
  // For cached steps, use cached timing if available
  let started, ended, dur;
  if (status === 'cached' && info && info.cached_started_at !== undefined) {
    started = fmt(info.cached_started_at);
    ended = fmt(info.cached_ended_at);
    dur = (typeof info.cached_execution_time === 'number') ? `${info.cached_execution_time.toFixed(2)}s` : '-';
  } else {
    started = fmt(info && info.started_at);
    ended = fmt(info && info.ended_at);
    dur = (info && typeof info.duration_sec === 'number') ? `${info.duration_sec.toFixed(2)}s` : '-';
  }
  
  if (status === 'cached' && info && info.cached_run_id) {
    return `${nodeName}\nStatus: ${status}\nCached from run: ${info.cached_run_id}\nStarted: ${started}\nEnded: ${ended}\nTime taken: ${dur}`;
  } else {
    return `${nodeName}\nStatus: ${status}\nStarted: ${started}\nEnded: ${ended}\nTime taken: ${dur}`;
  }
}

// ---- Run ID ordering helpers (ensure oldest is #1) ----
function extractRunTimestamp(runId) {
  try {
    const s = String(runId || "");
    const m = s.match(/-(\d{14})-/);
    if (m && m[1]) return Number(m[1]);
  } catch {}
  return null;
}

function sortRunsOldestFirst(list) {
  try {
    const arr = Array.from(list || []);
    const decorated = arr.map(r => ({ id: r, ts: extractRunTimestamp(r) }));
    decorated.sort((a, b) => {
      const at = a.ts, bt = b.ts;
      if (typeof at === 'number' && typeof bt === 'number') return at - bt;
      if (typeof at === 'number') return -1;
      if (typeof bt === 'number') return 1;
      return String(a.id).localeCompare(String(b.id));
    });
    return decorated.map(d => d.id);
  } catch {
    return Array.from(list || []);
  }
}

async function loadProjects() {
  const data = await fetchJSON(`${API_BASE}/projects`);
  const projects = data.projects || [];
  elProject.innerHTML = "";
  for (const p of projects) {
    const opt = document.createElement("option");
    opt.value = p; opt.textContent = p; elProject.appendChild(opt);
  }
  if (projects.length) {
    elProject.value = projects[0];
  }
}

async function loadRuns(projectId) {
  console.log("loadRuns: projectId=", projectId);
  const data = await fetchJSON(`${API_BASE}/projects/${encodeURIComponent(projectId)}/runs`);
  console.log("loadRuns: data=", data);
  const runs = data.runs || [];
  console.log("loadRuns: runs count=", runs.length, runs);
  runsCache = sortRunsOldestFirst(runs);
  renderRunList(runsCache);
  if (runsCache.length) {
    current.runId = runsCache[runsCache.length - 1];
    selectRunInList(current.runId);
    console.log("loadRuns: selected run=", current.runId);
  } else {
    console.log("loadRuns: no runs found");
    current.runId = null;
  }
}

function renderRunList(runs) {
  if (!elRunList) return;
  elRunList.innerHTML = "";
  runs.forEach((runId, idx) => {
    const li = document.createElement('li');
    li.className = 'run-list-item';
    li.dataset.runId = String(runId);
    li.textContent = `${idx + 1}. ${runId}`;
    if (current.runId === runId) li.classList.add('selected');
    li.addEventListener('click', async () => {
      if (current.runId === runId) return;
      current.runId = runId;
      requestGen++;
      lastStatusMap = {};
      emptyStatusStreak = 0;
      
      // Clear chart cache for new run
      clearChartCache();
      
      selectRunInList(runId);
      startPolling();
      await loadDynamicCharts();
    });
    elRunList.appendChild(li);
  });
}

function selectRunInList(runId) {
  if (!elRunList) return;
  Array.from(elRunList.children).forEach((li) => {
    if (li.dataset && li.dataset.runId === String(runId)) li.classList.add('selected');
    else li.classList.remove('selected');
  });
}

async function loadGraph(projectId, initialStatusMap = {}, initialInfoMap = {}) {
  const localGen = requestGen;
  const g = await fetchJSON(`${API_BASE}/projects/${encodeURIComponent(projectId)}/graph`);
  if (localGen !== requestGen) return; // Stale response, ignore
  graphData = g;
  layoutGraph();
  if (localGen !== requestGen) return; // Stale after layout, ignore
  renderGraph(initialStatusMap, initialInfoMap);
}

function layoutGraph() {
  const nodes = graphData.nodes || [];
  const indeg = graphData.indeg || {};
  const adj = graphData.adj || {};
  // Layering based on longest-path topological ranks: child layer >= max(parent layer + 1)
  const indegWork = {};
  for (const n of nodes) indegWork[n] = Math.max(0, indeg[n] || 0);
  const queue = [];
  const layerOf = {};
  for (const n of nodes) {
    if ((indegWork[n] || 0) === 0) { queue.push(n); layerOf[n] = 0; }
  }
  const topoOrder = [];
  while (queue.length) {
    const u = queue.shift();
    topoOrder.push(u);
    const base = (layerOf[u] || 0) + 1;
    for (const v of (adj[u] || [])) {
      if (layerOf[v] === undefined || base > layerOf[v]) layerOf[v] = base;
      indegWork[v] = (indegWork[v] || 0) - 1;
      if (indegWork[v] <= 0) queue.push(v);
    }
  }
  // Any remaining nodes (in case of isolated/cyclic) fallback to 0
  for (const n of nodes) if (layerOf[n] === undefined) layerOf[n] = 0;
  // Group by layer, keeping topo order inside each layer
  const orderIndex = {};
  topoOrder.forEach((n, i) => { orderIndex[n] = i; });
  const layers = new Map();
  for (const n of nodes) {
    const d = Math.max(0, layerOf[n] || 0);
    if (!layers.has(d)) layers.set(d, []);
    layers.get(d).push(n);
  }
  for (const [d, arr] of layers) {
    arr.sort((a, b) => (orderIndex[a] || 0) - (orderIndex[b] || 0));
  }
  // Assign positions with small outer margins and full stretch
  positions = {};
  const width = svg.clientWidth || 1000;
  const height = svg.clientHeight || 600;
  const layerCount = layers.size || 1;
  const marginX = 12;
  const marginY = 12;
  const innerW = Math.max(100, width - 2 * marginX);
  const innerH = Math.max(100, height - 2 * marginY);
  // Use more of the canvas while preserving small outer margins
  const scaleH = 0.95; // horizontal scale (0-1]
  const scaleV = 0.90; // vertical scale (0-1]
  const usableW = innerW * scaleH;
  const usableH = innerH * scaleV;
  const offsetX = marginX + (innerW - usableW) / 2;
  const offsetY = marginY + (innerH - usableH) / 2;
  const vStep = (layerCount > 1) ? usableH / (layerCount - 1) : usableH / 2;
  for (const [d, arr] of layers.entries()) {
    const count = arr.length || 1;
    const hStep = (count > 1) ? usableW / count : usableW;
    arr.forEach((n, i) => {
      const x = (count > 1)
        ? (offsetX + (i + 0.5) * hStep)
        : (offsetX + usableW / 2);
      const y = offsetY + d * vStep;
      positions[n] = { x, y };
    });
  }
  // Fallback for nodes not reached
  const remaining = nodes.filter(n => !(n in positions));
  remaining.forEach((n, i) => {
    positions[n] = { x: offsetX + 40 + i * 90, y: offsetY + usableH + 40 };
  });
}

function clearSVG() {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
}

function renderGraph(statusMap = {}, infoMap = {}) {
  clearSVG();
  const adj = graphData.adj || {};
  // Draw links
  for (const [u, vs] of Object.entries(adj)) {
    for (const v of vs) {
      const a = positions[u], b = positions[v];
      if (!a || !b) continue;
      const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
      line.setAttribute("x1", a.x);
      line.setAttribute("y1", a.y);
      line.setAttribute("x2", b.x);
      line.setAttribute("y2", b.y);
      line.setAttribute("class", "link");
      svg.appendChild(line);
    }
  }
  // Draw nodes
  for (const n of graphData.nodes || []) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const p = positions[n];
    const st = (statusMap[n] || "pending").toLowerCase();
    const isChart = chartNodes.has(n);
    g.setAttribute("class", `node status-${st}${isChart ? ' clickable' : ''}`);
    if (isChart) {
      const size = 26;
      const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      rect.setAttribute("x", String(p.x - size / 2));
      rect.setAttribute("y", String(p.y - size / 2));
      rect.setAttribute("width", String(size));
      rect.setAttribute("height", String(size));
      rect.setAttribute("rx", "6");
      rect.setAttribute("ry", "6");
      g.appendChild(rect);
    } else {
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      c.setAttribute("cx", p.x);
      c.setAttribute("cy", p.y);
      c.setAttribute("r", "12");
      g.appendChild(c);
    }
    // Spinner arc for running
    if (st === "running") {
      const arc = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      arc.setAttribute("cx", p.x);
      arc.setAttribute("cy", p.y);
      arc.setAttribute("r", "10");
      arc.setAttribute("fill", "none");
      arc.setAttribute("class", "spinner");
      g.appendChild(arc);
    }
    const t = document.createElementNS("http://www.w3.org/2000/svg", "text");
    t.setAttribute("x", p.x);
    t.setAttribute("y", p.y - 18);
    t.setAttribute("text-anchor", "middle");
    t.textContent = n;
    g.appendChild(t);

    // For cached nodes, draw a small numeric badge indicating the source run index
    try {
      const info = infoMap[n] || {};
      if (st === "cached" && info && info.cached_run_id) {
        const srcId = String(info.cached_run_id);
        const idx = runsCache.indexOf(srcId);
        if (idx !== -1) {
          const badge = document.createElementNS("http://www.w3.org/2000/svg", "text");
          badge.setAttribute("x", String(p.x - 16));
          badge.setAttribute("y", String(p.y + 16));
          badge.setAttribute("text-anchor", "start");
          badge.setAttribute("class", "node-cached-index");
          badge.textContent = String(idx + 1);
          g.appendChild(badge);
        }
      }
    } catch {}

    // Custom tooltip hover
    g.addEventListener("mousemove", (ev) => showTooltip(n, ev.clientX, ev.clientY));
    g.addEventListener("mouseleave", hideTooltip);
    // Open modal on click for chart nodes
    if (isChart) {
      g.addEventListener("click", () => { openChartModal(n); });
    }
    svg.appendChild(g);
  }
}

// ---- Status Smoothing (no-downgrade merge) ----
function normalizeStatus(s) {
  const v = String(s || 'pending').toLowerCase();
  if (v === 'completed' || v === 'cached' || v === 'failed' || v === 'running') return v;
  return 'pending';
}

function mergeStatusMaps(prev = {}, next = {}) {
  // Status precedence with a guard: do not promote running -> cached mid-run.
  // This avoids the brief blue flash when some steps report cached while the
  // overall process is still executing. We'll keep nodes orange (running)
  // until a terminal state (completed/failed) arrives.
  const rank = { completed: 4, failed: 4, running: 3, cached: 3, pending: 0 };
  const out = {};
  const nodes = (graphData && Array.isArray(graphData.nodes)) ? graphData.nodes : [];
  for (const n of nodes) {
    const p = normalizeStatus(prev[n]);
    let q = normalizeStatus(next[n]);
    // Special-case: prevent upgrading from running to cached during execution
    if (p === 'running' && q === 'cached') {
      out[n] = 'running';
      continue;
    }
    // Only upgrade on strictly higher precedence to avoid oscillation
    out[n] = (rank[q] > rank[p]) ? q : p;
  }
  return out;
}

async function pollStatus() {
  if (!current.project || !current.runId) return;
  try {
    const localGen = requestGen;
    const data = await fetchJSON(`${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(current.runId)}/status`);
    if (localGen !== requestGen) return; // Stale response, ignore
    elStatus.textContent = data.status || "unknown";
    const proc = data.process_status || {};
    const info = data.process_info || {};
    lastProcessInfo = info;
    // Detect if backend returned no process statuses repeatedly (e.g., project/run missing)
    if (proc && Object.keys(proc).length > 0) {
      emptyStatusStreak = 0;
      // Merge with last known to prevent transient downgrades (e.g., missing -> pending)
      const merged = mergeStatusMaps(lastStatusMap, proc);
      lastStatusMap = merged;
      renderGraph(merged, info);
    } else {
      emptyStatusStreak += 1;
      // If we observe empty process map for 2+ consecutive polls, clear cache to avoid stale green
      if (emptyStatusStreak >= 2) {
        lastStatusMap = {};
      }
      renderGraph(lastStatusMap, info);
    }
    
    // Update tooltip if currently visible for a node
    if (tooltipEl && tooltipEl.style.display === 'block' && tooltipEl.dataset.nodeName) {
      const nodeName = tooltipEl.dataset.nodeName;
      const nodeInfo = info[nodeName] || {};
      const tooltipText = buildTooltipText(nodeName, nodeInfo);
      const lines = tooltipText.split('\n');
      tooltipEl.innerHTML = lines.map(line => `<div>${line}</div>`).join('');
    }
    
    // Pre-load charts for completed chart nodes
    for (const nodeName of graphData.nodes || []) {
      const status = (merged[nodeName] || "pending").toLowerCase();
      const isChart = chartNodes.has(nodeName);
      
      // Pre-load if it's a chart node and is completed/cached
      if (isChart && (status === "completed" || status === "cached")) {
        preloadChartForNode(nodeName);
      }
    }
  } catch (e) {
    // ignore errors to keep polling
  }
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(pollStatus, 2000);
  pollStatus();
}

function startRunPolling() {
  if (runPollTimer) clearInterval(runPollTimer);
  runPollTimer = setInterval(async () => {
    if (!current.project) return;
    try {
      const data = await fetchJSON(`${API_BASE}/projects/${encodeURIComponent(current.project)}/runs`);
      const runs = data.runs || [];
      const normalized = sortRunsOldestFirst(runs);
      // Merge with existing list to preserve current order and append new items at bottom
      const existing = runsCache;
      const different = normalized.length !== existing.length || normalized.some((r, i) => existing[i] !== r);
      if (different) {
        const prev = current.runId;
        // Preserve existing order for items that still exist; append any new ones
        const incomingSet = new Set(normalized);
        const kept = existing.filter(r => incomingSet.has(r));
        const keptSet = new Set(kept);
        const added = normalized.filter(r => !keptSet.has(r));
        runsCache = kept.concat(added);
        renderRunList(runsCache);
        if (normalized.includes(prev)) {
          current.runId = prev;
          selectRunInList(prev);
        } else if (normalized.length) {
          current.runId = normalized[normalized.length - 1];
          selectRunInList(current.runId);
          // Reset chart and status state and reload dynamic charts for the new run
          requestGen++;
          lastStatusMap = {};
          emptyStatusStreak = 0;
          clearChartCache();
          startPolling();
      try { 
        // Close stale chart modal, if any
        if (isModalOpen) closeChartModal();
        await loadDynamicCharts(); 
      } catch {}
        }
        else {
          // No runs left – clear run and hide dynamic charts
          current.runId = null;
          selectRunInList(null);
          requestGen++;
          lastStatusMap = {};
          emptyStatusStreak = 0;
          clearChartCache();
          if (pollTimer) clearInterval(pollTimer);
      try { 
        if (isModalOpen) closeChartModal();
        await loadDynamicCharts(); 
      } catch {}
        }
      }
    } catch (e) {
      // ignore
    }
  }, 5000);
}

elProject.addEventListener("change", async () => {
  console.log("Project changed to:", elProject.value);
  current.project = elProject.value;
  // Invalidate any in-flight async work from previous project
  requestGen++;
  
  // Clear previous project state to avoid flickering
  clearSVG();
  graphData = { nodes: [], adj: {}, indeg: {} };
  positions = {};
  lastProcessInfo = {};
  lastStatusMap = {};
  emptyStatusStreak = 0;
  hideTooltip();
  if (pollTimer) clearInterval(pollTimer);
  if (runPollTimer) clearInterval(runPollTimer);
  
  // Clear chart cache for new project
  clearChartCache();
  
  // Immediately clear current run and hide any dynamic charts to avoid stale display
  current.runId = null;
  try {
    if (isModalOpen) closeChartModal();
    await loadDynamicCharts();
  } catch {}
  
  
  await loadRuns(current.project);
  // current.runId set by loadRuns
  console.log("After loading runs, runId:", current.runId);
  
  // Fetch initial status before rendering to avoid color flickering
  let initialStatusMap = {};
  let initialInfoMap = {};
  if (current.runId) {
    try {
      const data = await fetchJSON(`${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(current.runId)}/status`);
      initialStatusMap = data.process_status || {};
      initialInfoMap = data.process_info || {};
      lastProcessInfo = initialInfoMap;
      // Seed lastStatusMap with initial merged values
      lastStatusMap = mergeStatusMaps({}, initialStatusMap);
      emptyStatusStreak = 0;
    } catch (e) {
      console.log("Could not fetch initial status, will use defaults");
      lastStatusMap = {};
      emptyStatusStreak = 0;
    }
  }
  // Determine chart nodes from chart-config
  try {
    const configUrl = `${API_BASE}/projects/${encodeURIComponent(current.project)}/chart-config`;
    const configData = await fetchJSON(configUrl);
    const charts = configData.charts || [];
    chartNodes = new Set(charts.map(c => c.name));
  } catch (e) {
    chartNodes = new Set();
  }
  
  await loadGraph(current.project, lastStatusMap, initialInfoMap);
  startPolling();
  startRunPolling();
  startDynamicChartsAutoload();
});

// Run selection handled by sidebar list clicks

// -------- Modal Event Listeners ---------
// Close modal when close button is clicked
if (elChartModalClose) {
  elChartModalClose.addEventListener('click', closeChartModal);
}

// Close modal when clicking outside the modal content
if (elChartModal) {
  elChartModal.addEventListener('click', (event) => {
    if (event.target === elChartModal) {
      closeChartModal();
    }
  });
}

// Close modal with Escape key
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && isModalOpen) {
    closeChartModal();
  }
});

(async function init() {
  console.log("=== INIT START ===");
  await loadProjects();
  current.project = elProject.value || null;
  console.log("Current project:", current.project);
  if (current.project) {
    await loadRuns(current.project);
    console.log("Current runId:", current.runId);
    
    // Fetch initial status before rendering to avoid color flickering
    let initialStatusMap = {};
    let initialInfoMap = {};
    if (current.runId) {
      try {
        const data = await fetchJSON(`${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(current.runId)}/status`);
        initialStatusMap = data.process_status || {};
        initialInfoMap = data.process_info || {};
        lastProcessInfo = initialInfoMap;
        lastStatusMap = mergeStatusMaps({}, initialStatusMap);
      } catch (e) {
        console.log("Could not fetch initial status, will use defaults");
        lastStatusMap = {};
      }
    }
    // Determine chart nodes from chart-config
    try {
      const configUrl = `${API_BASE}/projects/${encodeURIComponent(current.project)}/chart-config`;
      const configData = await fetchJSON(configUrl);
      const charts = configData.charts || [];
      chartNodes = new Set(charts.map(c => c.name));
    } catch (e) {
      chartNodes = new Set();
    }
    
    await loadGraph(current.project, lastStatusMap, initialInfoMap);
    startPolling();
    startRunPolling();
    startDynamicChartsAutoload();
  } else {
    console.log("No project selected, skipping initialization");
  }
  console.log("=== INIT COMPLETE ===");
})();

// Tooltip rendering using process_info from last poll
let lastProcessInfo = {};

function showTooltip(nodeName, x, y) {
  const info = lastProcessInfo[nodeName] || {};
  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'tooltip';
    document.body.appendChild(tooltipEl);
  }
  
  const tooltipText = buildTooltipText(nodeName, info);
  const lines = tooltipText.split('\n');
  
  tooltipEl.innerHTML = lines.map(line => `<div>${line}</div>`).join('');
  tooltipEl.style.left = (x + 12) + 'px';
  tooltipEl.style.top = (y + 12) + 'px';
  tooltipEl.style.display = 'block';
  // Store current node so we can update it on poll
  tooltipEl.dataset.nodeName = nodeName;
}

function hideTooltip() {
  if (tooltipEl) tooltipEl.style.display = 'none';
}

// -------- Chart Modal Functions ---------
async function openChartModal(nodeName) {
  if (!current.project || !current.runId) {
    console.log("openChartModal: No project or runId");
    return;
  }
  
  console.log(`openChartModal: Opening modal for node: ${nodeName}`);
  
  // Clear any existing polling
  if (chartModalPollTimer) {
    clearInterval(chartModalPollTimer);
    chartModalPollTimer = null;
  }
  
  // Show modal
  if (elChartModal) {
    elChartModal.classList.remove('hidden');
    isModalOpen = true;
  }
  
  // Clear image src to prevent flash of previous chart
  if (elChartModalImage) {
    elChartModalImage.src = '';
    elChartModalImage.style.display = 'none';
  }
  
  // Check cache first
  if (chartCache.has(nodeName)) {
    console.log(`Chart for ${nodeName} found in cache, displaying immediately`);
    const { objectUrl } = chartCache.get(nodeName);
    if (elChartModalImage) {
      elChartModalImage.src = objectUrl;
      elChartModalImage.style.display = 'block';
    }
    if (elChartModalMessage) {
      elChartModalMessage.style.display = 'none';
    }
    return;
  }
  
  // Show loading message if not cached
  if (elChartModalMessage) {
    elChartModalMessage.textContent = 'Loading chart...';
    elChartModalMessage.style.display = 'block';
  }
  
  // Try to fetch and display the chart
  await tryLoadChartForNode(nodeName);
}

async function tryLoadChartForNode(nodeName) {
  try {
    // Check if this node is cached and has a cached_run_id
    const nodeInfo = lastProcessInfo[nodeName] || {};
    const nodeStatus = (lastStatusMap[nodeName] || "pending").toLowerCase();
    const cachedRunId = (nodeStatus === "cached" && nodeInfo.cached_run_id) ? nodeInfo.cached_run_id : null;
    
    // Use cached run ID if available, otherwise current run ID
    const runIdToFetch = cachedRunId || current.runId;
    
    // Fetch chart data for the target run
    const url = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(runIdToFetch)}/charts`;
    console.log(`Fetching charts from: ${url} (${cachedRunId ? 'cached run' : 'current run'})`);
    const data = await fetchJSON(url);
    const charts = data.charts || {};
    
    // Look for chart items matching the node name
    let chartItem = null;
    for (const [chartName, chartInfo] of Object.entries(charts)) {
      if (chartName === nodeName && chartInfo.items && chartInfo.items.length > 0) {
        chartItem = chartInfo.items[0]; // Take the first item
        break;
      }
    }
    
    if (chartItem && chartItem.object_path) {
      // Chart is available, fetch and display it
      console.log(`Found chart for ${nodeName}:`, chartItem);
      await loadChartImage(chartItem, runIdToFetch);
      
      // Clear polling since we found the chart
      if (chartModalPollTimer) {
        clearInterval(chartModalPollTimer);
        chartModalPollTimer = null;
      }
    } else {
      // Chart not available yet, set up polling
      console.log(`Chart not yet available for ${nodeName}, setting up polling`);
      if (elChartModalMessage) {
        elChartModalMessage.textContent = `Chart for "${nodeName}" is not yet available.`;
        elChartModalMessage.style.display = 'block';
      }
      
      // Start polling every 3 seconds
      chartModalPollTimer = setInterval(async () => {
        if (!isModalOpen) {
          clearInterval(chartModalPollTimer);
          chartModalPollTimer = null;
          return;
        }
        await tryLoadChartForNode(nodeName);
      }, 3000);
    }
  } catch (error) {
    console.error(`Error loading chart for ${nodeName}:`, error);
    if (elChartModalMessage) {
      elChartModalMessage.textContent = `Error loading chart: ${error.message}`;
      elChartModalMessage.style.display = 'block';
    }
  }
}

async function loadChartImage(chartItem, runIdToFetch) {
  try {
    const params = new URLSearchParams();
    if (chartItem.object_path) params.set('uri', chartItem.object_path);
    if (chartItem.cache_path) params.set('cache_path', chartItem.cache_path);
    
    // Use the provided runId or fallback to current.runId
    const targetRunId = runIdToFetch || current.runId;
    
    const fetchUrl = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(targetRunId)}/charts/fetch?` + params.toString();
    console.log(`Fetching chart image from: ${fetchUrl}`);
    
    const resp = await fetch(fetchUrl);
    if (!resp.ok) {
      throw new Error(`Chart fetch failed: ${resp.status}`);
    }
    
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    
    if (elChartModalImage) {
      elChartModalImage.src = url;
      elChartModalImage.style.display = 'block';
    }
    if (elChartModalMessage) {
      elChartModalMessage.style.display = 'none';
    }
    
    console.log("Chart image loaded successfully");
  } catch (error) {
    console.error("Error loading chart image:", error);
    if (elChartModalMessage) {
      elChartModalMessage.textContent = `Error loading chart image: ${error.message}`;
      elChartModalMessage.style.display = 'block';
    }
  }
}

function closeChartModal() {
  console.log("closeChartModal: Closing modal");
  
  // Clear polling timer
  if (chartModalPollTimer) {
    clearInterval(chartModalPollTimer);
    chartModalPollTimer = null;
  }
  
  // Hide modal
  if (elChartModal) {
    elChartModal.classList.add('hidden');
    isModalOpen = false;
  }
  
  // Clear image and message
  if (elChartModalImage) {
    elChartModalImage.src = '';
    elChartModalImage.style.display = 'none';
  }
  if (elChartModalMessage) {
    elChartModalMessage.style.display = 'none';
  }
}

// -------- Dynamic Charts ---------
async function loadDynamicCharts() {
  // Clean up existing dynamic charts
  dynamicChartCleanups.forEach(cleanup => cleanup());
  dynamicChartCleanups = [];
  if (elDynamicChartsGrid) elDynamicChartsGrid.innerHTML = '';
  if (elDynamicChartsContainer) elDynamicChartsContainer.style.display = 'none';
  dynamicChartsInitialized = false;
  
  if (!current.project || !current.runId) {
    dynamicChartsInitialized = false;
    return;
  }
  
  try {
    // Fetch chart configuration from project
    const configUrl = `${API_BASE}/projects/${encodeURIComponent(current.project)}/chart-config`;
    const configData = await fetchJSON(configUrl);
    console.log('Chart config:', configData);
    
    const charts = configData.charts || [];
    const entrypoint = configData.entrypoint;
    
    // Filter for dynamic charts
    const dynamicCharts = charts.filter(c => c.type === 'dynamic');
    
    if (dynamicCharts.length === 0) {
      dynamicChartsInitialized = false;
      return;
    }
    
    // Show dynamic charts container
    if (elDynamicChartsContainer) elDynamicChartsContainer.style.display = 'block';
    
    // Load user chart definitions if entrypoint exists
    if (entrypoint) {
      try {
        // Dynamically import user chart file at /projects/<id>/charts/*.js
        const chartModulePath = '/' + entrypoint; // e.g., /projects/titanic/charts/plot_metrics.js
        console.log('Loading user charts from:', chartModulePath);
        await import(chartModulePath);
        console.log('User charts loaded successfully');
      } catch (error) {
        console.error('Failed to load user chart file:', error);
        elDynamicChartsGrid.innerHTML = `<div class="chart-error">Failed to load chart definitions: ${error.message}</div>`;
        dynamicChartsInitialized = false;
        return;
      }
    }
    
    // Render each dynamic chart
    for (const chartConfig of dynamicCharts) {
      const chartDiv = document.createElement('div');
      chartDiv.className = 'dynamic-chart-item';
      chartDiv.innerHTML = `<h4>${chartConfig.name}</h4><div class="chart-canvas-container"></div>`;
      if (elDynamicChartsGrid) elDynamicChartsGrid.appendChild(chartDiv);
      const canvasContainer = chartDiv.querySelector('.chart-canvas-container');
      
      try {
        const cleanup = renderDynamicChart(
          current.project,
          current.runId,
          chartConfig.name,
          chartConfig,
          canvasContainer,
          API_BASE
        );
        dynamicChartCleanups.push(cleanup);
      } catch (error) {
        console.error(`Failed to render chart ${chartConfig.name}:`, error);
        canvasContainer.innerHTML = `<div class="chart-error">Error: ${error.message}</div>`;
      }
    }
    // Mark initialized after attempting to render at least one chart
    dynamicChartCleanups.length > 0 ? (dynamicChartsInitialized = true) : (dynamicChartsInitialized = false);
  } catch (error) {
    console.error('Error loading dynamic charts:', error);
    dynamicChartsInitialized = false;
  }
}

// -------- Charts (KV-backed) ---------
async function refreshCharts() {
  if (!current.project || !current.runId) {
    console.log("refreshCharts: No project or runId");
    return;
  }
  console.log(`refreshCharts: project=${current.project}, runId=${current.runId}`);
  
  // Load dynamic charts
  await loadDynamicCharts();
  
  // Load static charts (existing logic)
  try {
    const url = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(current.runId)}/charts`;
    console.log(`Fetching charts from: ${url}`);
    const data = await fetchJSON(url);
    console.log("Charts response:", data);
    const charts = data.charts || {};
    const candidates = [];
    for (const [name, info] of Object.entries(charts)) {
      const items = (info && info.items) || [];
      for (const it of items) {
        candidates.push({
          label: `${name}/${it.title}`,
          uri: it.object_path || '',
          cache_path: it.cache_path || ''
        });
      }
    }
    console.log(`Found ${candidates.length} chart candidates:`, candidates);
    elChartSelect.innerHTML = "";
    for (const c of candidates) {
      const opt = document.createElement("option");
      opt.value = JSON.stringify({ uri: c.uri, cache_path: c.cache_path });
      opt.textContent = c.label; elChartSelect.appendChild(opt);
    }
    if (candidates.length) {
      elChartSelect.value = JSON.stringify({ uri: candidates[0].uri, cache_path: candidates[0].cache_path });
      console.log("Loading first chart...");
      await loadChart(JSON.parse(elChartSelect.value));
      // Show image, hide empty message
      if (elChartImage) elChartImage.style.display = '';
      if (elChartEmptyMessage) elChartEmptyMessage.style.display = 'none';
    } else {
      console.log("No charts found");
      if (elChartImage) {
        elChartImage.src = "";
        elChartImage.style.display = 'none';
      }
      if (elChartEmptyMessage) {
        elChartEmptyMessage.textContent = 'No charts currently';
        elChartEmptyMessage.style.display = 'block';
      }
    }
  } catch (e) {
    console.error("Error refreshing charts:", e);
    if (elChartImage) {
      elChartImage.src = "";
      elChartImage.style.display = 'none';
    }
    if (elChartEmptyMessage) {
      elChartEmptyMessage.textContent = 'No charts currently';
      elChartEmptyMessage.style.display = 'block';
    }
  }
}

// Periodic static charts refresh (preserve current selection)
async function refreshStaticChartsList() {
  if (!current.project || !current.runId) return;
  try {
    const url = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(current.runId)}/charts`;
    const data = await fetchJSON(url);
    const charts = data.charts || {};
    const candidates = [];
    for (const [name, info] of Object.entries(charts)) {
      const items = (info && info.items) || [];
      for (const it of items) {
        candidates.push({
          label: `${name}/${it.title} (${info.type || 'static'})`,
          uri: it.object_path || '',
          cache_path: it.cache_path || ''
        });
      }
    }

    // Preserve current selection if still available
    const prev = elChartSelect.value;
    const prevSet = new Set(candidates.map(c => JSON.stringify({ uri: c.uri, cache_path: c.cache_path })));

    // Rebuild options
    elChartSelect.innerHTML = "";
    for (const c of candidates) {
      const opt = document.createElement("option");
      opt.value = JSON.stringify({ uri: c.uri, cache_path: c.cache_path });
      opt.textContent = c.label; elChartSelect.appendChild(opt);
    }

    if (prev && prevSet.has(prev)) {
      elChartSelect.value = prev;
      // Do not reload image to avoid flicker; user can switch manually
      if (elChartImage) elChartImage.style.display = '';
      if (elChartEmptyMessage) elChartEmptyMessage.style.display = 'none';
    } else if (!prev && candidates.length) {
      // No previous selection; select first and load once
      elChartSelect.value = JSON.stringify({ uri: candidates[0].uri, cache_path: candidates[0].cache_path });
      await loadChart(JSON.parse(elChartSelect.value));
      if (elChartImage) elChartImage.style.display = '';
      if (elChartEmptyMessage) elChartEmptyMessage.style.display = 'none';
    } else if (prev && !prevSet.has(prev)) {
      // Previous selection disappeared; keep current image but set first option
      if (candidates.length) {
        elChartSelect.value = JSON.stringify({ uri: candidates[0].uri, cache_path: candidates[0].cache_path });
        if (elChartImage) elChartImage.style.display = '';
        if (elChartEmptyMessage) elChartEmptyMessage.style.display = 'none';
      } else {
        if (elChartImage) {
          elChartImage.src = "";
          elChartImage.style.display = 'none';
        }
        if (elChartEmptyMessage) {
          elChartEmptyMessage.textContent = 'No charts currently';
          elChartEmptyMessage.style.display = 'block';
        }
      }
    }
  } catch (e) {
    // Ignore transient errors
  }
}

function startStaticChartsPolling() {
  if (staticChartsPollTimer) clearInterval(staticChartsPollTimer);
  staticChartsPollTimer = setInterval(() => {
    if (!current.project || !current.runId) return;
    refreshStaticChartsList();
  }, 10000);
}

function startDynamicChartsAutoload() {
  if (dynamicChartsInitTimer) clearInterval(dynamicChartsInitTimer);
  dynamicChartsInitTimer = setInterval(async () => {
    if (!current.project || !current.runId) return;
    if (dynamicChartsInitialized) {
      clearInterval(dynamicChartsInitTimer);
      dynamicChartsInitTimer = null;
      return;
    }
    await loadDynamicCharts();
    if (dynamicChartsInitialized) {
      clearInterval(dynamicChartsInitTimer);
      dynamicChartsInitTimer = null;
    }
  }, 3000);
}

elChartSelect.addEventListener('change', async () => {
  try {
    const ref = JSON.parse(elChartSelect.value);
    await loadChart(ref);
  } catch {
    // ignore
  }
});

async function loadChart(ref) {
  if (!ref) { 
    console.log("loadChart: No ref provided");
    if (elChartImage) {
      elChartImage.src = "";
      elChartImage.style.display = 'none';
    }
    if (elChartEmptyMessage) {
      elChartEmptyMessage.textContent = 'No charts currently';
      elChartEmptyMessage.style.display = 'block';
    }
    return; 
  }
  console.log("loadChart: ref=", ref);
  try {
    const params = new URLSearchParams();
    if (ref.uri) params.set('uri', ref.uri);
    if (ref.cache_path) params.set('cache_path', ref.cache_path);
    const fetchUrl = `${API_BASE}/projects/${encodeURIComponent(current.project)}/runs/${encodeURIComponent(current.runId)}/charts/fetch?` + params.toString();
    console.log(`Fetching chart from: ${fetchUrl}`);
    const resp = await fetch(fetchUrl);
    console.log(`Chart fetch response: status=${resp.status}, content-type=${resp.headers.get('content-type')}`);
    if (!resp.ok) {
      const text = await resp.text();
      console.error(`Chart fetch failed: ${resp.status} ${text}`);
      throw new Error(`fetch failed: ${resp.status}`);
    }
    const blob = await resp.blob();
    console.log(`Chart blob size: ${blob.size} bytes`);
    const url = URL.createObjectURL(blob);
    elChartImage.src = url;
    if (elChartImage) elChartImage.style.display = '';
    if (elChartEmptyMessage) elChartEmptyMessage.style.display = 'none';
    console.log("Chart loaded successfully");
  } catch (e) {
    console.error("Error loading chart:", e);
    if (elChartImage) {
      elChartImage.src = "";
      elChartImage.style.display = 'none';
    }
    if (elChartEmptyMessage) {
      elChartEmptyMessage.textContent = 'No charts currently';
      elChartEmptyMessage.style.display = 'block';
    }
  }
}


