# StockSenseAI — Self-Hosted Infrastructure (Terraform / VPC / EC2 / EKS)

A second, self-hosted deployment path for StockSenseAI, alongside the existing
serverless (Lambda + API Gateway + CloudFront + S3 via SAM) deployment. It
demonstrates **traditional infrastructure-as-code**: a hand-authored multi-AZ
VPC, raw EC2 in public/private subnets, a bastion + NAT pattern, and a
Kubernetes (EKS) deployment — all in Terraform, gated by CI.

The existing serverless deployment and its live URL are **untouched**.

## Layout

```
infra/
├── terraform/
│   ├── modules/        # hand-written, reusable: vpc, ec2, nat-bastion, eks, lightsail
│   └── environments/
│       ├── live/       # OPTIONAL always-on Lightsail host (~$5/mo)
│       └── full-demo/  # VPC + EC2 + NAT + bastion + EKS (build → record → destroy)
├── k8s/                # hand-written Deployment + Service manifests
├── docs/               # cost breakdown, production-EC2 writeup, recording
└── scripts/            # deploy-live.sh, destroy-full-demo.sh
```

## Two layers, one goal

| | Live layer | Full-demo layer |
|---|---|---|
| Purpose | Optional always-on link | The real VPC/EC2/EKS proof |
| Host | Lightsail (bundled IP) | Raw EC2 + EKS in a custom VPC |
| Lifecycle | Always on | Build → record → **destroy** |
| Cost | ~$5/mo (optional) | ~$0 steady-state, <$0.50/session |

**Default (repo-only) delivery:** skip the live layer. The Terraform code, the
K8s manifests, the CI pipeline, and a one-time recorded `apply → kubectl →
destroy` session are the deliverable. See [docs/demo-recording.md](docs/demo-recording.md).

## The workload

Both layers run the same container as the serverless deployment, built from
[`backend/Dockerfile.server`](../backend/Dockerfile.server) (uvicorn entrypoint;
the Lambda image is separate and untouched). Each deployment self-identifies via
the `DEPLOYMENT` env var, surfaced at `/health`.

## Quickstart (full-demo)

```bash
cd infra/terraform/environments/full-demo
cp terraform.tfvars.example terraform.tfvars   # fill in your values
terraform init
terraform apply
# ... record the walkthrough, apply k8s manifests ...
../../../scripts/destroy-full-demo.sh          # tear down immediately after
```

## Docs

- [Cost breakdown](docs/cost-breakdown.md)
- [The full EC2 deployment (what Lightsail defers)](docs/production-ec2.md)
- [Demo recording](docs/demo-recording.md)
- Architecture diagrams: `docs/architecture-diagram-live.png`,
  `docs/architecture-diagram-full.png` _(TODO — export from draw.io/Excalidraw)_
