# Incident Response: Intermittent 502 Bad Gateway After Deployment

## 1. Initial Triage

The report is intermittent 502s through the ingress, twenty minutes after a
deployment, with pods still running and CPU/memory normal. "Intermittent" tells
me some backends are serving and some are not, so the first thing I check is the
**Service backends (endpoints)** — I want to know whether the Service actually
has healthy pods behind it, and whether the count matches the running pods. If
the app itself were broken I'd expect the pods to crash or error; here they are
running, so my suspicion goes to the routing layer between the ingress and the
pods rather than the application code.

## 2. Commands I Would Run

```bash
# Are the pods actually running and ready?
kubectl get pods -n profile-service

# Does the Service have healthy backends? (key check)
kubectl get endpoints profile-service -n profile-service

# Compare the Service targetPort against the container port
kubectl get svc profile-service -n profile-service -o yaml
kubectl get deploy profile-service -n profile-service -o yaml | grep -i port

# Check readiness probe status and recent events on a pod
kubectl describe pod <pod-name> -n profile-service

# Look at application logs for errors
kubectl logs <pod-name> -n profile-service

# Prove the app works when hit directly (bypassing the Service)
kubectl port-forward pod/<pod-name> 8080:8000 -n profile-service
curl http://localhost:8080/healthz
```

## 3. Metrics and Logs to Inspect

- Ingress 5xx / 502 rate to confirm the errors are coming from the ingress layer.
- Service endpoints count versus running pod count — a mismatch points at
  readiness or port problems.
- Pod readiness state over time (are pods flapping in and out of Ready?).
- Application logs for connection or startup errors.
- Recent deployment events / rollout history to line the errors up with the
  config change.

## 4. Plausible Root Causes

1. **Service targetPort does not match the container port.** If the recent
   config change altered the container port (or the Service targetPort), the
   Service forwards traffic to a port nothing is listening on, which returns a
   502 at the ingress even though the pod is healthy.
2. **Readiness probe misconfigured after the change.** If the probe points at
   the wrong path or port, pods can be added to or removed from the Service
   endpoints incorrectly, so some requests land on pods that cannot serve.
3. **Rolling update sent traffic to pods that were not ready.** During the
   rollout, new pods may have started receiving traffic before they were
   actually ready, producing intermittent failures while old pods drained.

## 5. Most Likely Root Cause

A **container port / Service targetPort mismatch** introduced by the recent
deployment configuration change. The strongest clue is that the service works
when called directly inside the cluster but fails through the ingress: a direct
call goes straight to the pod's endpoint, while the ingress path goes through
the Service. If hitting the pod directly works but going through the Service
does not, the break is in the Service routing — and a wrong targetPort is the
classic cause of exactly that. The pods being healthy and resource usage being
normal further rules out the application and resource exhaustion.

## 6. Immediate Mitigation

Roll back to the last known-good release to restore service quickly, then
investigate with traffic stable:

```bash
helm rollback profile-service -n profile-service
kubectl rollout status deploy/profile-service -n profile-service
```

## 7. Permanent Fix

Correct the Service `targetPort` so it matches the container port (8000), then
confirm endpoints repopulate and traffic flows through the Service. Keep the
container port, the Service targetPort, and the probe ports defined from a
single source so they cannot drift apart again.

## 8. Prevention Plan

This class of bug is catchable before it ever reaches a cluster. In CI I run
`helm template` and manifest validation, which renders the chart and surfaces
port/templating mistakes at pull-request time rather than at deploy time. Adding
a post-deploy smoke test that calls the service through the Service/ingress (not
just the pod) would also catch a routing break automatically and let the deploy
roll itself back.
