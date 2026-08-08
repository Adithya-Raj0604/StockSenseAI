# The full EC2 deployment (what the Lightsail choice defers)

The always-on live layer runs on **Lightsail** as a deliberate cost-vs-realism
tradeoff (~$5/mo flat, bundled IP). The raw-EC2-in-a-VPC path is still built and
recorded in the `full-demo` environment, but a *production, always-on* EC2
deployment would add the following — documented here so the tradeoff is explicit
rather than a gap.

## What production would add

| Concern | This project (demo) | Production EC2 |
|---------|---------------------|----------------|
| Compute | Single Lightsail box / single demo EC2 | **Auto Scaling Group** across ≥2 AZs |
| Ingress | Caddy on the box (Lightsail) | **Application Load Balancer** + target group |
| TLS | Caddy + Let's Encrypt | **ACM cert** on the ALB |
| Subnets | Lightsail is outside the VPC | App in **private subnets**, ALB in public |
| Public IP | Bundled static IP | **EIP/IPv4** (~$3.60/mo) or IPv6 |
| Health | Container `--restart` | **ALB + ASG health checks**, auto-replace |
| Deploys | `docker run` on boot | **Rolling / blue-green** via ASG + target groups |
| Scaling | Fixed | **Target-tracking** on CPU / request count |
| Secrets | Env vars | **SSM Parameter Store / Secrets Manager** |
| Logs | Local | **CloudWatch agent** / centralized logging |

## Why Lightsail is the right call *here*

- It's an always-on portfolio demo, not production traffic.
- It avoids the ~$3.60/mo IPv4 tax and free-tier-expiry cliff.
- The genuine VPC/EC2/bastion/NAT/EKS skills are already demonstrated in the
  `full-demo` environment and the recorded walkthrough.
- Choosing the $5 managed option *and* being able to spec the full ASG/ALB
  version is the cost-awareness + judgment signal the roles ask for.

## Rough production cost (for comparison)

ALB (~$16/mo) + 2× t3.small on-demand (~$30/mo) + EIP (~$3.60/mo) + NAT
(~$32/mo) ≈ **$80+/mo** — ~16× the Lightsail demo, justified only by real
traffic and uptime requirements.
