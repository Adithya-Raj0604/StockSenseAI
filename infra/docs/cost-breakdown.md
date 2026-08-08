# Cost breakdown

The added infrastructure is split into two layers so steady-state cost stays
near zero while still proving the full traditional-infra stack.

## The fact that drives the design

Since **February 2024, AWS charges ~$3.60/month for every in-use public IPv4
address** — Elastic IP or auto-assigned, attached or not. So a raw always-on
EC2 instance floors at ~$3.60/mo before compute, and lands ~$7–8/mo after the
12-month free tier. That exceeds a "few dollars/month" budget long-term, which
is why the always-on layer uses Lightsail (bundled IP) and the raw EC2/VPC path
is proven ephemerally instead.

## Layer 1 — Live (optional, always-on)

Only built if a permanent clickable link is wanted. Hosted on Lightsail, whose
bundle includes a static IP + data transfer (no separate IPv4 charge).

| Item | Cost/mo |
|------|---------|
| Lightsail instance, 1 GB bundle (`small_3_0`) | ~$5.00 |
| Static IP (bundled with instance) | $0.00 |
| Route 53 hosted zone (only if using a custom domain) | ~$0.50 |
| **Total** | **~$5.00–5.50** |

## Layer 2 — Full-demo (ephemeral: build → record → destroy)

Never left running. Costs accrue only during a ~1–2 hour record session.

| Item | Rate | ~1.5 hr session |
|------|------|-----------------|
| EKS control plane | $0.10/hr | ~$0.15 |
| NAT gateway | ~$0.045/hr + data | ~$0.07 |
| 2× t3.small nodes (SPOT) | ~$0.006/hr ea | ~$0.02 |
| Bastion + app EC2 (t3.micro/small) | ~$0.03/hr | ~$0.05 |
| NLB (from the k8s Service) | ~$0.0225/hr | ~$0.03 |
| **Session total** | | **< $0.50** |

Steady-state cost of Layer 2 after `terraform destroy`: **$0.**

## Repo-only mode (default)

Skip Layer 1 entirely. Only cost is the occasional <$0.50 full-demo record
session. **Effective steady-state: ~$0/month.**

## Guardrails backing these numbers

- AWS Budget alert at $10/mo scoped to `Project=StockSenseAI-Infra`.
- `full-demo` excluded from CI so it can never be applied accidentally.
- `infra/scripts/destroy-full-demo.sh` for one-command teardown.
