#!/usr/bin/env bash
# Apply the OPTIONAL always-on Lightsail live layer (~$5/mo).
# Skip this for repo-only delivery.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../terraform/environments/live" && pwd)"
cd "$DIR"

if [[ ! -f terraform.tfvars ]]; then
  echo "Missing terraform.tfvars. Copy terraform.tfvars.example and fill it in first." >&2
  exit 1
fi

terraform init
terraform apply
echo
echo "Now create a DNS A record for your domain pointing at the 'live_static_ip' output above."
