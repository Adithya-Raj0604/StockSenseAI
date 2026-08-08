# Full-demo runbook — build → record → destroy in one sitting

Exact commands for the single metered session. The whole thing is <$0.50 and
~30–40 min of wall-clock (EKS is the slow part). **Run `terraform destroy` at
the end no matter what.**

Set these once at the top of your shell:

```bash
export AWS_REGION=us-east-1
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export ECR_REGISTRY=$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
export IMAGE=$ECR_REGISTRY/stocksense-server:latest
```

---

## 0. One-time prerequisites (do these before the timed run)

**Budget alert** (safety net) — AWS Console → Billing → Budgets → create a
$10/month cost budget filtered to tag `Project = StockSenseAI-Infra`. Or:

```bash
# Console is easier; the CLI form needs a JSON budget doc.
```

**EC2 key pair** (for bastion/app SSH):

```bash
aws ec2 create-key-pair --key-name stocksense-demo \
  --query 'KeyMaterial' --output text > ~/.ssh/stocksense-demo.pem
chmod 600 ~/.ssh/stocksense-demo.pem
```

**ECR repo + push the server image** (build from repo root):

```bash
aws ecr create-repository --repository-name stocksense-server --region $AWS_REGION

aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin $ECR_REGISTRY

docker build -f backend/Dockerfile.server -t $IMAGE .
docker push $IMAGE
```

**Fill in tfvars:**

```bash
cd infra/terraform/environments/full-demo
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars:
#   ssh_ingress_cidr = "<your-public-ip>/32"   (curl ifconfig.me)
#   key_name         = "stocksense-demo"
#   container_image  = value of $IMAGE
#   ecr_registry     = value of $ECR_REGISTRY
```

---

## 1. Start recording, then apply

```bash
cd infra/terraform/environments/full-demo
terraform init
terraform apply            # ~15 min; narrate VPC, NAT, bastion, EC2, EKS coming up
```

Show the AWS console: VPC → subnets & route tables, then EKS → cluster → nodes.

## 2. Point kubectl at the cluster and deploy

```bash
aws eks update-kubeconfig --name stocksense-demo --region $AWS_REGION

# Update the image line in infra/k8s/deployment.yaml to $IMAGE first, then:
kubectl apply -f ../../../k8s/deployment.yaml
kubectl apply -f ../../../k8s/service.yaml

kubectl get pods -o wide
kubectl get svc stocksense        # note EXTERNAL-IP (NLB DNS) once provisioned
```

## 3. Prove it serves

```bash
LB=$(kubectl get svc stocksense -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl http://$LB/health            # -> "deployment":"self-hosted"
```

## 4. Operate it (the SRE signal)

```bash
kubectl describe pod -l app=stocksense | head -40
kubectl logs -l app=stocksense --tail=20

# Rolling update: push a v2 tag, then:
kubectl set image deployment/stocksense stocksense=$ECR_REGISTRY/stocksense-server:v2
kubectl rollout status deployment/stocksense
kubectl rollout history deployment/stocksense
```

## 5. (Optional) show the raw EC2 path

```bash
# SSH to bastion, then hop to the private app host (from terraform output):
ssh -i ~/.ssh/stocksense-demo.pem ec2-user@$(terraform output -raw bastion_public_ip)
# from the bastion:
curl http://<app_private_ip>:8000/health
```

## 6. DESTROY (do not skip)

```bash
kubectl delete -f ../../../k8s/service.yaml   # deletes the NLB before teardown
cd ../../../..                                 # back to repo root
./infra/scripts/destroy-full-demo.sh
```

Then verify in the console that **NAT gateways** and the **EKS cluster** are
gone (those are the hourly billers). Stop the recording.

---

## Cleanup checklist

- [ ] `terraform destroy` completed with no errors
- [ ] EKS cluster deleted (console)
- [ ] NAT gateway(s) deleted (console)
- [ ] NLB from the k8s Service deleted (console → EC2 → Load Balancers)
- [ ] Recording saved and linked in `demo-recording.md`
- [ ] ECR image can stay (pennies) or delete the repo to zero it out
