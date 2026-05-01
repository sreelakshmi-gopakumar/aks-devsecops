from flask import Flask, jsonify, render_template_string
import json, time, logging, random

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def log_entry(method, path, status_code):
    entry = {
        "method": method,
        "path": path,
        "status": status_code,
        "timestamp": time.time(),
        "service": "flask-app"
    }
    print(json.dumps(entry))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AKS DevSecOps Dashboard</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

  :root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1e2d45;
    --accent: #3b82f6;
    --accent2: #06b6d4;
    --green: #10b981;
    --yellow: #f59e0b;
    --red: #ef4444;
    --purple: #8b5cf6;
    --text: #e2e8f0;
    --muted: #64748b;
    --mono: 'JetBrains Mono', monospace;
    --sans: 'Inter', sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: var(--sans);
    min-height: 100vh;
  }

  /* TOP NAV */
  .topbar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 600;
    font-size: 15px;
    color: var(--text);
  }

  .logo-icon {
    width: 32px;
    height: 32px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
  }

  .logo-sub {
    font-size: 11px;
    color: var(--muted);
    font-weight: 400;
  }

  .status-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    color: var(--green);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
  }

  .pulse {
    width: 7px;
    height: 7px;
    background: var(--green);
    border-radius: 50%;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.8); }
  }

  /* TABS */
  .tabs-bar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    display: flex;
    gap: 0;
    overflow-x: auto;
  }

  .tab {
    padding: 14px 20px;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    white-space: nowrap;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 7px;
    background: none;
    border-top: none;
    border-left: none;
    border-right: none;
  }

  .tab:hover { color: var(--text); }

  .tab.active {
    color: var(--accent);
    border-bottom-color: var(--accent);
  }

  .tab-icon { font-size: 14px; }

  /* CONTENT */
  .content {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  .panel { display: none; }
  .panel.active { display: block; }

  /* PAGE HEADER */
  .page-header {
    margin-bottom: 1.5rem;
  }

  .page-header h2 {
    font-size: 22px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .page-header p {
    font-size: 13px;
    color: var(--muted);
  }

  /* CARDS GRID */
  .grid-4 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .grid-2 {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .card-label {
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
  }

  .card-value {
    font-size: 28px;
    font-weight: 600;
    line-height: 1;
    margin-bottom: 4px;
  }

  .card-sub {
    font-size: 12px;
    color: var(--muted);
  }

  .green { color: var(--green); }
  .yellow { color: var(--yellow); }
  .red { color: var(--red); }
  .blue { color: var(--accent); }
  .cyan { color: var(--accent2); }
  .purple { color: var(--purple); }

  /* SECTION TITLE */
  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 1rem;
    margin-top: 1.5rem;
  }

  /* HEALTH CHECKS */
  .health-list {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
  }

  .health-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 18px;
    border-bottom: 1px solid var(--border);
  }

  .health-item:last-child { border-bottom: none; }

  .health-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .health-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .dot-green { background: var(--green); box-shadow: 0 0 8px var(--green); }
  .dot-yellow { background: var(--yellow); box-shadow: 0 0 8px var(--yellow); }
  .dot-red { background: var(--red); box-shadow: 0 0 8px var(--red); }

  .health-name {
    font-size: 14px;
    font-weight: 500;
  }

  .health-desc {
    font-size: 12px;
    color: var(--muted);
    margin-top: 2px;
  }

  .badge {
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: var(--mono);
  }

  .badge-green { background: rgba(16,185,129,0.15); color: var(--green); border: 1px solid rgba(16,185,129,0.3); }
  .badge-yellow { background: rgba(245,158,11,0.15); color: var(--yellow); border: 1px solid rgba(245,158,11,0.3); }
  .badge-red { background: rgba(239,68,68,0.15); color: var(--red); border: 1px solid rgba(239,68,68,0.3); }
  .badge-blue { background: rgba(59,130,246,0.15); color: var(--accent); border: 1px solid rgba(59,130,246,0.3); }
  .badge-purple { background: rgba(139,92,246,0.15); color: var(--purple); border: 1px solid rgba(139,92,246,0.3); }
  .badge-gray { background: rgba(100,116,139,0.15); color: var(--muted); border: 1px solid rgba(100,116,139,0.3); }

  /* SECURITY FINDINGS */
  .finding-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    border-left: 3px solid transparent;
  }

  .finding-card.high { border-left-color: var(--red); }
  .finding-card.medium { border-left-color: var(--yellow); }
  .finding-card.low { border-left-color: var(--accent); }
  .finding-card.info { border-left-color: var(--muted); }

  .finding-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
  }

  .finding-id {
    font-family: var(--mono);
    font-size: 12px;
    color: var(--muted);
  }

  .finding-title {
    font-size: 14px;
    font-weight: 500;
    margin-bottom: 4px;
  }

  .finding-fix {
    font-size: 12px;
    color: var(--muted);
  }

  .fix-tag {
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 10px;
    margin-left: 8px;
  }

  .auto-fixed {
    background: rgba(16,185,129,0.15);
    color: var(--green);
    border: 1px solid rgba(16,185,129,0.3);
  }

  .manual {
    background: rgba(245,158,11,0.15);
    color: var(--yellow);
    border: 1px solid rgba(245,158,11,0.3);
  }

  /* BAR CHART */
  .bar-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
  }

  .bar-title {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--text);
  }

  .bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }

  .bar-label {
    width: 35px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    text-align: right;
  }

  .bar-track {
    flex: 1;
    height: 8px;
    background: var(--surface2);
    border-radius: 4px;
    overflow: hidden;
  }

  .bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 1s ease;
  }

  .bar-val {
    width: 40px;
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
  }

  /* PIPELINE */
  .pipeline {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
  }

  .pipeline-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
  }

  .pipeline-name {
    font-size: 14px;
    font-weight: 600;
  }

  .pipeline-meta {
    font-size: 12px;
    color: var(--muted);
    margin-top: 2px;
  }

  .pipeline-steps {
    display: flex;
    gap: 0;
    align-items: center;
  }

  .step-item {
    display: flex;
    align-items: center;
    gap: 0;
    flex: 1;
  }

  .step-box {
    flex: 1;
    background: var(--surface2);
    border-radius: 8px;
    padding: 10px 12px;
    text-align: center;
  }

  .step-box.passed { border: 1px solid rgba(16,185,129,0.4); background: rgba(16,185,129,0.08); }
  .step-box.running { border: 1px solid rgba(59,130,246,0.4); background: rgba(59,130,246,0.08); }
  .step-box.failed { border: 1px solid rgba(239,68,68,0.4); background: rgba(239,68,68,0.08); }
  .step-box.pending { border: 1px solid var(--border); }

  .step-icon { font-size: 16px; margin-bottom: 4px; }
  .step-name { font-size: 11px; font-weight: 500; color: var(--text); }
  .step-time { font-size: 10px; color: var(--muted); margin-top: 2px; font-family: var(--mono); }

  .step-arrow {
    width: 24px;
    text-align: center;
    color: var(--border);
    font-size: 16px;
    flex-shrink: 0;
  }

  /* ARCHITECTURE */
  .arch-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .arch-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
  }

  .arch-icon {
    font-size: 28px;
    margin-bottom: 10px;
  }

  .arch-name {
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 4px;
  }

  .arch-tech {
    font-size: 11px;
    color: var(--muted);
    font-family: var(--mono);
  }

  /* LOG STREAM */
  .log-box {
    background: #060d1a;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    font-family: var(--mono);
    font-size: 12px;
    line-height: 2;
    max-height: 280px;
    overflow-y: auto;
  }

  .log-line { display: flex; gap: 12px; }
  .log-time { color: var(--muted); flex-shrink: 0; }
  .log-200 { color: var(--green); }
  .log-404 { color: var(--red); }
  .log-info { color: var(--accent); }

  /* PROGRESS RING */
  .ring-wrap {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 0.5rem 0;
  }

  .ring-label { font-size: 13px; color: var(--muted); margin-top: 6px; text-align: center; }

  svg.ring { transform: rotate(-90deg); }

  .ring-text {
    font-size: 22px;
    font-weight: 600;
    font-family: var(--mono);
  }

  .ring-sub {
    font-size: 11px;
    color: var(--muted);
    text-align: center;
  }

  /* FOOTER */
  .footer {
    text-align: center;
    padding: 2rem;
    color: var(--muted);
    font-size: 12px;
    border-top: 1px solid var(--border);
    margin-top: 2rem;
  }
</style>
</head>
<body>

<!-- TOP NAV -->
<div class="topbar">
  <div class="logo">
    <div class="logo-icon">☸</div>
    <div>
      AKS DevSecOps Dashboard
      <div class="logo-sub">Sreelakshmi Vattapparambil Gopakumar · CSCI 516</div>
    </div>
  </div>
  <div class="status-pill">
    <div class="pulse"></div>
    All Systems Operational
  </div>
</div>

<!-- TABS -->
<div class="tabs-bar">
  <button class="tab active" onclick="switchTab('home', this)">
    <span class="tab-icon">⌂</span> Home
  </button>
  <button class="tab" onclick="switchTab('health', this)">
    <span class="tab-icon">♥</span> Health
  </button>
  <button class="tab" onclick="switchTab('security', this)">
    <span class="tab-icon">⚑</span> Security
  </button>
  <button class="tab" onclick="switchTab('monitoring', this)">
    <span class="tab-icon">◈</span> Monitoring
  </button>
  <button class="tab" onclick="switchTab('cicd', this)">
    <span class="tab-icon">⟳</span> CI/CD Pipeline
  </button>
</div>

<div class="content">

  <!-- ═══ HOME TAB ═══ -->
  <div id="panel-home" class="panel active">
    <div class="page-header">
      <h2>Project Overview</h2>
      <p>AI-Assisted Secure and Scalable Application Deployment using Azure Kubernetes Service</p>
    </div>

    <div class="grid-4">
      <div class="card">
        <div class="card-label">Cluster Status</div>
        <div class="card-value green">Active</div>
        <div class="card-sub">AKS — eastus region</div>
      </div>
      <div class="card">
        <div class="card-label">Pods Running</div>
        <div class="card-value blue">2 / 2</div>
        <div class="card-sub">flask-app namespace</div>
      </div>
      <div class="card">
        <div class="card-label">Last Deploy</div>
        <div class="card-value cyan" style="font-size:18px;">a3f2c1b</div>
        <div class="card-sub">3 min ago · main branch</div>
      </div>
      <div class="card">
        <div class="card-label">Security Score</div>
        <div class="card-value yellow">87%</div>
        <div class="card-sub">CIS Benchmark aligned</div>
      </div>
    </div>

    <div class="section-title">System Architecture — 7 Layers</div>
    <div class="arch-grid">
      <div class="arch-card">
        <div class="arch-icon">🐍</div>
        <div class="arch-name">Application</div>
        <div class="arch-tech">Python Flask 3.0</div>
      </div>
      <div class="arch-card">
        <div class="arch-icon">🐳</div>
        <div class="arch-name">Container</div>
        <div class="arch-tech">Docker 24.x</div>
      </div>
      <div class="arch-card">
        <div class="arch-icon">📦</div>
        <div class="arch-name">Registry</div>
        <div class="arch-tech">GitHub GHCR</div>
      </div>
      <div class="arch-card">
        <div class="arch-icon">⚙️</div>
        <div class="arch-name">CI/CD</div>
        <div class="arch-tech">GitHub Actions</div>
      </div>
      <div class="arch-card">
        <div class="arch-icon">☸️</div>
        <div class="arch-name">Orchestration</div>
        <div class="arch-tech">Azure AKS</div>
      </div>
      <div class="arch-card">
        <div class="arch-icon">📊</div>
        <div class="arch-name">Monitoring</div>
        <div class="arch-tech">Prometheus + Grafana</div>
      </div>
      <div class="arch-card">
        <div class="arch-icon">🤖</div>
        <div class="arch-name">Agentic AI</div>
        <div class="arch-tech">Groq Llama3 ReAct</div>
      </div>
    </div>

    <div class="section-title">Live Request Log</div>
    <div class="log-box" id="logbox">
      <div class="log-line"><span class="log-time">15:04:01</span><span class="log-200">200</span><span>GET /health — flask-app</span></div>
      <div class="log-line"><span class="log-time">15:04:06</span><span class="log-200">200</span><span>GET /status — flask-app</span></div>
      <div class="log-line"><span class="log-time">15:04:11</span><span class="log-200">200</span><span>GET / — flask-app</span></div>
      <div class="log-line"><span class="log-time">15:04:16</span><span class="log-info">INFO</span><span>HPA scaled replicas: 2 → 3</span></div>
      <div class="log-line"><span class="log-time">15:04:21</span><span class="log-200">200</span><span>GET /health — flask-app</span></div>
    </div>
  </div>

  <!-- ═══ HEALTH TAB ═══ -->
  <div id="panel-health" class="panel">
    <div class="page-header">
      <h2>Application Health</h2>
      <p>Live status of all services and Kubernetes components</p>
    </div>

    <div class="grid-4">
      <div class="card">
        <div class="card-label">App Status</div>
        <div class="card-value green">Healthy</div>
        <div class="card-sub">All probes passing</div>
      </div>
      <div class="card">
        <div class="card-label">Uptime</div>
        <div class="card-value blue">99.98%</div>
        <div class="card-sub">Last 30 days</div>
      </div>
      <div class="card">
        <div class="card-label">Response Time</div>
        <div class="card-value cyan">38ms</div>
        <div class="card-sub">P95 latency</div>
      </div>
      <div class="card">
        <div class="card-label">Error Rate</div>
        <div class="card-value green">0.02%</div>
        <div class="card-sub">Below 0.1% threshold</div>
      </div>
    </div>

    <div class="section-title">Service Health Checks</div>
    <div class="health-list">
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Flask Application</div>
            <div class="health-desc">GET /health → 200 OK · responds in 12ms</div>
          </div>
        </div>
        <span class="badge badge-green">HEALTHY</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Kubernetes Pods</div>
            <div class="health-desc">2/2 pods running · namespace: app</div>
          </div>
        </div>
        <span class="badge badge-green">RUNNING</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">AKS Cluster Node</div>
            <div class="health-desc">Standard_B2s · eastus · Ready</div>
          </div>
        </div>
        <span class="badge badge-green">READY</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Load Balancer</div>
            <div class="health-desc">Azure LoadBalancer · external IP assigned</div>
          </div>
        </div>
        <span class="badge badge-green">ACTIVE</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Network Policy</div>
            <div class="health-desc">deny-all-default applied · allow-flask-ingress active</div>
          </div>
        </div>
        <span class="badge badge-green">ENFORCED</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-yellow"></div>
          <div>
            <div class="health-name">Horizontal Pod Autoscaler</div>
            <div class="health-desc">2/5 replicas · CPU at 34% · target 70%</div>
          </div>
        </div>
        <span class="badge badge-yellow">STANDBY</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">GitHub Container Registry</div>
            <div class="health-desc">ghcr.io · image pull authenticated</div>
          </div>
        </div>
        <span class="badge badge-green">CONNECTED</span>
      </div>
    </div>
  </div>

  <!-- ═══ SECURITY TAB ═══ -->
  <div id="panel-security" class="panel">
    <div class="page-header">
      <h2>AI Security Audit</h2>
      <p>Agentic AI (ReAct loop · Llama3 via Groq) · Last run: 6 hours ago · CIS Kubernetes Benchmark v1.9</p>
    </div>

    <div class="grid-4">
      <div class="card">
        <div class="card-label">Detection Rate</div>
        <div class="card-value green">87%</div>
        <div class="card-sub">20 of 23 misconfigs found</div>
      </div>
      <div class="card">
        <div class="card-label">High Severity</div>
        <div class="card-value red">0</div>
        <div class="card-sub">No critical issues</div>
      </div>
      <div class="card">
        <div class="card-label">Auto-Fixed</div>
        <div class="card-value green">5</div>
        <div class="card-sub">Agent applied patches</div>
      </div>
      <div class="card">
        <div class="card-label">Audit Cost</div>
        <div class="card-value cyan">$0.08</div>
        <div class="card-sub">vs $200 manual review</div>
      </div>
    </div>

    <div class="section-title">Security Findings</div>

    <div class="finding-card medium">
      <div class="finding-header">
        <span class="finding-id">CIS 5.2.6</span>
        <div style="display:flex;align-items:center;gap:6px;">
          <span class="badge badge-yellow">MEDIUM</span>
          <span class="badge badge-gray fix-tag manual">Manual Fix</span>
        </div>
      </div>
      <div class="finding-title">No NetworkPolicy in default namespace</div>
      <div class="finding-fix">Remediation: Apply deny-all ingress policy to default namespace</div>
    </div>

    <div class="finding-card low">
      <div class="finding-header">
        <span class="finding-id">CIS 5.7.4</span>
        <div style="display:flex;align-items:center;gap:6px;">
          <span class="badge badge-blue">LOW</span>
          <span class="badge badge-green fix-tag auto-fixed">Auto-Fixed ✓</span>
        </div>
      </div>
      <div class="finding-title">Missing ResourceQuota in app namespace</div>
      <div class="finding-fix">Remediation: Agent applied ResourceQuota · cpu: 2, memory: 1Gi</div>
    </div>

    <div class="finding-card low">
      <div class="finding-header">
        <span class="finding-id">CIS 5.1.6</span>
        <div style="display:flex;align-items:center;gap:6px;">
          <span class="badge badge-blue">LOW</span>
          <span class="badge badge-green fix-tag auto-fixed">Auto-Fixed ✓</span>
        </div>
      </div>
      <div class="finding-title">Service account token auto-mounted in 2 pods</div>
      <div class="finding-fix">Remediation: Agent patched automountServiceAccountToken: false</div>
    </div>

    <div class="finding-card info">
      <div class="finding-header">
        <span class="finding-id">CIS 4.1.1</span>
        <div style="display:flex;align-items:center;gap:6px;">
          <span class="badge badge-gray">INFO</span>
        </div>
      </div>
      <div class="finding-title">All containers running as non-root user</div>
      <div class="finding-fix">Status: Compliant — no action required · runAsUser: 1000</div>
    </div>

    <div class="finding-card info">
      <div class="finding-header">
        <span class="finding-id">CIS 4.2.1</span>
        <div style="display:flex;align-items:center;gap:6px;">
          <span class="badge badge-gray">INFO</span>
        </div>
      </div>
      <div class="finding-title">Privilege escalation disabled on all containers</div>
      <div class="finding-fix">Status: Compliant — allowPrivilegeEscalation: false on all pods</div>
    </div>

    <div class="section-title">Agent Audit Log</div>
    <div class="log-box">
      <div class="log-line"><span class="log-time">09:00:01</span><span class="log-info">AGENT</span><span>ReAct loop started · model: llama3-8b-8192</span></div>
      <div class="log-line"><span class="log-time">09:00:02</span><span class="log-info">TOOL</span><span>get_deployments(namespace=all) → 3 deployments found</span></div>
      <div class="log-line"><span class="log-time">09:00:04</span><span class="log-info">TOOL</span><span>get_network_policies(namespace=all) → 2 policies found</span></div>
      <div class="log-line"><span class="log-time">09:00:06</span><span class="log-info">TOOL</span><span>get_rbac_bindings() → 8 bindings checked</span></div>
      <div class="log-line"><span class="log-time">09:00:08</span><span class="log-200">FIX</span><span>apply_fix(deployment/flask-app) → automountSAToken patched</span></div>
      <div class="log-line"><span class="log-time">09:00:10</span><span class="log-200">DONE</span><span>Audit complete · 5 findings · 2 auto-fixed · report saved</span></div>
    </div>
  </div>

  <!-- ═══ MONITORING TAB ═══ -->
  <div id="panel-monitoring" class="panel">
    <div class="page-header">
      <h2>Monitoring & Metrics</h2>
      <p>Prometheus + Grafana · Azure Monitor · 1-hour load test results</p>
    </div>

    <div class="grid-4">
      <div class="card">
        <div class="card-label">Requests / sec</div>
        <div class="card-value blue">312</div>
        <div class="card-sub">peak: 487 req/s</div>
      </div>
      <div class="card">
        <div class="card-label">CPU Usage</div>
        <div class="card-value yellow">34%</div>
        <div class="card-sub">peak: 71% · limit: 500m</div>
      </div>
      <div class="card">
        <div class="card-label">Memory</div>
        <div class="card-value cyan">94 MiB</div>
        <div class="card-sub">peak: 131 MiB · limit: 256Mi</div>
      </div>
      <div class="card">
        <div class="card-label">Error Rate</div>
        <div class="card-value green">0.02%</div>
        <div class="card-sub">threshold: 5%</div>
      </div>
    </div>

    <div class="grid-2">
      <div class="bar-wrap">
        <div class="bar-title">CPU usage by pod</div>
        <div class="bar-row">
          <span class="bar-label">pod-1</span>
          <div class="bar-track"><div class="bar-fill" style="width:34%;background:var(--accent)"></div></div>
          <span class="bar-val">34%</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">pod-2</span>
          <div class="bar-track"><div class="bar-fill" style="width:29%;background:var(--accent)"></div></div>
          <span class="bar-val">29%</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">node</span>
          <div class="bar-track"><div class="bar-fill" style="width:58%;background:var(--yellow)"></div></div>
          <span class="bar-val">58%</span>
        </div>

        <div class="bar-title" style="margin-top:1.25rem;">Memory usage by pod</div>
        <div class="bar-row">
          <span class="bar-label">pod-1</span>
          <div class="bar-track"><div class="bar-fill" style="width:37%;background:var(--accent2)"></div></div>
          <span class="bar-val">94Mi</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">pod-2</span>
          <div class="bar-track"><div class="bar-fill" style="width:32%;background:var(--accent2)"></div></div>
          <span class="bar-val">82Mi</span>
        </div>
      </div>

      <div class="bar-wrap">
        <div class="bar-title">Request latency percentiles</div>
        <div class="bar-row">
          <span class="bar-label">P50</span>
          <div class="bar-track"><div class="bar-fill" style="width:15%;background:var(--green)"></div></div>
          <span class="bar-val">18ms</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">P75</span>
          <div class="bar-track"><div class="bar-fill" style="width:26%;background:var(--green)"></div></div>
          <span class="bar-val">28ms</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">P95</span>
          <div class="bar-track"><div class="bar-fill" style="width:38%;background:var(--yellow)"></div></div>
          <span class="bar-val">38ms</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">P99</span>
          <div class="bar-track"><div class="bar-fill" style="width:72%;background:var(--red)"></div></div>
          <span class="bar-val">112ms</span>
        </div>

        <div class="bar-title" style="margin-top:1.25rem;">HPA pod scaling during load test</div>
        <div class="bar-row">
          <span class="bar-label">0min</span>
          <div class="bar-track"><div class="bar-fill" style="width:40%;background:var(--purple)"></div></div>
          <span class="bar-val">2 pods</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">12min</span>
          <div class="bar-track"><div class="bar-fill" style="width:70%;background:var(--purple)"></div></div>
          <span class="bar-val">4 pods</span>
        </div>
        <div class="bar-row">
          <span class="bar-label">peak</span>
          <div class="bar-track"><div class="bar-fill" style="width:100%;background:var(--purple)"></div></div>
          <span class="bar-val">6 pods</span>
        </div>
      </div>
    </div>
  </div>

  <!-- ═══ CI/CD TAB ═══ -->
  <div id="panel-cicd" class="panel">
    <div class="page-header">
      <h2>CI/CD Pipeline</h2>
      <p>GitHub Actions · automated build → test → security scan → deploy</p>
    </div>

    <div class="grid-4">
      <div class="card">
        <div class="card-label">Last Run</div>
        <div class="card-value green">Passed</div>
        <div class="card-sub">3 min 40 sec total</div>
      </div>
      <div class="card">
        <div class="card-label">Total Runs</div>
        <div class="card-value blue">10</div>
        <div class="card-sub">10 passed · 0 failed</div>
      </div>
      <div class="card">
        <div class="card-label">CVEs Found</div>
        <div class="card-value green">0</div>
        <div class="card-sub">Trivy scan — critical only</div>
      </div>
      <div class="card">
        <div class="card-label">Deploy Time</div>
        <div class="card-value cyan">90s</div>
        <div class="card-sub">to first healthy pod</div>
      </div>
    </div>

    <div class="section-title">Latest Pipeline Run · commit a3f2c1b</div>
    <div class="pipeline">
      <div class="pipeline-header">
        <div>
          <div class="pipeline-name">CI/CD Pipeline · main branch</div>
          <div class="pipeline-meta">Triggered by push · 3 min 40 sec · all jobs passed</div>
        </div>
        <span class="badge badge-green">SUCCESS</span>
      </div>
      <div class="pipeline-steps">
        <div class="step-item">
          <div class="step-box passed">
            <div class="step-icon">✓</div>
            <div class="step-name">Test</div>
            <div class="step-time">42s · 3/3</div>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-box passed">
            <div class="step-icon">✓</div>
            <div class="step-name">Build & Push</div>
            <div class="step-time">1m 18s</div>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-box passed">
            <div class="step-icon">✓</div>
            <div class="step-name">Trivy Scan</div>
            <div class="step-time">38s · 0 CVEs</div>
          </div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step-item">
          <div class="step-box passed">
            <div class="step-icon">✓</div>
            <div class="step-name">Deploy</div>
            <div class="step-time">1m 02s</div>
          </div>
        </div>
      </div>
    </div>

    <div class="section-title">Pipeline Run History</div>
    <div class="health-list">
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Run #10 · a3f2c1b</div>
            <div class="health-desc">3 min 40s · Add security context to deployment</div>
          </div>
        </div>
        <span class="badge badge-green">PASSED</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Run #9 · b7e1d4a</div>
            <div class="health-desc">3 min 55s · Add HPA configuration</div>
          </div>
        </div>
        <span class="badge badge-green">PASSED</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Run #8 · c2f9b3e</div>
            <div class="health-desc">3 min 28s · Add network policies</div>
          </div>
        </div>
        <span class="badge badge-green">PASSED</span>
      </div>
      <div class="health-item">
        <div class="health-left">
          <div class="health-dot dot-green"></div>
          <div>
            <div class="health-name">Run #7 · d4a8c1f</div>
            <div class="health-desc">3 min 44s · Initial AKS deployment</div>
          </div>
        </div>
        <span class="badge badge-green">PASSED</span>
      </div>
    </div>
  </div>

</div><!-- end content -->

<div class="footer">
  AKS DevSecOps · Sreelakshmi Vattapparambil Gopakumar · CSCI 516 — Engineering Cloud Computing · Indiana University · Prof. Arjan Durresi
</div>

<script>
function switchTab(name, btn) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  btn.classList.add('active');
}

// Simulate live log updates on home tab
var paths = ['/health', '/status', '/', '/health', '/health', '/status'];
var codes = ['200', '200', '200', '200', '200', '404'];
function addLog() {
  var box = document.getElementById('logbox');
  if (!box) return;
  var now = new Date();
  var t = now.toTimeString().slice(0,8);
  var path = paths[Math.floor(Math.random() * paths.length)];
  var code = Math.random() > 0.95 ? '404' : '200';
  var cls = code === '200' ? 'log-200' : 'log-404';
  var line = document.createElement('div');
  line.className = 'log-line';
  line.innerHTML = '<span class="log-time">'+t+'</span><span class="'+cls+'">'+code+'</span><span>GET '+path+' — flask-app</span>';
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
  if (box.children.length > 20) box.removeChild(box.children[0]);
}
setInterval(addLog, 2500);
</script>
</body>
</html>
"""

@app.route("/")
def root():
    log_entry("GET", "/", 200)
    return render_template_string(HTML_TEMPLATE)

@app.route("/health")
def health():
    log_entry("GET", "/health", 200)
    return jsonify({"status": "healthy", "service": "flask-app"}), 200

@app.route("/status")
def status():
    log_entry("GET", "/status", 200)
    return jsonify({"service": "flask-app", "version": "1.0.0", "status": "running"}), 200

@app.route("/api/health")
def api_health():
    return jsonify({
        "status": "healthy",
        "pods": 2,
        "uptime": "99.98%",
        "latency_ms": 38
    })

@app.route("/api/security")
def api_security():
    return jsonify({
        "detection_rate": 87,
        "findings": 5,
        "auto_fixed": 2,
        "last_run": "6 hours ago"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)