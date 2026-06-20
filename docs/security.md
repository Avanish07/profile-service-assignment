# Security Hardening

This document describes the security measures applied across the container, the
Kubernetes layer, and CI/CD, with the reasoning behind each. The approach is
defence in depth: reduce what an attacker can do at each layer.

## Container Hardening (Dockerfile)

- **Minimal base image** — `python:3.12-slim`. Smaller than the full image and
  glibc-based so Python wheels install cleanly, while keeping a shell for
  debugging.
- **Multi-stage build** — dependencies are installed in a builder stage and only
  the resulting virtualenv is copied into the runtime image, so build tooling
  and pip caches are not shipped.
- **Non-root user** — the image creates a user with a fixed UID (10001) and runs
  as that user, so a compromised container is not root.
- **Deterministic dependencies** — pinned `requirements.txt` installed at build
  time for reproducible images.
- **No secrets in the image** — `.dockerignore` excludes `.env`, `*.db`,
  `.venv`, and similar; configuration and secrets are injected at runtime via
  environment variables.
- **Writable data on a volume** — the app only needs to write to `/data`, which
  is provided by a mounted volume, keeping the rest of the filesystem clean.

## Kubernetes Hardening (Helm chart)

- **Pod and container SecurityContext:**
  - `runAsNonRoot: true`, `runAsUser: 10001` (matches the image UID)
  - `allowPrivilegeEscalation: false`
  - `capabilities: drop: [ALL]` — drop all Linux capabilities
  - `fsGroup: 10001` so the mounted `/data` volume is writable by the non-root
    user
- **Resource requests and limits** — every container has CPU/memory requests and
  a memory limit, so a single pod cannot starve the node (the memory limit also
  gives the OOM killer a hard ceiling).
- **Dedicated ServiceAccount** — the workload runs under its own ServiceAccount
  with no extra RBAC, since the app needs no Kubernetes API access.
- **Secrets vs ConfigMap** — non-sensitive config (app name, environment, log
  level) is in a ConfigMap; the sensitive `DATABASE_URL` is in a Secret.

A read-only root filesystem is a natural next step: because the only writable
path is the `/data` volume, `readOnlyRootFilesystem: true` can be enabled to
lock down the rest of the container filesystem.

## CI/CD Security

- **Image scanning** — Trivy scans the built image in CI and fails the build on
  CRITICAL/HIGH vulnerabilities (ignoring unfixed ones so PRs are not blocked on
  issues with no available patch).
- **No long-lived credentials** — the deploy workflow authenticates to the
  container registry (GHCR) using the auto-provided `GITHUB_TOKEN` plus a scoped
  `packages: write` permission, so no registry credentials are stored.
- **Immutable image tags** — images are tagged with the commit SHA, so every
  deployed image is traceable to exact code and rollbacks are unambiguous.
- **Gated production** — production deploys go through a protected GitHub
  Environment that requires manual approval, and only run from the main branch.

## Secret Management

- No real secrets are committed. The `DATABASE_URL` value in the chart is a
  local SQLite placeholder for development, not a real credential.
- In production, secrets would come from a secret manager (e.g. AWS Secrets
  Manager / Vault) and be synced into Kubernetes via the External Secrets
  Operator, with the workload authenticating through a cloud identity (IRSA)
  rather than static keys.

## Security Checklist

- [x] No hardcoded / committed real credentials
- [x] Non-root container user
- [x] Dropped Linux capabilities
- [x] Resource limits
- [x] Minimal RBAC (dedicated ServiceAccount, no extra permissions)
- [x] Image scanning in CI
- [x] Secret management strategy (placeholder now, External Secrets in prod)
- [ ] Read-only root filesystem (documented next step)
- [ ] NetworkPolicy (documented next step)