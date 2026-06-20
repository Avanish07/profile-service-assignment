# DevOps Assignment: Productionize the Profile Service

## Context

You have been given a small profile service. Treat it as a new microservice that needs to be prepared for production deployment.

The application code is intentionally simple. The goal of this assignment is to evaluate your DevOps, SRE, Kubernetes, CI/CD, security, observability, and documentation skills.

## Expectation

This assignment is intentionally broad. You do not need to complete every task perfectly. We are more interested in your approach, assumptions, trade-offs, and reasoning. A well-documented partial solution is completely acceptable.

You do not need to deploy to a paid cloud account. Your work should be reviewable locally using kind, minikube, Docker Desktop Kubernetes, or clear dry-run instructions.

## Your deliverables

Submit your work as a GitHub repository or a zipped folder. The submission must include:

1. A production-ready Dockerfile.
2. Kubernetes manifests, Helm chart, or Kustomize overlays.
3. GitHub Actions workflows for CI and deployment.
4. Infrastructure-as-Code skeleton using Terraform, Bicep, Pulumi, or another clear IaC tool.
5. Security hardening for container and Kubernetes deployment.
6. Observability plan with metrics, logs, dashboards, and alerts.
7. Runbook and rollback instructions.
8. A short architecture document.
9. A short RCA-style response for the incident scenario in `docs/INCIDENT_SCENARIO.md`.

## Application behavior

The service exposes these endpoints:

- `GET /healthz`: process health.
- `GET /readyz`: dependency readiness check.
- `GET /metrics`: Prometheus-compatible metrics.
- `GET /profiles`: list profiles.
- `POST /profiles`: create a profile.
- `GET /profiles/{user_id}`: read a profile.
- `PUT /profiles/{user_id}`: update a profile.
- `DELETE /profiles/{user_id}`: delete a profile.

## Task 1: Containerization

Create a Dockerfile suitable for production.

Minimum expectations:

- Uses a reasonable minimal base image.
- Does not run as root.
- Uses deterministic dependency installation.
- Does not bake secrets into the image.
- Uses a sensible working directory.
- Exposes port 8000.
- Runs the app with a production-appropriate ASGI server command.
- Includes a `.dockerignore`.

Nice-to-have:

- Multi-stage build.
- Read-only root filesystem compatibility.
- Image labels.
- Healthcheck with explanation.
- Explanation of base image tradeoffs.

## Task 2: Kubernetes deployment

Create production-minded Kubernetes resources using either raw manifests, Helm, or Kustomize.

Minimum resources:

- Namespace.
- Deployment.
- Service.
- ConfigMap.
- Secret template or external secret reference.
- Ingress or documented ingress assumptions.
- Resource requests and limits.
- Readiness and liveness probes.
- HorizontalPodAutoscaler.

Strong submissions should also include:

- PodDisruptionBudget.
- SecurityContext at pod and container level.
- ServiceAccount with minimal permissions.
- NetworkPolicy.
- Rolling update configuration.
- Separate dev/staging/prod values or overlays.

Important: do not put real secrets in the repository.

## Task 3: CI/CD

Create GitHub Actions workflows.

Minimum PR checks:

- Lint or formatting check.
- Unit tests.
- Docker image build.
- Kubernetes/Helm manifest validation.

Minimum main branch behavior:

- Build and tag image using commit SHA.
- Push image to a registry placeholder.
- Deploy to staging or update deployment manifests.
- Require manual approval before production deployment.

Security checks expected:

- Dependency scanning or SCA.
- Container image scanning.
- Secret scanning or documented strategy.

Preferred:

- OIDC/federated cloud authentication instead of long-lived credentials.
- GitHub environments for staging and production.
- GitOps-compatible deployment option.
- Clear rollback step.

## Task 4: Infrastructure as Code

Provide an IaC skeleton. It does not need to create a real cloud cluster.

Minimum expectations:

- Clear folder structure.
- Environment separation for dev/staging/prod.
- Variables and outputs.
- Remote state strategy explained.
- Placeholder resources for container registry, Kubernetes namespace, service account/identity, and secret integration.

You may use Terraform, Bicep, Pulumi, or another IaC tool. Choose one and explain your choice.

## Task 5: Observability

Create a document named `docs/observability.md`.

It must include:

- Metrics to collect.
- Logs to collect.
- Example alerts.
- Dashboard outline.
- SLO proposal.
- How to debug high latency, high 5xx, and pod restarts.

Expected metrics include:

- Request rate.
- p95/p99 latency.
- 4xx and 5xx error rate.
- Pod restarts.
- CPU and memory usage.
- HPA scaling activity.
- Database readiness failures.
- Ingress 4xx/5xx if ingress is included.

## Task 6: Security hardening

Create a document named `docs/security.md` and implement relevant hardening in your manifests.

Minimum expectations:

- No hardcoded credentials.
- Non-root container.
- Dropped Linux capabilities where possible.
- Read-only root filesystem where possible.
- Resource limits.
- Minimal RBAC.
- Image scanning in CI.
- Secret management strategy.

Bonus:

- External Secrets Operator or cloud secret manager integration design.
- SBOM generation.
- Admission policy considerations.
- NetworkPolicy with clear traffic rules.

## Task 7: Runbook and rollback

Create `docs/runbook.md`.

It must include:

- How to deploy.
- How to verify deployment.
- How to inspect pods, services, ingress, and logs.
- How to roll back.
- How to handle failed readiness probes.
- How to handle high error rate.
- How to handle database connectivity failure.

## Task 8: Architecture note

Create `docs/architecture.md`.

It must include:

- One architecture diagram or text diagram.
- Deployment flow.
- Runtime flow.
- Environment separation.
- Security and secret handling.
- Tradeoffs and assumptions.

## Task 9: Incident scenario

Read `docs/INCIDENT_SCENARIO.md` and provide your RCA-style response in `docs/incident-response.md`.

Your response should include:

- Symptoms.
- Immediate mitigation.
- Investigation commands.
- Root cause hypothesis.
- Fix.
- Prevention plan.

## Expected final structure

A strong submission may look like this:

```text
.
├── app/
├── tests/
├── Dockerfile
├── .dockerignore
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── helm/ or k8s/ or overlays/
├── terraform/ or infra/
│   ├── modules/
│   └── envs/
│       ├── dev/
│       ├── staging/
│       └── prod/
├── docs/
│   ├── architecture.md
│   ├── observability.md
│   ├── security.md
│   ├── runbook.md
│   └── incident-response.md
└── README.md
```


## What we value most

We value operational thinking over excessive tooling. A strong submission should be secure, maintainable, observable, repeatable, and easy to reason about.
