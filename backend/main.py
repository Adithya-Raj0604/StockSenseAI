from functools import lru_cache
from math import ceil
import os

os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")

import joblib
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.settings import settings

try:
    from mangum import Mangum
except ImportError:
    Mangum = None


class PredictRequest(BaseModel):
    Item_Name: str
    Category: str
    Subcategory: str
    Unit: str
    Current_Stock: float
    Reorder_Level: float
    Daily_Usage: float
    Lead_Time: float
    Price_per_Unit: float
    Seasonal_Factor: float
    Waste_Percentage: float


class ChatRequest(BaseModel):
    message: str


@lru_cache(maxsize=1)
def load_model():
    return joblib.load(settings.model_path)


@lru_cache(maxsize=1)
def load_inventory_data():
    inventory_df = pd.read_csv(settings.data_path)
    inventory_df.columns = inventory_df.columns.str.strip()
    inventory_df["Date"] = pd.to_datetime(inventory_df["Date"])
    return inventory_df


model = load_model()
df = load_inventory_data()


app = FastAPI(
    title="StockSense AI API",
    description="ML reorder prediction and rule-based inventory chatbot.",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_known_items():
    return sorted(df["Item_Name"].dropna().unique().tolist())


def detect_item(message: str):
    normalized_message = message.lower()

    for item in get_known_items():
        if item.lower() in normalized_message:
            return item

    return None


def detect_period(message: str):
    normalized_message = message.lower()

    if "tomorrow" in normalized_message or "next day" in normalized_message:
        return "next_day"

    if "today" in normalized_message:
        return "today"

    if "this week" in normalized_message:
        return "this_week"

    if "next week" in normalized_message:
        return "next_week"

    if "this month" in normalized_message:
        return "this_month"

    if "next month" in normalized_message:
        return "next_month"

    if "week" in normalized_message:
        return "next_week"

    if "month" in normalized_message:
        return "next_month"

    return "next_month"


def format_period(period: str):
    mapping = {
        "today": "today",
        "next_day": "tomorrow",
        "this_week": "this week",
        "next_week": "next week",
        "this_month": "this month",
        "next_month": "next month",
    }

    return mapping.get(period, period.replace("_", " "))


def forecast_item(item_name: str, period: str = "next_month"):
    item_df = df[df["Item_Name"].str.lower() == item_name.lower()].copy()

    if item_df.empty:
        return {"error": f"No inventory data found for item: {item_name}"}

    item_df = item_df.sort_values("Date")
    unit = item_df["Unit"].mode()[0]

    if period in ["today", "next_day"]:
        recent_days = item_df.tail(7)
        forecast_value = recent_days["Inventory_To_Order"].mean()
        method = "7-day moving average"

    elif period in ["this_week", "next_week"]:
        item_df["Week"] = item_df["Date"].dt.to_period("W")
        weekly_orders = item_df.groupby("Week")["Inventory_To_Order"].sum().sort_index()
        recent_weeks = weekly_orders.tail(4)
        forecast_value = recent_weeks.mean()
        method = "4-week moving average"

    else:
        item_df["Month"] = item_df["Date"].dt.to_period("M")
        monthly_orders = item_df.groupby("Month")["Inventory_To_Order"].sum().sort_index()
        recent_months = monthly_orders.tail(3)
        forecast_value = recent_months.mean()
        method = "3-month moving average"

    item_df["Month"] = item_df["Date"].dt.to_period("M")
    monthly_history = item_df.groupby("Month")["Inventory_To_Order"].sum().sort_index()

    return {
        "item": item_name,
        "period": period,
        "forecasted_quantity": format_quantity_value(forecast_value, unit),
        "unit": unit,
        "method": method,
        "monthly_history": {
            str(month): format_quantity_value(value, unit)
            for month, value in monthly_history.items()
        },
    }


def is_whole_number_unit(unit: str):
    return unit.strip().lower() in {"piece", "pieces", "unit", "units", "each"}


def format_quantity_value(value: float, unit: str):
    numeric_value = max(0, float(value))

    if is_whole_number_unit(unit):
        return int(ceil(numeric_value))

    return round(numeric_value, 2)


def format_unit(unit: str, quantity: float):
    normalized_unit = unit.strip()
    lower_unit = normalized_unit.lower()

    if lower_unit in {"kg", "g", "ml"}:
        return lower_unit

    if lower_unit in {"liter", "liters", "litre", "litres"}:
        return "liter" if abs(quantity - 1) < 1e-6 else "liters"

    if lower_unit in {"pieces", "piece"}:
        return "piece" if abs(quantity - 1) < 1e-6 else "pieces"

    if lower_unit in {"units", "unit"}:
        return "unit" if abs(quantity - 1) < 1e-6 else "units"

    return normalized_unit if abs(quantity - 1) < 1e-6 else f"{normalized_unit}s"


def format_quantity_with_unit(quantity: float, unit: str):
    return f"{quantity} {format_unit(unit, quantity)}"


def calculate_operational_minimum(request: PredictRequest):
    projected_stock_after_lead_time = request.Current_Stock - (request.Daily_Usage * request.Lead_Time)
    required_reorder = max(0, request.Reorder_Level - projected_stock_after_lead_time)
    waste_multiplier = 1 + max(0, request.Waste_Percentage) / 100

    return required_reorder * waste_multiplier


def classify_risk(quantity: float):
    if quantity < 10:
        risk = "Low"
    elif quantity < 50:
        risk = "Medium"
    else:
        risk = "High"

    return risk


def build_reorder_summary(model_prediction: float, operational_minimum: float, unit: str, item: str):
    final_prediction = max(model_prediction, operational_minimum)
    display_quantity = format_quantity_value(final_prediction, unit)
    display_model_prediction = format_quantity_value(model_prediction, unit)
    display_operational_minimum = format_quantity_value(operational_minimum, unit)
    unit_clean = format_unit(unit, display_quantity)
    adjusted_by_guardrail = operational_minimum > model_prediction

    return {
        "risk_level": classify_risk(display_quantity),
        "predicted_order": display_quantity,
        "model_prediction": display_model_prediction,
        "operational_minimum": display_operational_minimum,
        "adjusted_by_guardrail": adjusted_by_guardrail,
        "unit": unit_clean,
        "summary": f"The recommended order is {display_quantity} {unit_clean} of {item}.",
        "explanation": (
            "The ML estimate was below the operational minimum needed to cover lead-time usage and restore stock "
            "to the reorder level, so the recommendation was raised."
            if adjusted_by_guardrail
            else "The ML estimate is above the operational minimum needed for the current stock, usage, and lead time."
        ),
    }


@app.get("/")
def home():
    return {
        "message": "StockSense AI API is running.",
        "routes": ["/health", "/predict", "/chat", "/items"],
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "items_loaded": len(df) > 0,
    }


@app.get("/items")
def get_items():
    return {"items": get_known_items()}


@app.post("/predict")
def predict_inventory(request: PredictRequest):
    input_df = pd.DataFrame([request.model_dump()])

    operational_minimum = calculate_operational_minimum(request)
    model_adjustment = float(model.predict(input_df)[0])
    model_prediction = max(0, operational_minimum + model_adjustment)

    summary = build_reorder_summary(
        model_prediction=model_prediction,
        operational_minimum=operational_minimum,
        unit=request.Unit,
        item=request.Item_Name,
    )

    return {
        "item": request.Item_Name,
        "predicted_order": summary["predicted_order"],
        "model_prediction": summary["model_prediction"],
        "model_adjustment": round(model_adjustment, 2),
        "operational_minimum": summary["operational_minimum"],
        "adjusted_by_guardrail": summary["adjusted_by_guardrail"],
        "unit": summary["unit"],
        "risk_level": summary["risk_level"],
        "message": summary["summary"],
        "explanation": summary["explanation"],
    }


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.lower().strip()

    detected_item = detect_item(message)
    detected_period = detect_period(message)
    human_period = format_period(detected_period)

    inventory_intent_words = [
        "buy",
        "order",
        "need",
        "forecast",
        "month",
        "week",
        "tomorrow",
        "today",
        "stock",
        "inventory",
        "how much",
        "purchase",
    ]

    is_inventory_question = any(word in message for word in inventory_intent_words)

    if message in ["hi", "hello", "hey", "help"]:
        return {
            "reply": (
                "Hi, I'm StockSense AI. I can help forecast ingredient orders, explain inventory predictions, "
                "and suggest ways to reduce waste. Try asking: 'How much milk should I buy next month?'"
            )
        }

    if detected_item is None and is_inventory_question:
        sample_items = get_known_items()[:6]

        return {
            "reply": (
                "I don't see that item in the restaurant inventory data, so I can't create an order forecast for it. "
                f"Try asking about items like {', '.join(sample_items)}."
            )
        }

    if detected_item and is_inventory_question:
        result = forecast_item(detected_item, detected_period)

        if "error" in result:
            return {"reply": result["error"]}

        history = result.get("monthly_history", {})
        history_text = ""

        if history:
            recent_history = list(history.items())[-3:]
            history_text = " Recent monthly totals were: " + ", ".join(
                [f"{month}: {format_quantity_with_unit(qty, result['unit'])}" for month, qty in recent_history]
            ) + "."

        return {
            "reply": (
                f"Based on recent inventory trends, you should plan to buy about "
                f"{format_quantity_with_unit(result['forecasted_quantity'], result['unit'])} of {result['item']} "
                f"for {human_period}. "
                f"This estimate uses a {result['method']}.{history_text} "
                f"You can also ask me why this amount may be high or how to reduce waste."
            )
        }

    if "why" in message or "high" in message:
        return {
            "reply": (
                "A higher reorder amount is usually caused by higher daily usage, longer supplier lead time, "
                "low current stock, seasonal demand, or expected waste. In this system, daily usage and lead time "
                "are two of the strongest drivers of the prediction."
            )
        }

    if "waste" in message and ("reduce" in message or "lower" in message):
        return {
            "reply": (
                "To reduce waste, you can lower orders for slow-moving items, review spoilage trends, "
                "adjust safety stock, and compare actual usage against predicted demand each week."
            )
        }

    if "waste" in message:
        return {
            "reply": (
                "Waste percentage represents the expected portion of inventory lost due to spoilage, trimming, "
                "over-preparation, or unused stock. A higher waste percentage usually increases reorder quantity."
            )
        }

    if "seasonal" in message:
        return {
            "reply": (
                "Seasonal factor adjusts demand based on seasonal patterns. For example, if demand is expected "
                "to rise during a busy month, the seasonal factor increases the recommended order."
            )
        }

    if "lead time" in message:
        return {
            "reply": (
                "Lead time is the number of days between placing an order and receiving it. Longer lead times "
                "usually increase reorder quantities because the restaurant needs enough inventory to avoid stockouts."
            )
        }

    return {
        "reply": (
            "I can help with inventory forecasting, reorder explanations, and waste reduction. "
            "For example, ask: 'How much milk should I buy next month?' or 'Why is my chicken order high?'"
        )
    }


handler = Mangum(app, lifespan="off") if Mangum else None
