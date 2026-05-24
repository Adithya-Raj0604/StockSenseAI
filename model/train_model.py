# %% [markdown]
# # StockSense AI Model Training
#
# This notebook trains a hybrid inventory model. The deterministic inventory policy calculates the
# minimum safe reorder amount, while the machine learning model learns an adjustment from messy
# historical ordering behavior.

# %%
from pathlib import Path
import os
import sys

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import joblib
import mlflow
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

if "__file__" in globals():
    SCRIPT_DIR = Path(__file__).resolve().parent
else:
    current_dir = Path.cwd()
    SCRIPT_DIR = (
        current_dir
        if (current_dir / "restaurant_inventory_with_targets.csv").exists()
        else current_dir / "model"
    )
PROJECT_ROOT = SCRIPT_DIR.parent if SCRIPT_DIR.name == "model" else SCRIPT_DIR
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.ml_features import (  # noqa: E402
    BASE_FEATURES,
    CATEGORICAL_FEATURES,
    ENGINEERED_FEATURES,
    NUMERIC_FEATURES,
    InventoryFeatureEngineer,
    add_inventory_features,
)

RANDOM_STATE = 42
DATA_PATH = SCRIPT_DIR / "restaurant_inventory_with_targets.csv"
MODEL_PATH = SCRIPT_DIR / "reorder_model_tuned.pkl"
MLFLOW_EXPERIMENT_NAME = "stocksense-reorder-model"
MLFLOW_TRACKING_URI = f"sqlite:///{(PROJECT_ROOT / 'mlflow.db').as_posix()}"

# %% [markdown]
# ## Load Data

# %%
df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()

print("Dataset loaded successfully")
print("Shape:", df.shape)
print(df.head())

# %% [markdown]
# ## Clean Data And Build Inventory Policy Features

# %%
target = "Inventory_To_Order"
required_columns = BASE_FEATURES + [target]
missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

for column in NUMERIC_FEATURES + [target]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.dropna(subset=required_columns).copy()
df = add_inventory_features(df)

print("Cleaned dataset shape:", df.shape)
print(df[BASE_FEATURES + ["Waste_Adjusted_Minimum", target]].head())

# %% [markdown]
# ## Simulate Controlled Real-World Label Noise
#
# The project intentionally keeps noisy labels to mimic messy real restaurant ordering behavior.
# The noise is seeded for reproducibility and clipped so the target never becomes physically impossible.

# %%
rng = np.random.default_rng(RANDOM_STATE)
noise_scale = min(1.0, df[target].std() * 0.05)

df["Raw_Target"] = df[target]
df["Noisy_Target"] = (
    df[target] + rng.normal(loc=0, scale=noise_scale, size=len(df))
).clip(lower=0)

df["Target_Adjustment"] = df["Noisy_Target"] - df["Waste_Adjusted_Minimum"]

print(f"Noise scale: {noise_scale:.2f}")
print("Raw target min:", round(df["Raw_Target"].min(), 2))
print("Noisy target min:", round(df["Noisy_Target"].min(), 2))
print("Adjustment target summary:")
print(df["Target_Adjustment"].describe().round(2))

# %% [markdown]
# ## Train/Test Split

# %%
X = df[BASE_FEATURES]
y_adjustment = df["Target_Adjustment"]
y_final = df["Noisy_Target"]

X_train, X_test, y_train, y_test, y_final_train, y_final_test = train_test_split(
    X,
    y_adjustment,
    y_final,
    test_size=0.2,
    random_state=RANDOM_STATE,
)

print("Training rows:", X_train.shape[0])
print("Testing rows:", X_test.shape[0])

# %% [markdown]
# ## Model Candidates
#
# Each model predicts the adjustment above the operational minimum. The final recommendation is
# `max(operational minimum, operational minimum + model adjustment)`.

# %%
model_features = NUMERIC_FEATURES + ENGINEERED_FEATURES

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL_FEATURES),
        ("num", "passthrough", model_features),
    ],
    verbose_feature_names_out=False,
)

candidate_models = {
    "Random Forest": RandomForestRegressor(
        n_estimators=300,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
    "Extra Trees": ExtraTreesRegressor(
        n_estimators=400,
        min_samples_leaf=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    ),
    "Hist Gradient Boosting": HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=300,
        l2_regularization=0.05,
        random_state=RANDOM_STATE,
    ),
}

def make_pipeline(regressor):
    return Pipeline(
        steps=[
            ("feature_engineering", InventoryFeatureEngineer()),
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )

# %% [markdown]
# ## Evaluate Candidate Models

# %%
def operational_minimum_for(X_values):
    return add_inventory_features(X_values)["Waste_Adjusted_Minimum"].to_numpy()


def evaluate_model(name, pipeline):
    pipeline.fit(X_train, y_train)

    adjustment_pred = pipeline.predict(X_test)
    operational_minimum = operational_minimum_for(X_test)
    final_pred = np.maximum(operational_minimum, operational_minimum + adjustment_pred)
    final_pred = np.clip(final_pred, 0, None)

    return {
        "Model": name,
        "MAE": mean_absolute_error(y_final_test, final_pred),
        "RMSE": np.sqrt(mean_squared_error(y_final_test, final_pred)),
        "R2": r2_score(y_final_test, final_pred),
        "Adjustment_MAE": mean_absolute_error(y_test, adjustment_pred),
        "Pipeline": pipeline,
    }


results = []
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)

for model_name, regressor in candidate_models.items():
    print(f"Training {model_name}...")
    result = evaluate_model(model_name, make_pipeline(regressor))

    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_name", model_name)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("training_rows", X_train.shape[0])
        mlflow.log_param("testing_rows", X_test.shape[0])
        mlflow.log_param("target", "Target_Adjustment")

        for param_name, param_value in regressor.get_params().items():
            mlflow.log_param(f"hyperparameter_{param_name}", param_value)

        mlflow.log_metric("mae", result["MAE"])
        mlflow.log_metric("rmse", result["RMSE"])
        mlflow.log_metric("r2", result["R2"])
        mlflow.log_metric("adjustment_mae", result["Adjustment_MAE"])

    results.append(result)

comparison = pd.DataFrame(results).drop(columns=["Pipeline"]).sort_values("MAE")
comparison

# %% [markdown]
# ## Select Best Model And Save

# %%
best_result = min(results, key=lambda item: item["MAE"])
best_model = best_result["Pipeline"]

print("Best model:", best_result["Model"])
print(f"MAE: {best_result['MAE']:.2f}")
print(f"RMSE: {best_result['RMSE']:.2f}")
print(f"R2: {best_result['R2']:.3f}")

joblib.dump(best_model, MODEL_PATH)
print(f"Saved model to {MODEL_PATH}")

with mlflow.start_run(run_name=f"best-{best_result['Model']}"):
    mlflow.log_param("selected_model", best_result["Model"])
    mlflow.log_param("model_output_path", str(MODEL_PATH))
    mlflow.log_metric("best_mae", best_result["MAE"])
    mlflow.log_metric("best_rmse", best_result["RMSE"])
    mlflow.log_metric("best_r2", best_result["R2"])
    mlflow.log_metric("best_adjustment_mae", best_result["Adjustment_MAE"])
    mlflow.log_artifact(MODEL_PATH)

# %% [markdown]
# ## Edge Case Checks

# %%
edge_cases = pd.DataFrame(
    [
        {
            "Item_Name": "Eggs",
            "Category": "Non-Veg",
            "Subcategory": "Poultry",
            "Unit": "pieces",
            "Current_Stock": 20,
            "Reorder_Level": 70,
            "Daily_Usage": 4,
            "Lead_Time": 2,
            "Price_per_Unit": 6,
            "Seasonal_Factor": 0.87,
            "Waste_Percentage": 1.52,
        },
        {
            "Item_Name": "Eggs",
            "Category": "Non-Veg",
            "Subcategory": "Poultry",
            "Unit": "pieces",
            "Current_Stock": 23,
            "Reorder_Level": 24,
            "Daily_Usage": 20,
            "Lead_Time": 0,
            "Price_per_Unit": 0.2,
            "Seasonal_Factor": 0.87,
            "Waste_Percentage": 1.52,
        },
    ]
)

edge_operational_minimum = operational_minimum_for(edge_cases)
edge_adjustment = best_model.predict(edge_cases)
edge_final = np.maximum(edge_operational_minimum, edge_operational_minimum + edge_adjustment)

edge_results = edge_cases[["Item_Name", "Current_Stock", "Reorder_Level", "Daily_Usage", "Lead_Time"]].copy()
edge_results["Operational_Minimum"] = np.ceil(edge_operational_minimum).astype(int)
edge_results["Model_Adjustment"] = np.round(edge_adjustment, 2)
edge_results["Final_Recommendation"] = np.ceil(edge_final).astype(int)
edge_results

# %% [markdown]
# ## Load Saved Model Smoke Test

# %%
loaded_model = joblib.load(MODEL_PATH)
sample = X_test.iloc[[0]]
sample_operational_minimum = operational_minimum_for(sample)[0]
sample_adjustment = loaded_model.predict(sample)[0]
sample_final = max(sample_operational_minimum, sample_operational_minimum + sample_adjustment)

print("Sample input:")
print(sample)
print(f"Operational minimum: {sample_operational_minimum:.2f}")
print(f"Model adjustment: {sample_adjustment:.2f}")
print(f"Final recommendation: {sample_final:.2f}")
