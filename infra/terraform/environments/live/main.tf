# LIVE environment — OPTIONAL always-on layer (~$5/mo).
# Skip this entirely for the default repo-only delivery; the recorded
# full-demo environment carries the real VPC/EC2/EKS proof.

module "live_host" {
  source = "../../modules/lightsail"

  name              = "stocksense-live"
  availability_zone = var.availability_zone
  bundle_id         = var.bundle_id
  container_image   = var.container_image
  domain            = var.domain
  ssh_ingress_cidr  = var.ssh_ingress_cidr
}

output "live_static_ip" {
  description = "Point the DNS A record for var.domain at this address."
  value       = module.live_host.static_ip
}
