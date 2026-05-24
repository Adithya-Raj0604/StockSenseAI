# StockSense AI

StockSense AI is a serverless inventory forecasting project for restaurant stock management. It serves a trained scikit-learn reorder model through a FastAPI API and provides a static frontend for reorder predictions and inventory chat.

## What It Does

- Predicts recommended reorder quantity for inventory items.
- Answers inventory questions with a lightweight rule-based chatbot.
- Uses historical inventory data to provide simple moving-average forecasts.
- Runs locally as a FastAPI app.
- Is prepared for AWS deployment with Lambda, API Gateway, S3, CloudFront, and CloudWatch.

## Architecture

```text
User Browser
  -> CloudFront
  -> S3 static frontend

Frontend JavaScript
  -> API Gateway HTTP API
  -> Lambda container image
  -> FastAPI + Mangum
  -> scikit-learn model + inventory CSV

Operations
  -> CloudWatch logs with 14-day retention
```

## Repository Layout

```text
backend/
  main.py              FastAPI routes and Lambda handler
  settings.py          Environment-driven config
  Dockerfile           Lambda container image
  requirements.txt     Runtime dependencies
  requirements-dev.txt Test dependencies

frontend/
  index.html           Static app
  script.js            API calls and UI behavior
  style.css            Responsive styling

model/
  reorder_model_tuned.pkl
  restaurant_inventory_with_targets.csv
  train_model.ipynb

template.yaml          AWS SAM infrastructure
tests/                 API smoke tests
```

## Local Backend

```powershell
.\venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

Open the API docs at:

```text
http://localhost:8000/docs
```

Useful endpoints:

- `GET /health`
- `GET /items`
- `POST /predict`
- `POST /chat`

## Local Frontend

Open `frontend/index.html` in a browser or serve the folder with any static file server. The frontend defaults to:

```text
http://localhost:8000
```

You can change the API URL directly in the UI after the backend is deployed.

## Run Tests

Install development dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

Run tests:

```powershell
.\venv\Scripts\python.exe -m pytest
```

## AWS Deployment Path

This repo is set up for AWS SAM using a Lambda container image.

Build:

```powershell
sam build
```

Deploy:

```powershell
sam deploy --guided
```

After deployment:

1. Copy the `ApiUrl` output.
2. Open the frontend and set the API URL.
3. Upload `frontend/index.html`, `frontend/script.js`, and `frontend/style.css` to the deployed S3 bucket.
4. Open the `FrontendDistributionDomain` output in a browser.
5. Update the stack with a stricter `AllowedCorsOrigins` value using the CloudFront domain.

## Cost Notes

The intended hosting model is low-cost serverless:

- API Gateway HTTP API charges per request.
- Lambda charges per request and compute duration.
- S3 stores the frontend assets.
- CloudFront serves the static frontend over HTTPS.
- CloudWatch stores short-retention logs.
- ECR stores the Lambda container image.

For recruiter/demo traffic, expected monthly cost is usually low, especially without RDS, NAT Gateway, WAF, provisioned concurrency, or long CloudWatch log retention.

## Resume Highlights

- Serverless ML inference using AWS Lambda and API Gateway.
- Static frontend hosted through S3 and CloudFront.
- FastAPI adapted to Lambda with Mangum.
- Containerized Python ML runtime for scikit-learn inference.
- Infrastructure-as-code with AWS SAM.
- Cost-conscious design with no always-on compute.

