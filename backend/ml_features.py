import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


BASE_FEATURES = [
    "Item_Name",
    "Category",
    "Subcategory",
    "Unit",
    "Current_Stock",
    "Reorder_Level",
    "Daily_Usage",
    "Lead_Time",
    "Price_per_Unit",
    "Seasonal_Factor",
    "Waste_Percentage",
]

NUMERIC_FEATURES = [
    "Current_Stock",
    "Reorder_Level",
    "Daily_Usage",
    "Lead_Time",
    "Price_per_Unit",
    "Seasonal_Factor",
    "Waste_Percentage",
]

CATEGORICAL_FEATURES = [
    "Item_Name",
    "Category",
    "Subcategory",
    "Unit",
]

ENGINEERED_FEATURES = [
    "Lead_Time_Demand",
    "Projected_Stock_After_Lead_Time",
    "Reorder_Gap",
    "Operational_Minimum",
    "Waste_Adjusted_Minimum",
    "Stock_Coverage_Days",
    "Is_Below_Reorder_Level",
]


def add_inventory_features(data):
    df = pd.DataFrame(data).copy()

    for column in NUMERIC_FEATURES:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Lead_Time_Demand"] = df["Daily_Usage"] * df["Lead_Time"]
    df["Projected_Stock_After_Lead_Time"] = df["Current_Stock"] - df["Lead_Time_Demand"]
    df["Reorder_Gap"] = df["Reorder_Level"] - df["Projected_Stock_After_Lead_Time"]
    df["Operational_Minimum"] = np.maximum(0, df["Reorder_Gap"])
    df["Waste_Adjusted_Minimum"] = df["Operational_Minimum"] * (
        1 + np.maximum(0, df["Waste_Percentage"]) / 100
    )
    df["Stock_Coverage_Days"] = df["Current_Stock"] / df["Daily_Usage"].replace(0, np.nan)
    df["Stock_Coverage_Days"] = df["Stock_Coverage_Days"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["Is_Below_Reorder_Level"] = (df["Current_Stock"] < df["Reorder_Level"]).astype(int)

    return df


class InventoryFeatureEngineer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return add_inventory_features(X)

