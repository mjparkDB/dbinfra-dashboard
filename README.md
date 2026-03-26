[IT인프라표준화_NocoDB_vs_Metabase_비교대시보드.html](https://github.com/user-attachments/files/26261551/IT._NocoDB_vs_Metabase_.html)
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>IT 인프라 표준화 조회시스템 — NocoDB vs Metabase 비교</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
:root {
  --bg: #0d0f14;
  --surface: #13161e;
  --surface2: #1a1e28;
  --border: #252a38;
  --border2: #2e3448;
  --text: #e2e6f0;
  --muted: #7a8099;
  --noco-primary: #0f9b72;
  --noco-accent: #13c79a;
  --noco-soft: rgba(15,155,114,0.12);
  --meta-primary: #509ee3;
  --meta-accent: #74b9f8;
  --meta-soft: rgba(80,158,227,0.12);
  --red: #e05c5c;
  --yellow: #e0c45c;
  --green: #5ce08a;
  --orange: #e0935c;
  --purple: #a78bfa;
  --radius: 10px;
  --radius-sm: 6px;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family: 'IBM Plex Sans KR', sans-serif; background: var(--bg); color: var(--text); min-height:100vh; overflow-x:hidden; }

/* ── TOP NAV ── */
.top-nav {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 28px;
  height: 58px;
  display: flex;
  align-items: center;
  gap: 24px;
  position: sticky;
  top:0;
  z-index:100;
}
.nav-logo { font-family:'Syne',sans-serif; font-size:15px; font-weight:800; letter-spacing:0.5px; color:var(--text); white-space:nowrap; }
.nav-logo span { color: var(--meta-accent); }
.nav-divider { width:1px; height:28px; background:var(--border); }
.nav-tabs { display:flex; gap:4px; }
.nav-tab {
  padding: 7px 18px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all .2s;
  color: var(--muted);
}
.nav-tab:hover { color: var(--text); background: var(--surface2); }
.nav-tab.active-noco { color: var(--noco-accent); background: var(--noco-soft); border-color: rgba(15,155,114,0.3); }
.nav-tab.active-meta { color: var(--meta-accent); background: var(--meta-soft); border-color: rgba(80,158,227,0.3); }
.nav-tab.active-split { color: var(--purple); background: rgba(167,139,250,0.1); border-color: rgba(167,139,250,0.3); }
.nav-badge { font-size:10px; padding:1px 7px; border-radius:20px; margin-left:6px; }
.badge-noco { background: var(--noco-soft); color: var(--noco-accent); }
.badge-meta { background: var(--meta-soft); color: var(--meta-accent); }
.nav-right { margin-left:auto; display:flex; align-items:center; gap:12px; }
.nav-date { font-size:12px; color:var(--muted); font-family:'JetBrains Mono',monospace; }

/* ── MAIN ── */
.main { display:flex; height: calc(100vh - 58px); }
.panel {
  flex:1;
  overflow:hidden;
  display:flex;
  flex-direction:column;
  transition: all .3s;
  position:relative;
}
.panel.hidden { display:none; }
.panel-divider { width:4px; background: var(--border); cursor:col-resize; flex-shrink:0; position:relative; z-index:10; }
.panel-divider::after { content:''; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:2px; height:40px; background:var(--border2); border-radius:2px; }

/* ── PANEL HEADER ── */
.panel-header {
  padding: 0 20px;
  height: 46px;
  display:flex;
  align-items:center;
  gap:12px;
  border-bottom: 1px solid var(--border);
  flex-shrink:0;
}
.panel-header.noco-header { background: #0d1812; border-bottom-color: rgba(15,155,114,0.25); }
.panel-header.meta-header { background: #0d1520; border-bottom-color: rgba(80,158,227,0.25); }
.tool-badge {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 3px 10px;
  border-radius: 5px;
  text-transform:uppercase;
}
.tool-badge.noco { background: var(--noco-soft); color: var(--noco-accent); border:1px solid rgba(15,155,114,0.3); }
.tool-badge.meta { background: var(--meta-soft); color: var(--meta-accent); border:1px solid rgba(80,158,227,0.3); }
.panel-title { font-size:13px; font-weight:500; color:var(--muted); }
.panel-actions { margin-left:auto; display:flex; gap:8px; }
.ph-btn {
  font-size:12px; padding:5px 12px; border-radius:6px; cursor:pointer; border:none;
  font-family:inherit; font-weight:500; transition:.15s;
}
.ph-btn.noco { background:var(--noco-soft); color:var(--noco-accent); border:1px solid rgba(15,155,114,0.3); }
.ph-btn.noco:hover { background:rgba(15,155,114,0.2); }
.ph-btn.meta { background:var(--meta-soft); color:var(--meta-accent); border:1px solid rgba(80,158,227,0.3); }
.ph-btn.meta:hover { background:rgba(80,158,227,0.2); }

/* ══════════════════════════════════════════════
   NOCODB PANEL
══════════════════════════════════════════════ */
.noco-panel { background: #0a0e0c; }
.noco-sidebar {
  width: 200px;
  border-right: 1px solid rgba(15,155,114,0.15);
  background: #0b0f0d;
  flex-shrink:0;
  overflow-y:auto;
  padding: 12px 0;
}
.noco-body { display:flex; flex:1; overflow:hidden; }
.noco-sidebar-section { padding: 6px 14px 2px; font-size:10px; color:#3a5a4a; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; margin-top:8px; }
.noco-sidebar-item {
  padding: 7px 14px 7px 20px;
  font-size:12.5px;
  color:#5a8a72;
  cursor:pointer;
  display:flex;
  align-items:center;
  gap:8px;
  transition:.15s;
  border-left: 2px solid transparent;
  position:relative;
}
.noco-sidebar-item:hover { color:#13c79a; background:rgba(15,155,114,0.07); }
.noco-sidebar-item.active { color: var(--noco-accent); background: var(--noco-soft); border-left-color: var(--noco-accent); font-weight:500; }
.noco-sidebar-count { margin-left:auto; font-size:11px; background:rgba(15,155,114,0.15); color:var(--noco-accent); padding:1px 6px; border-radius:10px; font-family:'JetBrains Mono',monospace; }
.noco-icon { font-size:14px; width:16px; text-align:center; }

.noco-content { flex:1; display:flex; flex-direction:column; overflow:hidden; }

/* NocoDB toolbar */
.noco-toolbar {
  height:44px; display:flex; align-items:center; gap:10px;
  padding:0 16px; border-bottom:1px solid rgba(15,155,114,0.12);
  background:#0b0f0d; flex-shrink:0;
}
.noco-view-btn {
  font-size:12px; padding:5px 12px; border-radius:5px; cursor:pointer;
  border:1px solid rgba(15,155,114,0.2); background:transparent; color:#5a8a72;
  font-family:inherit; display:flex; align-items:center; gap:5px; transition:.15s;
}
.noco-view-btn:hover, .noco-view-btn.active { background:var(--noco-soft); color:var(--noco-accent); border-color:rgba(15,155,114,0.4); }
.noco-filter-chip {
  font-size:11px; padding:4px 10px; border-radius:20px;
  background:rgba(15,155,114,0.1); color:var(--noco-accent);
  border:1px solid rgba(15,155,114,0.25); cursor:pointer; transition:.15s;
  display:flex; align-items:center; gap:4px;
}
.noco-filter-chip:hover { background:rgba(15,155,114,0.18); }
.noco-filter-chip.active { background:rgba(15,155,114,0.25); }
.chip-x { opacity:.6; }
.noco-search {
  margin-left:auto; background:rgba(15,155,114,0.06); border:1px solid rgba(15,155,114,0.15);
  border-radius:6px; padding:5px 12px; font-size:12px; color:var(--noco-accent);
  font-family:inherit; outline:none; width:160px; transition:.2s;
}
.noco-search::placeholder { color:#3a5a4a; }
.noco-search:focus { border-color:rgba(15,155,114,0.4); background:rgba(15,155,114,0.1); }

/* NocoDB table */
.noco-table-wrap { flex:1; overflow:auto; }
.noco-table { width:100%; border-collapse:collapse; font-size:12.5px; }
.noco-table thead th {
  background:#0b0f0d; color:#3a6a54; font-size:11px; font-weight:600;
  padding:9px 12px; text-align:left; border-bottom:1px solid rgba(15,155,114,0.15);
  border-right:1px solid rgba(15,155,114,0.08); position:sticky; top:0; z-index:5;
  white-space:nowrap; letter-spacing:.4px; cursor:pointer; user-select:none;
}
.noco-table thead th:hover { color:var(--noco-accent); }
.noco-table thead th .sort-icon { opacity:.4; margin-left:4px; font-size:10px; }
.noco-table tbody tr {
  border-bottom:1px solid rgba(15,155,114,0.07);
  cursor:pointer; transition:.12s;
}
.noco-table tbody tr:hover { background:rgba(15,155,114,0.05); }
.noco-table tbody tr.selected-row { background:rgba(15,155,114,0.1); }
.noco-table tbody td {
  padding:8px 12px; border-right:1px solid rgba(15,155,114,0.06);
  white-space:nowrap; color:#9ab8a8;
}
.noco-table tbody td:first-child { color:var(--text); font-weight:500; }
.row-num { color:#2a4a3a; font-family:'JetBrains Mono',monospace; font-size:11px; width:36px; text-align:right; padding-right:14px; }
.expand-icon { color:#3a6a54; margin-right:8px; font-size:11px; opacity:0; transition:.15s; }
.noco-table tbody tr:hover .expand-icon { opacity:1; }

/* Status badges */
.status-badge {
  display:inline-flex; align-items:center; gap:5px;
  font-size:11px; padding:3px 9px; border-radius:20px; font-weight:500;
}
.status-dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; }
.s-good { background:rgba(92,224,138,0.12); color:#5ce08a; border:1px solid rgba(92,224,138,0.2); }
.s-good .status-dot { background:#5ce08a; }
.s-warn { background:rgba(224,196,92,0.12); color:#e0c45c; border:1px solid rgba(224,196,92,0.2); }
.s-warn .status-dot { background:#e0c45c; }
.s-eol { background:rgba(224,92,92,0.12); color:#e05c5c; border:1px solid rgba(224,92,92,0.2); }
.s-eol .status-dot { background:#e05c5c; }
.s-caution { background:rgba(224,147,92,0.12); color:#e0935c; border:1px solid rgba(224,147,92,0.2); }
.s-caution .status-dot { background:#e0935c; }

.type-chip { font-size:11px; padding:2px 8px; border-radius:4px; font-family:'JetBrains Mono',monospace; background:rgba(100,120,180,0.12); color:#8899cc; border:1px solid rgba(100,120,180,0.2); }
.ver-text { font-family:'JetBrains Mono',monospace; color:#7a9c8a; font-size:12px; }
.site-text { color:#6a8a78; }
.count-cell { font-family:'JetBrains Mono',monospace; text-align:center; }
.noco-footer { height:32px; border-top:1px solid rgba(15,155,114,0.12); background:#0b0f0d; flex-shrink:0; display:flex; align-items:center; padding:0 16px; gap:16px; }
.noco-footer-text { font-size:11px; color:#3a5a4a; }
.noco-footer-text span { color:var(--noco-accent); }
.noco-add-row { font-size:11px; color:#2a4a3a; cursor:pointer; display:flex; align-items:center; gap:4px; transition:.15s; }
.noco-add-row:hover { color:var(--noco-accent); }


/* ══════════════════════════════════════════════
   METABASE PANEL
══════════════════════════════════════════════ */
.meta-panel { background: #0a0d14; }
.meta-body { display:flex; flex:1; overflow:hidden; }
.meta-sidebar {
  width:200px; border-right:1px solid rgba(80,158,227,0.12);
  background:#090c13; flex-shrink:0; overflow-y:auto; padding:12px 0;
}
.meta-sidebar-section { padding:6px 14px 2px; font-size:10px; color:#2a3a5a; font-weight:600; letter-spacing:1.2px; text-transform:uppercase; margin-top:8px; }
.meta-sidebar-item {
  padding:7px 14px 7px 20px; font-size:12.5px; color:#4a6a9a;
  cursor:pointer; display:flex; align-items:center; gap:8px; transition:.15s;
  border-left:2px solid transparent;
}
.meta-sidebar-item:hover { color:var(--meta-accent); background:rgba(80,158,227,0.07); }
.meta-sidebar-item.active { color:var(--meta-accent); background:var(--meta-soft); border-left-color:var(--meta-accent); font-weight:500; }
.meta-content { flex:1; overflow:auto; padding:16px; display:flex; flex-direction:column; gap:14px; }

/* KPI cards */
.meta-kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; flex-shrink:0; }
.meta-kpi {
  background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius);
  padding:14px 16px; cursor:pointer; transition:.2s; position:relative; overflow:hidden;
}
.meta-kpi::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:var(--radius) var(--radius) 0 0; }
.meta-kpi.k-blue::before { background:var(--meta-primary); }
.meta-kpi.k-green::before { background:var(--green); }
.meta-kpi.k-red::before { background:var(--red); }
.meta-kpi.k-yellow::before { background:var(--yellow); }
.meta-kpi:hover { border-color:var(--border2); transform:translateY(-1px); box-shadow:0 4px 20px rgba(0,0,0,0.3); }
.kpi-label { font-size:11px; color:var(--muted); font-weight:500; letter-spacing:.3px; margin-bottom:8px; }
.kpi-value { font-size:28px; font-weight:700; font-family:'Syne',sans-serif; line-height:1; margin-bottom:4px; }
.kpi-value.c-blue { color:var(--meta-accent); }
.kpi-value.c-green { color:var(--green); }
.kpi-value.c-red { color:var(--red); }
.kpi-value.c-yellow { color:var(--yellow); }
.kpi-sub { font-size:11px; color:var(--muted); }
.kpi-trend { font-size:11px; }
.kpi-trend.up { color:var(--green); }
.kpi-trend.down { color:var(--red); }

/* Chart row */
.meta-chart-row { display:grid; grid-template-columns:1.4fr 1fr; gap:10px; flex-shrink:0; }
.meta-card {
  background:var(--surface2); border:1px solid var(--border); border-radius:var(--radius); overflow:hidden;
}
.meta-card-header { padding:12px 16px; border-bottom:1px solid var(--border); display:flex; align-items:center; gap:10px; }
.meta-card-title { font-size:13px; font-weight:600; color:var(--text); }
.meta-card-sub { font-size:11px; color:var(--muted); margin-left:auto; }
.meta-card-body { padding:14px 16px; }

/* Bar chart */
.bar-chart { display:flex; align-items:flex-end; gap:8px; height:130px; }
.bar-group { flex:1; display:flex; flex-direction:column; align-items:center; gap:5px; }
.bar-wrap { flex:1; display:flex; align-items:flex-end; width:100%; }
.bar {
  width:100%; border-radius:3px 3px 0 0; transition:.4s ease; cursor:pointer; position:relative;
  min-height:4px;
}
.bar:hover { filter:brightness(1.2); }
.bar-label { font-size:10px; color:var(--muted); white-space:nowrap; text-align:center; }
.bar-val { font-size:10px; text-align:center; font-family:'JetBrains Mono',monospace; }

/* Donut */
.donut-wrap { display:flex; align-items:center; gap:16px; }
.donut-svg { flex-shrink:0; }
.donut-legend { display:flex; flex-direction:column; gap:8px; }
.legend-item { display:flex; align-items:center; gap:8px; font-size:12px; cursor:pointer; }
.legend-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
.legend-label { color:var(--muted); }
.legend-val { margin-left:auto; font-family:'JetBrains Mono',monospace; font-weight:600; color:var(--text); }

/* Table card */
.meta-table { width:100%; border-collapse:collapse; font-size:12px; }
.meta-table thead th { padding:8px 12px; text-align:left; color:var(--muted); font-size:11px; font-weight:600; letter-spacing:.4px; border-bottom:1px solid var(--border); background:var(--surface); white-space:nowrap; }
.meta-table tbody tr { border-bottom:1px solid rgba(255,255,255,0.04); cursor:pointer; transition:.12s; }
.meta-table tbody tr:hover { background:rgba(80,158,227,0.06); }
.meta-table tbody td { padding:8px 12px; color:var(--muted); }
.meta-table tbody td:first-child { color:var(--text); font-weight:500; }
.meta-pager { padding:10px 16px; display:flex; align-items:center; justify-content:space-between; border-top:1px solid var(--border); }
.pager-info { font-size:11px; color:var(--muted); }
.pager-btns { display:flex; gap:4px; }
.pager-btn { font-size:11px; padding:4px 9px; border-radius:4px; border:1px solid var(--border); background:transparent; color:var(--muted); cursor:pointer; font-family:inherit; transition:.15s; }
.pager-btn:hover { border-color:var(--meta-primary); color:var(--meta-accent); }
.pager-btn.active { background:var(--meta-soft); color:var(--meta-accent); border-color:rgba(80,158,227,0.4); }

/* ══════════════════════════════════════════════
   DETAIL MODAL (공통)
══════════════════════════════════════════════ */
.modal-overlay {
  position:fixed; inset:0; background:rgba(0,0,0,0.75); z-index:1000;
  display:none; align-items:center; justify-content:center;
  backdrop-filter:blur(4px);
}
.modal-overlay.open { display:flex; animation:fadeIn .2s; }
@keyframes fadeIn { from{opacity:0} to{opacity:1} }
.modal-box {
  background:var(--surface); border:1px solid var(--border2); border-radius:14px;
  width:640px; max-height:80vh; overflow:hidden; display:flex; flex-direction:column;
  box-shadow:0 24px 80px rgba(0,0,0,0.6);
  animation:slideUp .25s ease;
}
@keyframes slideUp { from{transform:translateY(20px);opacity:0} to{transform:translateY(0);opacity:1} }
.modal-header {
  padding:18px 22px; border-bottom:1px solid var(--border);
  display:flex; align-items:center; gap:12px;
}
.modal-mode { font-size:11px; padding:3px 10px; border-radius:20px; font-weight:700; letter-spacing:.8px; text-transform:uppercase; }
.modal-mode.m-noco { background:var(--noco-soft); color:var(--noco-accent); }
.modal-mode.m-meta { background:var(--meta-soft); color:var(--meta-accent); }
.modal-title { font-size:16px; font-weight:700; }
.modal-close { margin-left:auto; width:28px; height:28px; border-radius:6px; background:var(--surface2); border:1px solid var(--border); cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:14px; color:var(--muted); transition:.15s; }
.modal-close:hover { color:var(--text); border-color:var(--border2); }
.modal-body { padding:20px 22px; overflow-y:auto; }

.detail-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:16px; }
.detail-field { background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:12px 14px; }
.detail-field-label { font-size:10px; color:var(--muted); letter-spacing:.6px; text-transform:uppercase; margin-bottom:4px; }
.detail-field-val { font-size:13px; font-weight:600; color:var(--text); }
.detail-field-val.mono { font-family:'JetBrains Mono',monospace; font-size:12px; }
.detail-section { margin-bottom:14px; }
.detail-section-title { font-size:11px; color:var(--muted); letter-spacing:.8px; text-transform:uppercase; font-weight:600; margin-bottom:8px; padding-bottom:6px; border-bottom:1px solid var(--border); }
.detail-row { display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.04); font-size:13px; }
.detail-row:last-child { border-bottom:none; }
.detail-row-label { color:var(--muted); }
.detail-row-val { color:var(--text); font-weight:500; }
.detail-row-val.mono { font-family:'JetBrains Mono',monospace; font-size:12px; }
.modal-footer { padding:14px 22px; border-top:1px solid var(--border); display:flex; gap:8px; justify-content:flex-end; }
.modal-btn { font-size:12px; padding:7px 16px; border-radius:7px; cursor:pointer; font-family:inherit; font-weight:500; transition:.15s; border:1px solid var(--border); }
.modal-btn.primary-noco { background:var(--noco-soft); color:var(--noco-accent); border-color:rgba(15,155,114,0.3); }
.modal-btn.primary-noco:hover { background:rgba(15,155,114,0.2); }
.modal-btn.primary-meta { background:var(--meta-soft); color:var(--meta-accent); border-color:rgba(80,158,227,0.3); }
.modal-btn.primary-meta:hover { background:rgba(80,158,227,0.2); }
.modal-btn.secondary { background:transparent; color:var(--muted); }
.modal-btn.secondary:hover { color:var(--text); }

/* ── TOOLTIP ── */
.tooltip { position:absolute; background:#1e2433; border:1px solid var(--border2); border-radius:6px; padding:6px 10px; font-size:11px; color:var(--text); pointer-events:none; z-index:500; opacity:0; transition:.15s; white-space:nowrap; }

/* ── COMPARE NOTE ── */
.compare-note {
  position:fixed; bottom:16px; left:50%; transform:translateX(-50%);
  background:rgba(20,24,36,0.95); border:1px solid var(--border2); border-radius:30px;
  padding:8px 20px; font-size:12px; color:var(--muted); z-index:200;
  display:flex; align-items:center; gap:10px; backdrop-filter:blur(8px);
}
.compare-note strong { color:var(--text); }
.cn-noco { color:var(--noco-accent); }
.cn-meta { color:var(--meta-accent); }
</style>
</head>
<body>

<!-- TOP NAV -->
<nav class="top-nav">
  <div class="nav-logo">IT인프라 <span>표준화조회</span></div>
  <div class="nav-divider"></div>
  <div class="nav-tabs">
    <div class="nav-tab" id="tab-noco" onclick="setView('noco')">
      🍃 NocoDB <span class="nav-badge badge-noco">스프레드시트형</span>
    </div>
    <div class="nav-tab" id="tab-meta" onclick="setView('meta')">
      📊 Metabase <span class="nav-badge badge-meta">BI 대시보드형</span>
    </div>
    <div class="nav-tab active-split" id="tab-split" onclick="setView('split')">
      ⊞ 나란히 비교
    </div>
  </div>
  <div class="nav-right">
    <div class="nav-date" id="nav-clock">2026-03-26 09:41</div>
  </div>
</nav>

<!-- MAIN -->
<div class="main" id="main-wrap">

  <!-- ═══ NOCODB PANEL ═══ -->
  <div class="panel noco-panel" id="panel-noco">
    <div class="panel-header noco-header">
      <div class="tool-badge noco">NocoDB</div>
      <span class="panel-title">IT 인프라 자산 데이터베이스 · 표 보기</span>
      <div class="panel-actions">
        <button class="ph-btn noco" onclick="nocoExport()">↓ Export</button>
        <button class="ph-btn noco" onclick="nocoNewRow()">+ 행 추가</button>
      </div>
    </div>
    <div class="noco-body">
      <!-- Sidebar -->
      <div class="noco-sidebar">
        <div class="noco-sidebar-section">워크스페이스</div>
        <div class="noco-sidebar-item active" onclick="nocoNav(this,'network')">
          <span class="noco-icon">🌐</span> 네트워크 장비
          <span class="noco-sidebar-count">47</span>
        </div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'server')">
          <span class="noco-icon">🖥</span> 서버
          <span class="noco-sidebar-count">124</span>
        </div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'sw')">
          <span class="noco-icon">📦</span> 소프트웨어
          <span class="noco-sidebar-count">311</span>
        </div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'eol')">
          <span class="noco-icon">⚠️</span> EOL 대상
          <span class="noco-sidebar-count" style="background:rgba(224,92,92,0.15);color:#e05c5c;">12</span>
        </div>
        <div class="noco-sidebar-section" style="margin-top:16px;">뷰</div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'grid')">
          <span class="noco-icon">⊞</span> 표 보기
        </div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'gallery')">
          <span class="noco-icon">▦</span> 갤러리 보기
        </div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'kanban')">
          <span class="noco-icon">▥</span> 칸반 보기
        </div>
        <div class="noco-sidebar-section" style="margin-top:16px;">공유</div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'share')">
          <span class="noco-icon">🔗</span> 공유 링크
        </div>
        <div class="noco-sidebar-item" onclick="nocoNav(this,'api')">
          <span class="noco-icon">⚡</span> API 연동
        </div>
      </div>

      <!-- Content -->
      <div class="noco-content">
        <div class="noco-toolbar">
          <button class="noco-view-btn active" id="noco-view-grid">⊞ 표</button>
          <button class="noco-view-btn" id="noco-view-kanban">▥ 칸반</button>
          <div style="width:1px;height:20px;background:rgba(15,155,114,0.2);margin:0 4px;"></div>
          <div class="noco-filter-chip active" id="chip-all" onclick="nocoFilter('all')">전체 <span class="chip-x">✕</span></div>
          <div class="noco-filter-chip" id="chip-eol" onclick="nocoFilter('eol')">⚠ EOL 임박</div>
          <div class="noco-filter-chip" id="chip-cisco" onclick="nocoFilter('cisco')">Cisco</div>
          <div class="noco-filter-chip" id="chip-seoul" onclick="nocoFilter('seoul')">서울 본사</div>
          <input class="noco-search" type="text" placeholder="🔍  장비 검색..." id="noco-search-input" oninput="nocoSearch(this.value)">
        </div>

        <div class="noco-table-wrap">
          <table class="noco-table" id="noco-table">
            <thead>
              <tr>
                <th class="row-num"></th>
                <th onclick="nocoSort('name')">장비명 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('type')">유형 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('vendor')">제조사 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('model')">모델 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('os')">OS / 펌웨어 버전 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('latest')">최신 버전 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('site')">사이트 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('status')">상태 <span class="sort-icon">↕</span></th>
                <th onclick="nocoSort('eol')">EOL 일자 <span class="sort-icon">↕</span></th>
              </tr>
            </thead>
            <tbody id="noco-tbody"></tbody>
          </table>
        </div>
        <div class="noco-footer">
          <span class="noco-footer-text">총 <span id="noco-count">47</span>개 행</span>
          <span class="noco-footer-text">필터 적용: <span id="noco-filter-label">없음</span></span>
          <div class="noco-add-row" onclick="nocoNewRow()">+ 행 추가</div>
        </div>
      </div>
    </div>
  </div>

  <!-- DIVIDER (split mode) -->
  <div class="panel-divider" id="panel-divider"></div>

  <!-- ═══ METABASE PANEL ═══ -->
  <div class="panel meta-panel" id="panel-meta">
    <div class="panel-header meta-header">
      <div class="tool-badge meta">Metabase</div>
      <span class="panel-title">IT 인프라 표준화 현황 대시보드</span>
      <div class="panel-actions">
        <button class="ph-btn meta" onclick="metaShare()">🔗 공유</button>
        <button class="ph-btn meta" onclick="metaRefresh()">↺ 새로고침</button>
      </div>
    </div>
    <div class="meta-body">
      <div class="meta-sidebar">
        <div class="meta-sidebar-section">대시보드</div>
        <div class="meta-sidebar-item active">📊 인프라 현황 종합</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">🌐 네트워크 장비 현황</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">🖥 서버 OS 버전 현황</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">⚠️ EOL 모니터링</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">🏢 사이트별 현황</div>
        <div class="meta-sidebar-section" style="margin-top:16px;">질의</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">📝 새 질문 만들기</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">📁 저장된 질문</div>
        <div class="meta-sidebar-section" style="margin-top:16px;">데이터소스</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">🗄 CMDB · PostgreSQL</div>
        <div class="meta-sidebar-item" onclick="metaNav(this)">📋 ITSM · MySQL</div>
      </div>

      <div class="meta-content" id="meta-content">
        <!-- KPI Row -->
        <div class="meta-kpi-row">
          <div class="meta-kpi k-blue" onclick="metaKpiClick('total')">
            <div class="kpi-label">총 관리 자산</div>
            <div class="kpi-value c-blue">482</div>
            <div class="kpi-sub">장비 <span class="kpi-trend up">↑ 23 이번달</span></div>
          </div>
          <div class="meta-kpi k-green" onclick="metaKpiClick('standard')">
            <div class="kpi-label">표준화 준수율</div>
            <div class="kpi-value c-green">74%</div>
            <div class="kpi-sub kpi-trend up">↑ 8.2%p 지난달 대비</div>
          </div>
          <div class="meta-kpi k-red" onclick="metaKpiClick('eol')">
            <div class="kpi-label">EOL 임박 장비</div>
            <div class="kpi-value c-red">12</div>
            <div class="kpi-sub">6개월 이내 만료 <span class="kpi-trend down">↑ 3 증가</span></div>
          </div>
          <div class="meta-kpi k-yellow" onclick="metaKpiClick('upgrade')">
            <div class="kpi-label">업그레이드 필요</div>
            <div class="kpi-value c-yellow">38</div>
            <div class="kpi-sub">버전 2단계 이상 뒤처짐</div>
          </div>
        </div>

        <!-- Chart Row -->
        <div class="meta-chart-row">
          <!-- Bar chart: 사이트별 표준화율 -->
          <div class="meta-card">
            <div class="meta-card-header">
              <div class="meta-card-title">📍 사이트별 표준화 준수율</div>
              <div class="meta-card-sub">2026 Q1 기준</div>
            </div>
            <div class="meta-card-body">
              <div class="bar-chart" id="meta-bar-chart">
                <!-- bars inserted by JS -->
              </div>
            </div>
          </div>

          <!-- Donut chart: 장비 유형별 비율 -->
          <div class="meta-card">
            <div class="meta-card-header">
              <div class="meta-card-title">⚙️ 장비 유형별 현황</div>
              <div class="meta-card-sub">총 482대</div>
            </div>
            <div class="meta-card-body">
              <div class="donut-wrap">
                <svg class="donut-svg" width="110" height="110" viewBox="0 0 110 110" id="donut-svg">
                  <!-- drawn by JS -->
                </svg>
                <div class="donut-legend" id="donut-legend"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Table card -->
        <div class="meta-card">
          <div class="meta-card-header">
            <div class="meta-card-title">🔍 버전 비표준 장비 목록</div>
            <div class="meta-card-sub">클릭하여 상세 조회</div>
          </div>
          <table class="meta-table" id="meta-table">
            <thead>
              <tr>
                <th>장비명</th>
                <th>유형</th>
                <th>현재 버전</th>
                <th>표준 버전</th>
                <th>사이트</th>
                <th>우선순위</th>
                <th>상태</th>
              </tr>
            </thead>
            <tbody id="meta-tbody"></tbody>
          </table>
          <div class="meta-pager">
            <span class="pager-info">총 38개 중 1-10 표시</span>
            <div class="pager-btns">
              <button class="pager-btn active">1</button>
              <button class="pager-btn" onclick="metaPage(this,2)">2</button>
              <button class="pager-btn" onclick="metaPage(this,3)">3</button>
              <button class="pager-btn" onclick="metaPage(this,4)">4</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- MODAL (공통) -->
<div class="modal-overlay" id="modal-overlay" onclick="closeModal(event)">
  <div class="modal-box" id="modal-box">
    <div class="modal-header">
      <div class="modal-mode" id="modal-mode-badge"></div>
      <div class="modal-title" id="modal-title"></div>
      <div class="modal-close" onclick="closeModalDirect()">✕</div>
    </div>
    <div class="modal-body" id="modal-body"></div>
    <div class="modal-footer" id="modal-footer"></div>
  </div>
</div>

<!-- COMPARE NOTE -->
<div class="compare-note" id="compare-note">
  <span class="cn-noco">🍃 NocoDB</span> 스프레드시트형 직접 편집 &nbsp;·&nbsp;
  <span class="cn-meta">📊 Metabase</span> BI 분석형 시각화 &nbsp;·&nbsp;
  <strong>행·카드 클릭</strong>으로 상세 조회
</div>

<script>
// ──────────────────────────────────────
// DATA
// ──────────────────────────────────────
const networkData = [
  {id:1, name:'CORE-SW-01', type:'Core Switch', vendor:'Cisco', model:'Catalyst 9500', os:'17.3.6', latest:'17.12.2', site:'서울 본사', status:'warn', eol:'2028-03-31', ip:'10.0.1.1', slots:8, uptime:'712일', mgmt:'SNMP v3', rack:'IDC-A-01'},
  {id:2, name:'DIST-SW-B2F', type:'Distribution SW', vendor:'Cisco', model:'Catalyst 9300', os:'17.6.1', latest:'17.12.2', site:'서울 본사', status:'warn', eol:'2029-06-30', ip:'10.0.2.10', slots:4, uptime:'389일', mgmt:'SNMP v3', rack:'B2F-IDF-01'},
  {id:3, name:'FW-EDGE-01', type:'Firewall', vendor:'Palo Alto', model:'PA-5220', os:'10.1.9', latest:'11.1.2', site:'서울 본사', status:'eol', eol:'2025-12-31', ip:'203.x.x.1', slots:0, uptime:'1024일', mgmt:'Panorama', rack:'IDC-A-02'},
  {id:4, name:'BR-RTR-BUSAN', type:'Branch Router', vendor:'Cisco', model:'ISR 4331', os:'16.9.8', latest:'17.6.4', site:'부산 지점', status:'eol', eol:'2025-09-30', ip:'10.10.1.1', slots:2, uptime:'834일', mgmt:'SNMP v2c', rack:'BS-IDC-01'},
  {id:5, name:'ACC-SW-3F-A', type:'Access Switch', vendor:'Cisco', model:'Catalyst 2960-X', os:'15.2.7', latest:'15.2.7', site:'서울 본사', status:'good', eol:'2027-10-31', ip:'10.0.3.21', slots:0, uptime:'201일', mgmt:'SNMP v3', rack:'3F-IDF-A'},
  {id:6, name:'WLC-CENTRAL', type:'Wireless Controller', vendor:'Cisco', model:'9800-L', os:'17.9.3', latest:'17.12.1', site:'서울 본사', status:'warn', eol:'2030-01-31', ip:'10.0.5.5', slots:0, uptime:'445일', mgmt:'WebUI', rack:'IDC-A-03'},
  {id:7, name:'BR-SW-DAEGU', type:'Branch Switch', vendor:'HP', model:'Aruba 2930F', os:'16.10.0015', latest:'16.11.0009', site:'대구 지점', status:'warn', eol:'2028-12-31', ip:'10.20.1.10', slots:0, uptime:'178일', mgmt:'SNMP v2c', rack:'DG-MDF'},
  {id:8, name:'IDS-DMZ-01', type:'IDS/IPS', vendor:'Snort', model:'VM-IDS', os:'3.1.44', latest:'3.1.66', site:'서울 본사', status:'caution', eol:'N/A', ip:'10.0.100.5', slots:0, uptime:'67일', mgmt:'Web API', rack:'IDC-B-01'},
  {id:9, name:'CORE-SW-02', type:'Core Switch', vendor:'Cisco', model:'Catalyst 9500', os:'17.12.2', latest:'17.12.2', site:'서울 본사', status:'good', eol:'2028-03-31', ip:'10.0.1.2', slots:8, uptime:'398일', mgmt:'SNMP v3', rack:'IDC-A-01'},
  {id:10, name:'BR-RTR-GWANGJU', type:'Branch Router', vendor:'Cisco', model:'ISR 4321', os:'17.3.6', latest:'17.6.4', site:'광주 지점', status:'warn', eol:'2027-05-31', ip:'10.30.1.1', slots:2, uptime:'521일', mgmt:'SNMP v3', rack:'GJ-IDC-01'},
  {id:11, name:'FW-BRANCH-INCHEON', type:'Firewall', vendor:'Fortinet', model:'FortiGate 80F', os:'7.0.12', latest:'7.4.3', site:'인천 지점', status:'warn', eol:'2029-11-30', ip:'10.40.0.1', slots:0, uptime:'299일', mgmt:'FortiManager', rack:'IC-IDF'},
  {id:12, name:'ACC-SW-5F-A', type:'Access Switch', vendor:'Cisco', model:'Catalyst 3650', os:'16.12.9', latest:'16.12.10', site:'서울 본사', status:'caution', eol:'2026-07-31', ip:'10.0.3.51', slots:0, uptime:'632일', mgmt:'SNMP v2c', rack:'5F-IDF-A'},
];

const metaTableData = [
  {name:'FW-EDGE-01', type:'Firewall', current:'10.1.9', standard:'11.1.2', site:'서울 본사', priority:'긴급', status:'eol'},
  {name:'BR-RTR-BUSAN', type:'Branch Router', current:'16.9.8', standard:'17.6.4', site:'부산 지점', priority:'긴급', status:'eol'},
  {name:'CORE-SW-01', type:'Core Switch', current:'17.3.6', standard:'17.12.2', site:'서울 본사', priority:'높음', status:'warn'},
  {name:'DIST-SW-B2F', type:'Dist. Switch', current:'17.6.1', standard:'17.12.2', site:'서울 본사', priority:'높음', status:'warn'},
  {name:'WLC-CENTRAL', type:'Wireless Ctrl', current:'17.9.3', standard:'17.12.1', site:'서울 본사', priority:'보통', status:'warn'},
  {name:'BR-SW-DAEGU', type:'Branch Switch', current:'16.10.0015', standard:'16.11.0009', site:'대구 지점', priority:'보통', status:'warn'},
  {name:'BR-RTR-GWANGJU', type:'Branch Router', current:'17.3.6', standard:'17.6.4', site:'광주 지점', priority:'보통', status:'warn'},
  {name:'FW-BRANCH-INCHEON', type:'Firewall', current:'7.0.12', standard:'7.4.3', site:'인천 지점', priority:'보통', status:'warn'},
  {name:'IDS-DMZ-01', type:'IDS/IPS', current:'3.1.44', standard:'3.1.66', site:'서울 본사', priority:'낮음', status:'caution'},
  {name:'ACC-SW-5F-A', type:'Access Switch', current:'16.12.9', standard:'16.12.10', site:'서울 본사', priority:'낮음', status:'caution'},
];

const barData = [
  {site:'서울 본사', rate:81, count:124},
  {site:'부산 지점', rate:58, count:38},
  {site:'대구 지점', rate:72, count:31},
  {site:'인천 지점', rate:65, count:27},
  {site:'광주 지점', rate:79, count:22},
  {site:'대전 지점', rate:87, count:19},
];

const donutData = [
  {label:'스위치', val:198, color:'#509ee3'},
  {label:'서버', val:124, color:'#5ce08a'},
  {label:'방화벽', val:47, color:'#e05c5c'},
  {label:'라우터', val:62, color:'#e0c45c'},
  {label:'무선AP/WLC', val:51, color:'#a78bfa'},
];

// ──────────────────────────────────────
// VIEW SWITCHING
// ──────────────────────────────────────
let currentView = 'split';

function setView(v) {
  currentView = v;
  const pNoco = document.getElementById('panel-noco');
  const pMeta = document.getElementById('panel-meta');
  const divider = document.getElementById('panel-divider');
  const tNoco = document.getElementById('tab-noco');
  const tMeta = document.getElementById('tab-meta');
  const tSplit = document.getElementById('tab-split');

  [tNoco,tMeta,tSplit].forEach(t => t.className = 'nav-tab');
  if(v==='noco') { pNoco.style.display='flex'; pMeta.style.display='none'; divider.style.display='none'; tNoco.className='nav-tab active-noco'; }
  else if(v==='meta') { pNoco.style.display='none'; pMeta.style.display='flex'; divider.style.display='none'; tMeta.className='nav-tab active-meta'; }
  else { pNoco.style.display='flex'; pMeta.style.display='flex'; divider.style.display='block'; tSplit.className='nav-tab active-split'; }
}

// ──────────────────────────────────────
// NOCODB RENDER
// ──────────────────────────────────────
let nocoCurrentFilter = 'all';
let nocoCurrentSearch = '';

function renderNoco(data) {
  const tbody = document.getElementById('noco-tbody');
  tbody.innerHTML = '';
  data.forEach((row, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="row-num">${i+1}</td>
      <td><span class="expand-icon">⤢</span>${row.name}</td>
      <td><span class="type-chip">${row.type}</span></td>
      <td>${row.vendor}</td>
      <td>${row.model}</td>
      <td><span class="ver-text">${row.os}</span></td>
      <td><span class="ver-text">${row.latest}</span>${row.os===row.latest?'&nbsp;<span style="color:#5ce08a;font-size:10px;">✓</span>':''}</td>
      <td><span class="site-text">${row.site}</span></td>
      <td>${statusBadge(row.status)}</td>
      <td><span class="ver-text" style="color:${row.eol<'2026-06-30'?'#e05c5c':'#7a8099'}">${row.eol}</span></td>
    `;
    tr.onclick = () => openNocoDetail(row);
    tbody.appendChild(tr);
  });
  document.getElementById('noco-count').textContent = data.length;
}

function statusBadge(s) {
  const m = {good:['s-good','정상'],warn:['s-warn','업그레이드 필요'],eol:['s-eol','EOL 임박'],caution:['s-caution','점검 권고']};
  const [cls,txt] = m[s]||['s-good','정상'];
  return `<span class="status-badge ${cls}"><span class="status-dot"></span>${txt}</span>`;
}

function nocoFilter(f) {
  nocoCurrentFilter = f;
  ['chip-all','chip-eol','chip-cisco','chip-seoul'].forEach(id => {
    document.getElementById(id)?.classList.remove('active');
  });
  document.getElementById('chip-'+f)?.classList.add('active');
  let label = '없음';
  let data = networkData;
  if(f==='eol') { data = networkData.filter(r=>r.status==='eol'); label='EOL 임박'; }
  else if(f==='cisco') { data = networkData.filter(r=>r.vendor==='Cisco'); label='Cisco 장비'; }
  else if(f==='seoul') { data = networkData.filter(r=>r.site==='서울 본사'); label='서울 본사'; }
  document.getElementById('noco-filter-label').textContent = label;
  if(nocoCurrentSearch) data = data.filter(r=>r.name.toLowerCase().includes(nocoCurrentSearch.toLowerCase())||r.model.toLowerCase().includes(nocoCurrentSearch.toLowerCase()));
  renderNoco(data);
}

function nocoSearch(val) {
  nocoCurrentSearch = val;
  nocoFilter(nocoCurrentFilter);
}

function nocoNav(el, view) {
  document.querySelectorAll('.noco-sidebar-item').forEach(i=>i.classList.remove('active'));
  el.classList.add('active');
  if(view==='network') renderNoco(networkData);
}

function nocoSort(col) {
  const data = [...networkData].sort((a,b)=>String(a[col]).localeCompare(String(b[col])));
  renderNoco(data);
}

function nocoExport() { showToast('CSV 파일을 내보내는 중...', '#0f9b72'); }
function nocoNewRow() { showToast('새 행이 추가되었습니다', '#0f9b72'); }

function openNocoDetail(row) {
  const isGood = row.os === row.latest;
  const statusMap = {good:'정상',warn:'업그레이드 필요',eol:'EOL 임박',caution:'점검 권고'};
  const colorMap = {good:'#5ce08a',warn:'#e0c45c',eol:'#e05c5c',caution:'#e0935c'};
  document.getElementById('modal-mode-badge').textContent = 'NocoDB 상세 레코드';
  document.getElementById('modal-mode-badge').className = 'modal-mode m-noco';
  document.getElementById('modal-title').textContent = row.name;
  document.getElementById('modal-body').innerHTML = `
    <div class="detail-grid">
      <div class="detail-field"><div class="detail-field-label">유형</div><div class="detail-field-val">${row.type}</div></div>
      <div class="detail-field"><div class="detail-field-label">제조사</div><div class="detail-field-val">${row.vendor}</div></div>
      <div class="detail-field"><div class="detail-field-label">모델</div><div class="detail-field-val">${row.model}</div></div>
      <div class="detail-field"><div class="detail-field-label">사이트</div><div class="detail-field-val">${row.site}</div></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">버전 정보</div>
      <div class="detail-row"><span class="detail-row-label">현재 OS/펌웨어 버전</span><span class="detail-row-val mono" style="color:${colorMap[row.status]}">${row.os}</span></div>
      <div class="detail-row"><span class="detail-row-label">최신(표준) 버전</span><span class="detail-row-val mono" style="color:#5ce08a">${row.latest}</span></div>
      <div class="detail-row"><span class="detail-row-label">버전 상태</span><span class="detail-row-val">${statusBadge(row.status)}</span></div>
      <div class="detail-row"><span class="detail-row-label">EOL 일자</span><span class="detail-row-val mono" style="color:${row.eol<'2026-06-30'?'#e05c5c':'#7a8099'}">${row.eol}</span></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">네트워크 정보</div>
      <div class="detail-row"><span class="detail-row-label">IP 주소</span><span class="detail-row-val mono">${row.ip}</span></div>
      <div class="detail-row"><span class="detail-row-label">관리 방식</span><span class="detail-row-val">${row.mgmt}</span></div>
      <div class="detail-row"><span class="detail-row-label">설치 위치 (랙)</span><span class="detail-row-val mono">${row.rack}</span></div>
      <div class="detail-row"><span class="detail-row-label">업타임</span><span class="detail-row-val mono">${row.uptime}</span></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">NocoDB 링크 필드</div>
      <div class="detail-row"><span class="detail-row-label">연결된 유지보수 이력</span><span class="detail-row-val" style="color:#0f9b72;cursor:pointer">🔗 3건 보기</span></div>
      <div class="detail-row"><span class="detail-row-label">연결된 변경 요청 (CAB)</span><span class="detail-row-val" style="color:#0f9b72;cursor:pointer">🔗 1건 보기</span></div>
    </div>
  `;
  document.getElementById('modal-footer').innerHTML = `
    <button class="modal-btn secondary" onclick="closeModalDirect()">닫기</button>
    <button class="modal-btn primary-noco" onclick="showToast('레코드를 편집 중입니다',\'#0f9b72\')">✏️ 편집</button>
    <button class="modal-btn primary-noco" onclick="showToast('변경 이력을 기록했습니다',\'#0f9b72\')">📋 변경 기록</button>
  `;
  document.getElementById('modal-overlay').classList.add('open');
}

// ──────────────────────────────────────
// METABASE RENDER
// ──────────────────────────────────────
function renderMetaBar() {
  const container = document.getElementById('meta-bar-chart');
  const maxRate = 100;
  const colors = ['#509ee3','#5ce08a','#a78bfa','#e0c45c','#e0935c','#74b9f8'];
  container.innerHTML = barData.map((d,i)=>`
    <div class="bar-group">
      <div class="bar-val" style="color:${colors[i]};font-size:11px;">${d.rate}%</div>
      <div class="bar-wrap">
        <div class="bar" style="height:${d.rate}%;background:${colors[i]};opacity:0.85;"
          onclick="metaBarClick('${d.site}',${d.rate},${d.count})" title="${d.site}: ${d.rate}%"></div>
      </div>
      <div class="bar-label">${d.site.replace(' ','\n')}</div>
    </div>
  `).join('');
}

function renderDonut() {
  const total = donutData.reduce((s,d)=>s+d.val,0);
  const cx=55, cy=55, r=38, inner=24;
  let startAngle = -Math.PI/2;
  let paths = '';
  donutData.forEach(d => {
    const angle = (d.val/total) * Math.PI * 2;
    const x1=cx+r*Math.cos(startAngle), y1=cy+r*Math.sin(startAngle);
    const x2=cx+r*Math.cos(startAngle+angle), y2=cy+r*Math.sin(startAngle+angle);
    const xi1=cx+inner*Math.cos(startAngle), yi1=cy+inner*Math.sin(startAngle);
    const xi2=cx+inner*Math.cos(startAngle+angle), yi2=cy+inner*Math.sin(startAngle+angle);
    const large = angle > Math.PI ? 1 : 0;
    paths += `<path d="M${xi1},${yi1} L${x1},${y1} A${r},${r} 0 ${large},1 ${x2},${y2} L${xi2},${yi2} A${inner},${inner} 0 ${large},0 ${xi1},${yi1} Z"
      fill="${d.color}" opacity="0.85" style="cursor:pointer;transition:.2s;" onmouseenter="this.style.opacity=1" onmouseleave="this.style.opacity=0.85"
      onclick="metaDonutClick('${d.label}',${d.val})"/>`;
    startAngle += angle;
  });
  document.getElementById('donut-svg').innerHTML = paths + `<text x="55" y="53" text-anchor="middle" fill="#e2e6f0" font-size="14" font-weight="700" font-family="Syne">${total}</text><text x="55" y="67" text-anchor="middle" fill="#7a8099" font-size="9">대</text>`;

  const legend = document.getElementById('donut-legend');
  legend.innerHTML = donutData.map(d=>`
    <div class="legend-item" onclick="metaDonutClick('${d.label}',${d.val})">
      <div class="legend-dot" style="background:${d.color}"></div>
      <div class="legend-label">${d.label}</div>
      <div class="legend-val">${d.val}</div>
    </div>
  `).join('');
}

function renderMetaTable() {
  const tbody = document.getElementById('meta-tbody');
  const priorityColor = {긴급:'#e05c5c',높음:'#e0935c',보통:'#e0c45c',낮음:'#7a8099'};
  tbody.innerHTML = metaTableData.map(row=>`
    <tr onclick="openMetaDetail('${row.name}')">
      <td>${row.name}</td>
      <td><span class="type-chip">${row.type}</span></td>
      <td><span class="ver-text" style="color:#e0c45c">${row.current}</span></td>
      <td><span class="ver-text" style="color:#5ce08a">${row.standard}</span></td>
      <td>${row.site}</td>
      <td><span style="color:${priorityColor[row.priority]};font-weight:600;font-size:12px;">● ${row.priority}</span></td>
      <td>${statusBadge(row.status)}</td>
    </tr>
  `).join('');
}

function metaNav(el) {
  document.querySelectorAll('.meta-sidebar-item').forEach(i=>i.classList.remove('active'));
  el.classList.add('active');
  showToast('대시보드를 불러오는 중...', '#509ee3');
}
function metaPage(btn,page) {
  document.querySelectorAll('.pager-btn').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  showToast(`${page}페이지 조회 중...`, '#509ee3');
}
function metaShare() { showToast('공유 링크가 클립보드에 복사되었습니다', '#509ee3'); }
function metaRefresh() {
  document.getElementById('meta-content').style.opacity='0.5';
  setTimeout(()=>{ document.getElementById('meta-content').style.opacity='1'; showToast('데이터가 새로고침 되었습니다', '#509ee3'); }, 800);
}
function metaKpiClick(type) {
  const m = {
    total:{t:'총 관리 자산 상세',b:'전체 482대 자산 중: 네트워크 장비 307대, 서버 124대, 기타 51대. 이번 달 신규 등록 23대 (네트워크 15, 서버 8).'},
    standard:{t:'표준화 준수율 분석',b:'74% 준수 (357/482대). 미준수 125대 중 EOL 12대, 버전 지연 38대, 인증서 만료 예정 22대, 설정 비표준 53대.'},
    eol:{t:'EOL 임박 장비 목록',b:'6개월 이내 EOL 12대: FW-EDGE-01 (Palo Alto, 2025-12-31), BR-RTR-BUSAN (Cisco, 2025-09-30) 등. 즉각 교체 계획 수립 필요.'},
    upgrade:{t:'업그레이드 필요 장비',b:'현재 버전이 표준 버전 대비 2단계 이상 지연된 장비 38대. 네트워크 장비 27대, 서버 11대 포함.'}
  };
  const info = m[type];
  openMetaModal(info.t, `<div class="detail-section"><div class="detail-section-title">분석 결과</div><p style="font-size:13px;color:var(--muted);line-height:1.7">${info.b}</p></div>`);
}
function metaBarClick(site, rate, count) {
  openMetaModal(`${site} 표준화 현황`, `
    <div class="detail-grid">
      <div class="detail-field"><div class="detail-field-label">사이트</div><div class="detail-field-val">${site}</div></div>
      <div class="detail-field"><div class="detail-field-label">총 장비 수</div><div class="detail-field-val">${count}대</div></div>
      <div class="detail-field"><div class="detail-field-label">표준화 준수율</div><div class="detail-field-val" style="color:${rate>=80?'#5ce08a':rate>=65?'#e0c45c':'#e05c5c'}">${rate}%</div></div>
      <div class="detail-field"><div class="detail-field-label">비준수 장비</div><div class="detail-field-val" style="color:#e0c45c">${Math.round(count*(100-rate)/100)}대</div></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">Metabase SQL 쿼리 (자동 생성)</div>
      <div style="background:#090c13;border:1px solid var(--border);border-radius:8px;padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#7a9c8a;line-height:1.8">
        SELECT device_name, os_version, standard_version<br>
        FROM infra_assets<br>
        WHERE site = '${site}'<br>
        &nbsp;&nbsp;AND os_version != standard_version<br>
        ORDER BY eol_date ASC;
      </div>
    </div>
  `);
}
function metaDonutClick(label, val) {
  openMetaModal(`${label} 장비 현황`, `
    <div class="detail-grid">
      <div class="detail-field"><div class="detail-field-label">유형</div><div class="detail-field-val">${label}</div></div>
      <div class="detail-field"><div class="detail-field-label">총 대수</div><div class="detail-field-val">${val}대</div></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">이 대시보드에서 드릴다운 조회</div>
      <div class="detail-row"><span class="detail-row-label">Metabase 클릭-스루 기능</span><span class="detail-row-val" style="color:#509ee3">차트 클릭 → 상세 쿼리 자동 생성</span></div>
      <div class="detail-row"><span class="detail-row-label">연동 대시보드</span><span class="detail-row-val" style="color:#509ee3;cursor:pointer">📊 ${label} 상세 대시보드 →</span></div>
    </div>
  `);
}

function openMetaDetail(name) {
  const row = networkData.find(r=>r.name===name) || {name,type:'장비',vendor:'-',model:'-',os:'17.x.x',latest:'17.12.2',site:'-',status:'warn',eol:'-',ip:'-',mgmt:'-',rack:'-',uptime:'-'};
  const colorMap = {good:'#5ce08a',warn:'#e0c45c',eol:'#e05c5c',caution:'#e0935c'};
  openMetaModal(`${name} — 상세 분석`, `
    <div class="detail-grid">
      <div class="detail-field"><div class="detail-field-label">현재 버전</div><div class="detail-field-val mono" style="color:${colorMap[row.status]}">${row.os}</div></div>
      <div class="detail-field"><div class="detail-field-label">표준(최신) 버전</div><div class="detail-field-val mono" style="color:#5ce08a">${row.latest}</div></div>
      <div class="detail-field"><div class="detail-field-label">상태</div><div class="detail-field-val">${statusBadge(row.status)}</div></div>
      <div class="detail-field"><div class="detail-field-label">EOL</div><div class="detail-field-val mono">${row.eol}</div></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">Metabase 분석 정보</div>
      <div class="detail-row"><span class="detail-row-label">버전 격차</span><span class="detail-row-val mono" style="color:#e0c45c">${row.os} → ${row.latest}</span></div>
      <div class="detail-row"><span class="detail-row-label">업그레이드 우선순위</span><span class="detail-row-val" style="color:#e0935c">높음 (EOL 고려)</span></div>
      <div class="detail-row"><span class="detail-row-label">동일 사이트 동일 유형</span><span class="detail-row-val" style="color:#509ee3;cursor:pointer">🔍 관련 장비 조회 →</span></div>
    </div>
    <div class="detail-section">
      <div class="detail-section-title">Metabase 자동 생성 인사이트</div>
      <p style="font-size:12px;color:var(--muted);line-height:1.7;background:rgba(80,158,227,0.06);border:1px solid rgba(80,158,227,0.12);border-radius:8px;padding:10px 12px;">
        이 장비는 현재 버전이 표준 버전 대비 <span style="color:#e0c45c">지연</span> 상태입니다. EOL 일자가 ${row.eol<'2026-12-31'?'<span style="color:#e05c5c">6개월 이내</span>':'2027년 이후'}로, 업그레이드 계획을 수립하는 것을 권장합니다.
      </p>
    </div>
  `);
}

function openMetaModal(title, body) {
  document.getElementById('modal-mode-badge').textContent = 'Metabase 분석';
  document.getElementById('modal-mode-badge').className = 'modal-mode m-meta';
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').innerHTML = body;
  document.getElementById('modal-footer').innerHTML = `
    <button class="modal-btn secondary" onclick="closeModalDirect()">닫기</button>
    <button class="modal-btn primary-meta" onclick="showToast('질문이 저장되었습니다',\'#509ee3\')">💾 질문 저장</button>
    <button class="modal-btn primary-meta" onclick="showToast('대시보드에 추가되었습니다',\'#509ee3\')">📊 대시보드 추가</button>
  `;
  document.getElementById('modal-overlay').classList.add('open');
}

function closeModal(e) { if(e.target===document.getElementById('modal-overlay')) closeModalDirect(); }
function closeModalDirect() { document.getElementById('modal-overlay').classList.remove('open'); }

// ──────────────────────────────────────
// TOAST
// ──────────────────────────────────────
function showToast(msg, color) {
  const t = document.createElement('div');
  t.style.cssText = `position:fixed;bottom:56px;left:50%;transform:translateX(-50%);background:${color||'#509ee3'};color:#fff;padding:9px 20px;border-radius:30px;font-size:12px;font-family:'IBM Plex Sans KR',sans-serif;font-weight:500;z-index:2000;animation:slideUp .2s;box-shadow:0 4px 20px rgba(0,0,0,0.4);pointer-events:none;white-space:nowrap`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(()=>t.remove(), 2000);
}

// ──────────────────────────────────────
// CLOCK
// ──────────────────────────────────────
function updateClock() {
  const now = new Date();
  const pad = n=>String(n).padStart(2,'0');
  document.getElementById('nav-clock').textContent = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}`;
}
setInterval(updateClock, 60000);

// ──────────────────────────────────────
// INIT
// ──────────────────────────────────────
renderNoco(networkData);
renderMetaBar();
renderDonut();
renderMetaTable();
setView('split');
</script>
</body>
</html>
