# StockSense AI

StockSense AI is a deployed serverless inventory forecasting app for restaurant stock management. It combines a FastAPI backend, a trained scikit-learn model, inventory guardrails, and a static frontend hosted on AWS.

Live app: [https://d321ncqj1ylu8d.cloudfront.net/](https://d321ncqj1ylu8d.cloudfront.net/)

## What It Does

- Predicts recommended reorder quantities for restaurant inventory items.
- Combines ML predictions with rule-based inventory safeguards for reorder level, current stock, lead time, waste, and whole-unit items such as eggs.
- Provides an inventory chatbot for reorder forecasts, waste guidance, and prediction explanations.
- Shows field-level info popovers explaining how each input affects the recommendation.
- Runs locally as a FastAPI app and is deployed on AWS using Lambda, API Gateway, S3, CloudFront, ECR, CloudWatch, and SAM.

## Architecture

```text
User Browser
  -> CloudFront
  -> Private S3 static frontend

Frontend JavaScript
  -> API Gateway HTTP API
  -> Lambda container image
  -> FastAPI + Mangum
  -> scikit-learn hybrid model + inventory CSV

Operations
  -> CloudWatch logs with 14-day retention
  -> API Gateway throttling
  -> Tagged AWS resources for budget tracking
```

## ML Approach

The model was reworked from a direct reorder-quantity regressor into a hybrid inventory system:

```text
operational minimum = reorder level - projected stock after lead time
projected stock = current stock - daily usage * lead time
waste-adjusted minimum = operational minimum adjusted by expected waste
final recommendation = max(operational minimum, operational minimum + ML adjustment)
```

The training workflow keeps controlled noisy labels to simulate messy real-world inventory data, but clips impossible negative targets. It compares multiple regressors and currently saves a HistGradientBoostingRegressor-based pipeline that predicts demand adjustment above the operational minimum.

## Repository Layout

```text
backend/
  main.py              FastAPI routes, Lambda handler, prediction logic
  ml_features.py       Reusable inventory feature engineering
  settings.py          Environment-driven config
  Dockerfile           Lambda container image
  requirements.txt     Runtime dependencies
  requirements-dev.txt Test/training dependencies

frontend/
  index.html           Static app
  script.js            API calls and UI behavior
  style.css            Responsive styling

model/
  reorder_model_tuned.pkl
  restaurant_inventory_with_targets.csv
  train_model.py
  train_model.ipynb
  generate_notebook.py

template.yaml          AWS SAM infrastructure
tests/                 API smoke and regression tests
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

Serve the frontend locally:

```powershell
.\venv\Scripts\python.exe -m http.server 8080 --directory frontend
```

Then open:

```text
http://127.0.0.1:8080
```

The deployed frontend is configured to call the live API Gateway endpoint.

## Run Tests

Install development dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r backend\requirements-dev.txt
```

Run tests:

```powershell
.\venv\Scripts\python.exe -m pytest
```

## Training

Train and save the model:

```powershell
.\venv\Scripts\python.exe model\train_model.py
```

Regenerate the notebook from the script-backed workflow:

```powershell
.\venv\Scripts\python.exe model\generate_notebook.py
```

The training script logs candidate model metrics with MLflow using local ignored artifacts.

## AWS Deployment

This project is deployed with AWS SAM using a Lambda container image.

Validate and build:

```powershell
sam validate
sam build
```

Deploy:

```powershell
sam deploy --parameter-overrides AllowedCorsOrigins=https://d321ncqj1ylu8d.cloudfront.net
```

Upload frontend assets:

```powershell
aws s3 sync frontend s3://stocksense-ai-frontendbucket-mzzorrfadafi --delete
```

Invalidate CloudFront after frontend changes:

```powershell
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## Production Controls

- API Gateway HTTP API throttling.
- CORS restricted to the CloudFront frontend domain.
- FastAPI adapted to Lambda with `Mangum(app, lifespan="off")`.
- CloudWatch log retention set to 14 days.
- AWS resources tagged with `Project=StockSenseAI` and `Environment=Production`.
- Budget tracking prepared through AWS cost allocation tags.
- No NAT Gateway, RDS, WAF, provisioned concurrency, or always-on server.

## Cost Notes

This is designed as a low-cost resume project. Expected cost for light recruiter/demo traffic is roughly:

```text
$1-$4/month
```

Recommended budget controls:

- Account-wide AWS budget at `$10/month`.
- Project-specific budget at `$5/month` after the `Project` cost allocation tag becomes available.
- ECR lifecycle cleanup to keep only recent container images.

## Resume Highlights

- Built and deployed a full-stack restaurant inventory forecasting app using FastAPI, scikit-learn, AWS Lambda, API Gateway, S3, CloudFront, and Docker-based Lambda containers.
- Developed a hybrid ML prediction system combining a trained demand-adjustment model with rule-based inventory guardrails for reorder level, lead time, current stock, waste, and whole-unit item handling.
- Implemented a static frontend with prediction controls, inventory chatbot, item-level explanations, live API integration, and CloudFront-hosted production deployment.
- Added production-focused AWS controls including restricted CORS, API Gateway throttling, CloudWatch log retention, SAM infrastructure-as-code, tagged resources, and budget tracking preparation.
