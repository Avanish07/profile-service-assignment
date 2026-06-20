# Incident Scenario

Twenty minutes after a production deployment of the profile service, users start reporting intermittent `502 Bad Gateway` errors through the public API gateway/ingress.

Known facts:

- Some requests succeed and some fail.
- Pods appear to be running.
- CPU and memory are not obviously high.
- The deployment completed successfully according to CI/CD.
- The service works when called directly from inside the cluster.
- There was a recent change to Kubernetes deployment configuration.

Your task:

Create `docs/incident-response.md` with an RCA-style response.

Include:

1. Initial triage steps.
2. Exact commands you would run.
3. What metrics and logs you would inspect.
4. At least three plausible root causes.
5. Your most likely root cause and why.
6. Immediate mitigation.
7. Permanent fix.
8. Prevention plan.

Hints: Think about ingress, service endpoints, readiness probes, rolling updates, target ports, request timeouts, and dependency readiness.
