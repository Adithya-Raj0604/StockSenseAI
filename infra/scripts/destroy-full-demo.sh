#!/usr/bin/env bash
# One-command teardown of the expensive full-demo layer.
# Run this the moment recording is done — NAT gateway + EKS control plane
# bill by the hour.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../terraform/environments/full-demo" && pwd)"
cd "$DIR"

echo "Destroying full-demo environment in: $DIR"
terraform destroy -auto-approve
echo "Done. Verify in the AWS console that NAT gateways and the EKS cluster are gone."
