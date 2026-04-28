/* ===== NexaChain — main.js ===== */

const API = "http://127.0.0.1:5000/api";

// ─────────────────────────────────────────────
//  Clock
// ─────────────────────────────────────────────
function updateClock() {
  const now = new Date();
  document.getElementById("clock").textContent =
    now.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
}
setInterval(updateClock, 1000);
updateClock();

// ─────────────────────────────────────────────
//  Toast
// ─────────────────────────────────────────────
const ICONS = {
  success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>`,
  warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>`,
  info:    `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
};

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon">${ICONS[type] || ICONS.info}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = "toastOut 0.3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ─────────────────────────────────────────────
//  Page Navigation
// ─────────────────────────────────────────────
const PAGE_TITLES = {
  driver:   "Driver Dashboard",
  tracking: "Customer Tracking",
  admin:    "Admin Panel",
};

function showPage(name) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById(`page-${name}`).classList.add("active");
  document.getElementById(`nav-${name}`).classList.add("active");
  document.getElementById("page-title").textContent = PAGE_TITLES[name] || name;

  if (name === "driver")   loadDriverPage();
  if (name === "admin")    loadAdminPage();
}

// ─────────────────────────────────────────────
//  Sidebar (mobile)
// ─────────────────────────────────────────────
function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
  document.getElementById("sidebar-overlay").classList.toggle("open");
}
function closeSidebar() {
  document.getElementById("sidebar").classList.remove("open");
  document.getElementById("sidebar-overlay").classList.remove("open");
}

// ─────────────────────────────────────────────
//  ─── DRIVER DASHBOARD ───
// ─────────────────────────────────────────────
async function loadDriverPage() {
  try {
    const [statsRes, tasksRes] = await Promise.all([
      fetch(`${API}/driver/stats`),
      fetch(`${API}/driver/tasks`),
    ]);
    const stats = await statsRes.json();
    const tasks = await tasksRes.json();
    renderDriverStats(stats);
    renderTasks(tasks);
  } catch (e) {
    showToast("Could not load driver data", "warning");
  }
}

function renderDriverStats(s) {
  document.getElementById("ds-deliveries").textContent = s.today_deliveries;
  document.getElementById("ds-completed").textContent  = s.completed;
  document.getElementById("ds-distance").textContent   = s.distance_km;
  document.getElementById("ds-accuracy").textContent   = s.eta_accuracy + "%";
}

function renderTasks(tasks) {
  const el = document.getElementById("task-list");
  el.innerHTML = tasks.map(t => `
    <div class="task-item ${!t.done && t.num === 2 ? 'active-task' : ''}">
      <div class="task-header">
        <div class="task-num ${t.done ? 'done' : ''}">${t.done ? "✓" : t.num}</div>
        <span class="task-id">${t.id}</span>
        ${!t.done ? `<button class="btn btn-sm btn-success" onclick="completeTask('${t.id}')">Complete</button>` : `<span style="font-size:11px;color:#16A34A;font-weight:700;">DONE</span>`}
      </div>
      <div class="task-detail">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/></svg>
        <span>${t.address}</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
        <span>${t.weight}</span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        <span>${t.time}</span>
      </div>
    </div>
  `).join("");
}

async function completeTask(taskId) {
  try {
    const res = await fetch(`${API}/driver/complete/${taskId}`, { method: "POST" });
    const data = await res.json();
    if (data.ok) {
      showToast(`${taskId} marked as completed!`, "success");
      loadDriverPage();
    }
  } catch {
    showToast("Error updating task", "warning");
  }
}

async function setDriverStatus(status) {
  document.querySelectorAll(".toggle-btn").forEach(b => b.classList.remove("active"));
  document.getElementById(`toggle-${status}`).classList.add("active");
  try {
    const res = await fetch(`${API}/driver/status`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
    const data = await res.json();
    showToast(data.message, "info");
  } catch {
    showToast("Status update failed", "warning");
  }
}

// ─────────────────────────────────────────────
//  ─── CUSTOMER TRACKING ───
// ─────────────────────────────────────────────
function quickTrack(id) {
  document.getElementById("order-input").value = id;
  trackOrder();
}

async function trackOrder() {
  const raw = document.getElementById("order-input").value.trim();
  if (!raw) { showToast("Please enter an Order ID", "warning"); return; }

  const resultEl = document.getElementById("tracking-result");
  resultEl.style.display = "block";
  resultEl.innerHTML = `<div class="loading-spinner"></div>`;

  try {
    const res = await fetch(`${API}/track/${raw}`);
    const data = await res.json();
    if (!data.ok) {
      resultEl.innerHTML = `<div class="card" style="text-align:center;padding:40px;color:var(--accent-red);">
        ❌ Order <strong>${raw}</strong> not found. Try ORD-2847, ORD-2851, or ORD-2863.</div>`;
      return;
    }
    renderTrackingResult(data.order, resultEl);
  } catch {
    resultEl.innerHTML = `<div class="card" style="text-align:center;padding:40px;color:var(--accent-red);">Server error. Is Flask running?</div>`;
  }
}

function renderTrackingResult(order, el) {
  const STATUS_MAP = {
    "in-transit": { label: "In Transit",  color: "#1D4ED8" },
    "delayed":    { label: "Delayed",     color: "#D97706" },
    "pending":    { label: "Pending",     color: "#6B7280" },
    "completed":  { label: "Completed",   color: "#16A34A" },
  };
  const st = STATUS_MAP[order.status] || { label: order.status, color: "#333" };

  const stepsHTML = order.steps.map(s => `
    <div class="timeline-step">
      <div class="t-dot ${s.done ? 'done' : 'pending'}">${s.done ? "✓" : "○"}</div>
      <div><div class="t-label">${s.label}</div><div class="t-time">${s.time}</div></div>
    </div>
  `).join("");

  const delayHTML = order.delayReason ? `
    <div class="delay-box">
      <div class="delay-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg></div>
      <div><div class="delay-title">⚠️ Delay Notification</div><div class="delay-desc">${order.delayReason}</div></div>
    </div>` : "";

  el.innerHTML = `<div class="order-result">
    ${delayHTML}
    <div class="eta-card" style="margin-bottom:16px;">
      <div class="eta-label">Estimated Arrival</div>
      <div class="eta-time">${order.eta}</div>
      <div class="eta-sub">Order ${order.id} • ${order.customer}</div>
      <div class="eta-progress">
        <div class="eta-progress-label"><span>Order Placed</span><span>Delivered</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${order.progress}%"></div></div>
      </div>
    </div>
    <div class="order-info-grid">
      <div class="info-item"><div class="info-label">Product</div><div class="info-value" style="font-size:13px;">${order.product}</div></div>
      <div class="info-item"><div class="info-label">Weight</div><div class="info-value">${order.weight}</div></div>
      <div class="info-item"><div class="info-label">Driver</div><div class="info-value">${order.driver}</div></div>
      <div class="info-item"><div class="info-label">Status</div><div class="info-value" style="color:${st.color};">${st.label}</div></div>
      <div class="info-item" style="grid-column:1/-1;"><div class="info-label">From</div><div class="info-value" style="font-size:12px;">${order.from}</div></div>
      <div class="info-item" style="grid-column:1/-1;"><div class="info-label">To</div><div class="info-value" style="font-size:12px;">${order.to}</div></div>
    </div>
    <div class="card">
      <div class="card-header"><div class="card-title">Shipment Timeline</div></div>
      <div class="tracking-timeline">${stepsHTML}</div>
    </div>
    <div style="text-align:center;margin-top:16px;">
      <button class="btn btn-outline" onclick="showToast('Support chat opened','info')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
        Contact Support
      </button>
    </div>
  </div>`;
}

// ─────────────────────────────────────────────
//  ─── ADMIN PANEL ───
// ─────────────────────────────────────────────
let currentPage = 1;
let filteredTotal = 0;

async function loadAdminPage() {
  try {
    const [statsRes, chartRes, alertsRes] = await Promise.all([
      fetch(`${API}/admin/stats`),
      fetch(`${API}/admin/chart`),
      fetch(`${API}/admin/alerts`),
    ]);
    const stats  = await statsRes.json();
    const chart  = await chartRes.json();
    const alerts = await alertsRes.json();
    renderAdminStats(stats);
    renderBarChart(chart);
    renderAlerts(alerts);
  } catch {
    showToast("Could not load admin data", "warning");
  }
  filterTable();
}

function renderAdminStats(s) {
  document.getElementById("as-total").textContent    = s.total_deliveries;
  document.getElementById("as-ontime").textContent   = s.on_time_rate + "%";
  document.getElementById("as-delayed").textContent  = s.delayed;
  document.getElementById("as-failed").textContent   = s.failed;
  document.getElementById("as-drivers").textContent  = s.active_drivers;
}

function renderAlerts(alerts) {
  const el = document.getElementById("alerts-list");
  el.innerHTML = alerts.map(a => `
    <div class="alert-item ${a.type}">
      <div class="alert-icon ${a.type}">
        ${a.type === "danger"  ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>` : ""}
        ${a.type === "warning" ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>` : ""}
        ${a.type === "success" ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>` : ""}
      </div>
      <div>
        <div class="alert-title">${a.title}</div>
        <div class="alert-desc">${a.desc}</div>
        <div class="alert-time">${a.time}</div>
      </div>
    </div>
  `).join("");
}

async function filterTable() {
  const search = document.getElementById("admin-search")?.value || "";
  const status = document.getElementById("status-filter")?.value || "";
  const driver = document.getElementById("driver-filter")?.value || "";

  const params = new URLSearchParams({ search, status, driver, page: currentPage });
  try {
    const res  = await fetch(`${API}/admin/deliveries?${params}`);
    const data = await res.json();
    filteredTotal = data.total;
    renderTable(data.data, data.total);
  } catch {
    showToast("Could not load deliveries", "warning");
  }
}

function renderTable(rows, total) {
  const body = document.getElementById("table-body");
  const BADGE = {
    "on-time":   '<span class="badge on-time">On-Time</span>',
    "delayed":   '<span class="badge delayed">Delayed</span>',
    "in-transit":'<span class="badge in-transit">In Transit</span>',
    "completed": '<span class="badge completed">Completed</span>',
    "critical":  '<span class="badge critical">Critical</span>',
    "pending":   '<span class="badge pending">Pending</span>',
  };

  if (!rows.length) {
    body.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:40px;color:var(--text-muted);">No deliveries found</td></tr>`;
  } else {
    body.innerHTML = rows.map(d => {
      const initials = d.driver.split(" ").map(n => n[0]).join("");
      const delayStr = d.delay > 0 ? `<br><span style="font-size:11px;color:#D97706;">+${d.delay} min delay</span>` : "";
      return `<tr>
        <td><span style="font-family:'Syne',sans-serif;font-weight:700;color:#2563EB;">${d.id}</span></td>
        <td><div class="driver-cell">
          <div class="driver-avatar" style="background:${d.color};">${initials}</div>
          <div><div class="driver-name">${d.driver}</div><div class="driver-id">${d.driverId}</div></div>
        </div></td>
        <td style="font-size:13px;">${d.destination}</td>
        <td>${BADGE[d.status] || d.status}</td>
        <td style="font-size:13px;font-weight:600;">${d.eta}${delayStr}</td>
        <td style="font-size:13px;">${d.weight}</td>
        <td>
          <button class="btn btn-outline btn-sm" onclick="showToast('Viewing ${d.id}','info')" style="margin-right:4px;">View</button>
          <button class="btn btn-primary btn-sm" onclick="updateDelivery('${d.id}')">Update</button>
        </td>
      </tr>`;
    }).join("");
  }

  document.getElementById("table-count").textContent =
    `Showing ${rows.length} of ${total} deliveries`;
  renderPagination(total);
}

function renderPagination(total) {
  const totalPages = Math.ceil(total / 8);
  const pg = document.getElementById("pagination");
  let html = "";
  for (let i = 1; i <= totalPages; i++) {
    html += `<button class="page-btn ${i === currentPage ? "active" : ""}" onclick="goPage(${i})">${i}</button>`;
  }
  pg.innerHTML = html;
}

function goPage(p) { currentPage = p; filterTable(); }

async function updateDelivery(id) {
  try {
    const res = await fetch(`${API}/admin/delivery/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: "completed" }),
    });
    const data = await res.json();
    if (data.ok) { showToast(`${id} updated to completed`, "success"); filterTable(); }
  } catch { showToast("Update failed", "warning"); }
}

async function exportData() {
  showToast("Downloading CSV...", "success");
  window.location.href = `${API}/admin/export`;
}

function renderBarChart(data) {
  const maxVal = Math.max(...data.map(d => d.on + d.delayed));
  const H = 120;
  document.getElementById("bar-chart").innerHTML = data.map(d => {
    const total = d.on + d.delayed;
    const onH  = Math.round((d.on      / maxVal) * H);
    const delH = Math.round((d.delayed / maxVal) * H);
    return `<div class="chart-bar-wrap">
      <div class="chart-bar-val">${total}</div>
      <div style="display:flex;flex-direction:column;align-items:center;gap:2px;width:100%;">
        <div class="chart-bar" style="height:${delH}px;background:#F59E0B;" title="Delayed: ${d.delayed}"></div>
        <div class="chart-bar" style="height:${onH}px;background:#2563EB;" title="On-time: ${d.on}"></div>
      </div>
      <div class="chart-bar-label">${d.day}</div>
    </div>`;
  }).join("");
}

// ─────────────────────────────────────────────
//  Init
// ─────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  loadDriverPage();   // default page
});
