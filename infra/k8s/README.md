# Kubernetes manifests

Hand-written manifests that deploy the StockSense server-mode container
(`backend/Dockerfile.server`) to the EKS cluster from
`infra/terraform/environments/full-demo`.

## Apply

```bash
# 1. Point kubectl at the cluster Terraform just created
aws eks update-kubeconfig --name stocksense-demo --region us-east-1

# 2. Edit the image in deployment.yaml to your ECR repo:tag, then:
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# 3. Watch it come up
kubectl get pods -o wide
kubectl get svc stocksense   # EXTERNAL-IP is the load balancer DNS
```

## Field notes

**deployment.yaml**
- `replicas: 2` — two pods so a rolling update always has capacity to shift to.
- `strategy.rollingUpdate` — `maxUnavailable: 0` / `maxSurge: 1` means a new pod
  comes up and passes its readiness probe before an old one is removed, so there
  is no capacity dip during a rollout.
- `readinessProbe` on `/health` — a pod is kept out of the Service until the
  model + CSV finish loading (that import is slow; see `backend/main.py`).
- `livenessProbe` on `/health` — a wedged pod gets restarted automatically.
- `resources` — requests reserve enough for pandas + sklearn; limits cap it at
  1Gi, matching the Lambda's memory headroom.
- `DEPLOYMENT=self-hosted` env — surfaces in the `/health` response so you can
  prove which backend answered a request.

**service.yaml**
- `type: LoadBalancer` + the NLB annotation makes the AWS cloud controller
  provision a Network Load Balancer pointing at the pods.
- `port 80 -> targetPort 8000` maps the public LB port to the container port.

## Demonstrate a rolling update (for the recording)

```bash
# Push a new image tag, then:
kubectl set image deployment/stocksense stocksense=<ecr>/stocksense-server:v2
kubectl rollout status deployment/stocksense   # watch it converge
kubectl rollout history deployment/stocksense
```
