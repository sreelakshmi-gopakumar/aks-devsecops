# AKS DevSecOps Project

**Course:** CSCI 516 — Engineering Cloud Computing
**Student:** Sreelakshmi Vattapparambil Gopakumar
**University:** Indiana University Indianapolis
**Professor:** Prof. Arjan Durresi

---

## What this project does

This project deploys a Python web application to Microsoft Azure using Kubernetes. The interesting part is that the whole process — building, testing, scanning for security issues, and deploying — happens automatically whenever code is pushed to GitHub. There's also an AI agent that scans the cluster every 6 hours and fixes security problems on its own.

**Live app:** http://48.211.157.190

---

## How it's built — 7 layers

Each layer has one job:

| Layer | Tool | What it does |
|-------|------|-------------|
| App | Python Flask | Serves the web dashboard |
| Container | Docker | Packages the app so it runs the same everywhere |
| Registry | GitHub GHCR | Stores the Docker image online |
| CI/CD | GitHub Actions | Runs tests and deploys automatically on every push |
| Cluster | Azure AKS | Runs and manages the containers in the cloud |
| Monitoring | Prometheus + Grafana | Tracks CPU, memory, and traffic in real time |
| Security | Agentic AI (Llama3.3-70b) | Scans for misconfigurations and fixes them automatically |

---

## Running it locally

You'll need Python 3.11, Docker Desktop, Azure CLI, and kubectl installed.

**Start the Flask app:**
```bash
cd app
pip install -r requirements.txt
python app.py
```
Then open http://localhost:5000 in your browser.

**Run the tests:**
```bash
cd app
pytest tests/ -v
```

**Build and run with Docker:**
```bash
cd app
docker build -t flask-app:local .
docker run -p 5000:5000 flask-app:local
```

---

## How the CI/CD pipeline works

The idea is that you never deploy directly from your laptop. Instead:

```
You push code to the dev branch
        ↓
GitHub runs your tests, builds the Docker image,
and scans it for security vulnerabilities
        ↓
If everything passes, you merge dev into main
        ↓
GitHub automatically deploys the new version to Azure
```

Pushing to `dev` is safe — it runs checks but never touches the live app.
Merging to `main` is the deploy trigger.

---

## Monitoring

Prometheus collects metrics from the cluster every 15 seconds.
Grafana turns those into charts you can actually read.

To open the Grafana dashboard:
```bash
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
```
Then go to http://localhost:3000 and log in with `admin` / `Admin123!`

You'll find pre-built dashboards under Dashboards → Kubernetes showing
CPU usage, memory, network traffic, and pod health for the `app` namespace.

---

## The AI security agent

This is the most interesting part of the project.

Most security tools just scan and report — you still have to fix things manually.
This agent actually does something about what it finds.

It works in a loop:
1. Reads the cluster configuration using kubectl
2. Sends it to an LLM (Llama3.3-70b via Groq) which decides what to check next
3. The LLM calls tools — like `get_deployments` or `get_network_policies`
4. If it finds a LOW or MEDIUM severity issue, it applies a fix automatically
5. It logs everything and keeps going until the audit is done

This is called a ReAct loop (Reasoning + Acting). The difference from a regular
LLM call is that the model drives the whole process — it decides what to look at,
in what order, and what to do about what it finds. It runs as a scheduled job
inside the cluster every 6 hours.

---

## API endpoints

| URL | What it returns |
|-----|----------------|
| `/` | The dashboard UI |
| `/health` | Health check (used by Kubernetes internally) |
| `/status` | App version and status |
| `/api/info` | Project details as JSON |
| `/api/health` | Health data as JSON |
| `/api/security` | Latest security audit summary |

---

## Project structure

```
aks-devsecops/
├── app/
│   ├── app.py              main Flask app and dashboard UI
│   ├── Dockerfile          two-stage container build
│   ├── requirements.txt    Flask and gunicorn
│   └── tests/
│       └── test_app.py     four pytest tests
├── k8s/
│   ├── deployment.yaml     how many pods to run and how
│   ├── service.yaml        public IP and load balancer
│   ├── namespace.yaml      separate areas inside the cluster
│   ├── networkpolicy.yaml  blocks all traffic except what's needed
│   └── hpa.yaml            scales pods up when traffic increases
├── security/
│   └── agent.py            the AI security agent
└── .github/workflows/
    └── deploy.yml          the CI/CD pipeline
```