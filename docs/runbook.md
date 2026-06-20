# Runbook

Practical operational steps for the profile service. Replace `$NS` with the
target namespace (e.g. `profile-service`, `profile-service-staging`,
`profile-service-prod`) and `$REL` with the Helm release name
(`profile-service`).

```bash
export NS=profile-service
export REL=profile-service
```

## Deploy

Local (minikube):

```bash
# Build the image and load it into minikube
podman build -t profile-service:local .
podman save -o profile-service.tar localhost/profile-service:local
minikube image load profile-service.tar

# Install / upgrade via Helm
helm upgrade --install $REL ./helm/profile-service \
  --namespace $NS --create-namespace
```

Real environments are deployed by the CI/CD pipeline: a merge to main builds an
image tagged with the commit SHA, pushes it to the registry, deploys to
staging, and waits for manual approval before production.

## Verify a Deployment

```bash
# Rollout completed successfully
kubectl -n $NS rollout status deploy/$REL

# Pods are Running and Ready
kubectl -n $NS get pods

# Health checks via the Service
kubectl -n $NS port-forward svc/$REL 8080:80
curl http://localhost:8080/healthz
curl http://localhost:8080/readyz

# Confirm the Service has backends
kubectl -n $NS get endpoints $REL
```

## Inspect Pods, Services, Ingress, Events, Logs

```bash
kubectl -n $NS get deploy,pods,svc,ingress,hpa
kubectl -n $NS describe pod <pod-name>
kubectl -n $NS get events --sort-by=.lastTimestamp | tail -30
kubectl -n $NS logs deploy/$REL -f
kubectl -n $NS logs <pod-name> --previous   # logs from a crashed container
```

## Roll Back a Bad Release

```bash
# See revision history
helm -n $NS history $REL

# Roll back to the previous good revision (or a specific one)
helm -n $NS rollback $REL
helm -n $NS rollback $REL <revision>

# Confirm
kubectl -n $NS rollout status deploy/$REL
```

## Handle Failed Readiness Probes

Symptom: pods Running but `0/1 READY`; Service has no endpoints; requests 503.

```bash
kubectl -n $NS describe pod <pod-name> | grep -A5 -i readiness
kubectl -n $NS port-forward <pod-name> 8080:8000
curl -i http://localhost:8080/readyz    # 503 => the DB check is failing
```

Actions: if `/readyz` is 503, the database is unreachable — see the DB section.
If the probe timing is too tight for a slow start, increase the readiness
`initialDelaySeconds` and redeploy.

## Handle High Error Rate

```bash
# Are 5xx coming from the app or the edge?
kubectl -n $NS logs deploy/$REL --tail=200 | grep " 5"
kubectl -n $NS get endpoints $REL        # are pods behind the Service?
```

Immediate mitigation: if it started right after a deploy, roll back. If only
some pods are bad, delete them to recycle. If overloaded (HPA at max, CPU
pinned), temporarily raise `maxReplicas`.

## Handle Database Connectivity Failure

Symptom: `/readyz` returns 503; logs show connection errors to the DB.

```bash
# Is the DATABASE_URL secret present?
kubectl -n $NS get secret ${REL}-secret -o jsonpath='{.data.DATABASE_URL}' | base64 -d

# Can a pod reach the DB host/port?
kubectl -n $NS exec deploy/$REL -- python -c "import socket; socket.create_connection(('DB_HOST', 5432), 3); print('ok')"
```

Actions: fix the secret if missing/wrong, check network reachability and any
NetworkPolicy/firewall, and confirm the database itself is up. The app degrades
to 503 (drains traffic) rather than serving errors while the DB is down.