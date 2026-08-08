# Demo recording

> _Placeholder — add the link once recorded (Loom / unlisted YouTube / raw .mp4)._

A 2–3 minute screen recording of the `full-demo` environment being built,
operated, and torn down. This is the substitute for a permanently-running
cluster: it proves the Terraform actually applies and the cluster actually runs,
at ~$0 steady-state cost.

## Suggested script (what to capture)

1. `terraform apply` in `infra/terraform/environments/full-demo` — narrate the
   VPC, NAT/bastion, EC2, and EKS coming up (~15 min; edit down).
2. AWS console: show the VPC (subnets/route tables), the EKS cluster, the nodes.
3. `aws eks update-kubeconfig --name stocksense-demo`
4. `kubectl apply -f infra/k8s/` then `kubectl get pods -o wide`, `kubectl get svc`.
5. Hit the LoadBalancer DNS and show the `/health` response with
   `"deployment": "self-hosted"`.
6. A rolling update: `kubectl set image ...` → `kubectl rollout status ...`.
7. `terraform destroy` (or `infra/scripts/destroy-full-demo.sh`) — show
   everything torn down.

## Link

- Recording: _TODO_
