# Architecture

## Overview

The profile service is a stateless FastAPI microservice exposing profile CRUD
plus health, readiness, and metrics endpoints. It is containerised, deployed to
Kubernetes via a Helm chart, fronted by a Service (and ingress), and backed by a
database. Because all state lives in the database, the pods are disposable and
can be scaled horizontally.

## Text Diagram

```
Client
  |
  v
Ingress  (TLS termination, routing)
  |
  v
Service (ClusterIP, port 80 -> targetPort 8000)
  |
  v
Pods (uvicorn on :8000, non-root, 2..N replicas via HPA)
  |
  v
Database
```

```
CI (lint, test, build, scan, helm validate)
  -> Image Registry (tagged with commit SHA)
    -> Deploy workflow: staging -> [manual approval] -> production
```

## Deployment Flow

1. A pull request runs CI: lint and unit tests, a Docker build, a Trivy image
   scan, and Helm lint/template validation. All must pass to merge.
2. On merge to main, the deploy workflow builds an image tagged with the commit
   SHA and pushes it to the registry.
3. It deploys to staging automatically, then waits for manual approval (a
   protected GitHub Environment) before deploying to production.
4. The same immutable image is promoted through environments; nothing is rebuilt
   per environment.

## Runtime Request Flow

1. The client request reaches the ingress, which terminates TLS and routes by
   host/path.
2. The ingress forwards to the Service on port 80, which targets the container
   port 8000.
3. The Service load-balances to a Ready pod (only pods passing the readiness
   probe receive traffic).
4. uvicorn handles the request; the handler reads/writes the database and
   returns a response.
5. `/healthz` (liveness) and `/readyz` (readiness) are polled by the kubelet;
   `/metrics` is scraped by Prometheus.

## Environment Separation

Each environment (dev, staging, prod) is a separate Helm release in its own
namespace, and a separate Terraform state. Per-environment values control
replica count, resource sizes, and configuration. The same chart and the same
image are used across environments.

## Security and Secret Handling

Containers run as a non-root user, drop all Linux capabilities, and disallow
privilege escalation. Non-sensitive config is in a ConfigMap and the sensitive
`DATABASE_URL` is in a Secret. In production, secrets would come from a cloud
secret manager via the External Secrets Operator, with the workload using a
cloud identity rather than static keys. (Full detail in security.md.)

## Tradeoffs and Assumptions

- **One uvicorn process per pod, scaled via HPA** rather than many workers per
  pod — keeps each pod simple and limits the blast radius of a crash; tradeoff
  is slightly lower per-pod throughput.
- **SQLite for local/dev** to keep the assignment runnable with no external
  dependency; a real database (e.g. Postgres) would be used in staging/prod.
- **Schema is created on startup** in the starter app; in production this should
  be replaced with managed migrations (e.g. Alembic) run as a separate step.
- Assumes an ingress controller and a metrics stack exist in the cluster.

## What Would Change at 50 Microservices

- **Share the Helm chart** as a common library chart so every service inherits
  the same hardened defaults instead of copying YAML.
- **Adopt GitOps** (Argo CD / Flux) so a controller reconciles cluster state
  from git, rather than CI running helm upgrade directly.
- **Service mesh** for consistent mTLS, retries, and telemetry across services.
- **Central policy enforcement** (e.g. Kyverno) to require non-root, resource
  limits, and no `latest` tags cluster-wide.
- **Per-team namespaces with quotas** and standard golden-path templates so new
  services start from a secure, consistent baseline.