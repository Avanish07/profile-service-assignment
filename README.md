# Profile Service

A production-ready Kubernetes deployment of a small FastAPI profile service.
The application itself is intentionally simple (profile CRUD plus
health/readiness/metrics endpoints); this repository focuses on the DevOps,
SRE, security, and operability work around it.

## What's Included

```
Dockerfile            Multi-stage, non-root container image
.dockerignore         Keeps secrets and local state out of the build
helm/profile-service  Helm chart: Deployment, Service, ConfigMap, Secret,
                      ServiceAccount, HPA, Ingress
.github/workflows/    ci.yaml     - lint, test, docker build, Trivy scan, helm validate
                      deploy.yaml - build & push (SHA tag), staging, gated production
terraform/            IaC skeleton: namespace module + dev/staging/prod environments
docs/                 architecture, observability, security, runbook, incident-response
```

## Quick Start (local, minikube)

Build the image and load it into minikube:

```bash
podman build -t profile-service:local .
podman save -o profile-service.tar localhost/profile-service:local
minikube image load profile-service.tar
```

Deploy with Helm:

```bash
helm upgrade --install profile-service ./helm/profile-service \
  --namespace profile-service --create-namespace
```

Verify:

```bash
kubectl -n profile-service get pods
kubectl -n profile-service port-forward svc/profile-service 8080:80
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz
curl http://localhost:8080/profiles
```

The pods should be `1/1 Running`, and `/readyz` should return `ready` (it checks
the database connection).

## Run the App Directly (without Kubernetes)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest -q
```

## CI/CD

- **CI (`ci.yaml`)** runs on every pull request: Ruff lint, pytest, a Docker
  build, a Trivy image scan (fails on CRITICAL/HIGH), and Helm lint/template.
- **Deploy (`deploy.yaml`)** runs on merge to main: builds an image tagged with
  the commit SHA, pushes it to GHCR, deploys to staging, then waits for manual
  approval before production. The production gate uses a protected GitHub
  Environment, so it must be created in repo Settings → Environments (with a
  required reviewer) for the approval step to pause.

## Key Design Decisions

- **Non-root container with a writable volume.** The app runs as UID 10001. It
  writes its SQLite database to `/data`, which is a mounted volume so it stays
  writable under a non-root user (and so the rest of the filesystem can later be
  made read-only).
- **Service targetPort matches the container port (8000).** A mismatch here is
  a common cause of 502s through the ingress; see `docs/incident-response.md`.
- **Config split.** Non-sensitive config in a ConfigMap, `DATABASE_URL` in a
  Secret (a local SQLite placeholder here, never a real credential).

## Intentionally Incomplete / Assumptions

This is a broad assignment; the following are deliberate scope choices, noted
honestly:

- The deploy workflow's staging/production steps are placeholders, since there
  is no real cloud cluster to deploy to. The structure (SHA tags, staging then
  gated production) is complete.
- The Terraform skeleton provisions a real Kubernetes namespace (works on
  minikube). Cloud resources (container registry, IAM/IRSA, secret manager) are
  documented as placeholders rather than implemented, since they need a paid
  cloud account.
- NetworkPolicy and read-only root filesystem are documented as next steps in
  `docs/security.md`, not yet implemented.
- The app uses SQLite for local simplicity. A real deployment would use a
  managed database with proper migrations instead of creating the schema on
  startup.

## Documentation

- `docs/architecture.md` — design, deployment flow, runtime flow, tradeoffs
- `docs/observability.md` — metrics, logs, alerts, SLOs, debugging
- `docs/security.md` — container, Kubernetes, and CI/CD hardening
- `docs/runbook.md` — deploy, verify, troubleshoot, rollback
- `docs/incident-response.md` — RCA for the 502 incident scenario