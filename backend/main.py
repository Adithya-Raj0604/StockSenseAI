from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "reorder_model_tuned.pkl"
DATA_PATH = BASE_DIR / "model" / "restaurant_inventory_with_targets.csv"


# ============================================================
# LOAD MODEL AND DATA
# ============================================================

model = joblib.load(MODEL_PATH)

df = pd.read_csv(DATA_PATH)
df.columns = df.columns.str.strip()
df["Date"] = pd.to_datetime(df["Date"])


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="StockSense AI API",
    description="ML reorder prediction and rule-based inventory chatbot.",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_known_items():
    return sorted(df["Item_Name"].dropna().unique().tolist())


def detect_item(message: str):
    message = message.lower()

    for item in get_known_items():
        if item.lower() in message:
            return item

    return None


def detect_period(message: str):
    message = message.lower()

    if "tomorrow" in message or "next day" in message:
        return "next_day"

    if "today" in message:
        return "today"

    if "this week" in message:
        return "this_week"

    if "next week" in message:
        return "next_week"

    if "this month" in message:
        return "this_month"

    if "next month" in message:
        return "next_month"

    if "week" in message:
        return "next_week"

    if "month" in message:
        return "next_month"

    return "next_month"


def format_period(period: str):
    mapping = {
        "today": "today",
        "next_day": "tomorrow",
        "this_week": "this week",
        "next_week": "next week",
        "this_month": "this month",
        "next_month": "next month"
    }

    return mapping.get(period, period.replace("_", " "))


def forecast_item(item_name: str, period: str = "next_month"):
    item_df = df[df["Item_Name"].str.lower() == item_name.lower()].copy()

    if item_df.empty:
        return {
            "error": f"No inventory data found for item: {item_name}"
        }

    item_df = item_df.sort_values("Date")
    unit = item_df["Unit"].mode()[0]

    if period in ["today", "next_day"]:
        recent_days = item_df.tail(7)
        forecast_value = recent_days["Inventory_To_Order"].mean()
        method = "7-day moving average"

    elif period in ["this_week", "next_week"]:
        item_df["Week"] = item_df["Date"].dt.to_period("W")

        weekly_orders = (
            item_df.groupby("Week")["Inventory_To_Order"]
            .sum()
            .sort_index()
        )

        recent_weeks = weekly_orders.tail(4)
        forecast_value = recent_weeks.mean()
        method = "4-week moving average"

    else:
        item_df["Month"] = item_df["Date"].dt.to_period("M")

        monthly_orders = (
            item_df.groupby("Month")["Inventory_To_Order"]
            .sum()
            .sort_index()
        )

        recent_months = monthly_orders.tail(3)
        forecast_value = recent_months.mean()
        method = "3-month moving average"

    item_df["Month"] = item_df["Date"].dt.to_period("M")

    monthly_history = (
        item_df.groupby("Month")["Inventory_To_Order"]
        .sum()
        .sort_index()
    )

    return {
        "item": item_name,
        "period": period,
        "forecasted_quantity": round(float(forecast_value), 2),
        "unit": unit,
        "method": method,
        "monthly_history": {
            str(month): round(float(value), 2)
            for month, value in monthly_history.items()
        }
    }


def build_reorder_summary(prediction: float, unit: str, item: str):
    if prediction < 10:
        risk = "Low"
    elif prediction < 50:
        risk = "Medium"
    else:
        risk = "High"

    unit_clean = unit if abs(prediction - 1) < 1e-6 else unit + "s"

    return {
        "risk_level": risk,
        "summary": f"The recommended order is {prediction:.2f} {unit_clean} of {item}."
    }


# ============================================================
# ROUTES
# ============================================================

@app.get("/")
def home():
    return {
        "message": "StockSense AI API is running.",
        "routes": ["/predict", "/chat", "/items"]
    }


@app.get("/items")
def get_items():
    return {
        "items": get_known_items()
    }


@app.post("/predict")
def predict_inventory(request: PredictRequest):
    input_df = pd.DataFrame([request.dict()])

    prediction = model.predict(input_df)[0]
    prediction = max(0, float(prediction))

    summary = build_reorder_summary(
        prediction=prediction,
        unit=request.Unit,
        item=request.Item_Name
    )

    return {
        "item": request.Item_Name,
        "predicted_order": round(prediction, 2),
        "unit": request.Unit,
        "risk_level": summary["risk_level"],
        "message": summary["summary"]
    }


@app.post("/chat")
def chat(request: ChatRequest):
    message = request.message.lower().strip()

    detected_item = detect_item(message)
    detected_period = detect_period(message)
    human_period = format_period(detected_period)

    inventory_intent_words = [
        "buy", "order", "need", "forecast", "month", "week",
        "tomorrow", "today", "stock", "inventory", "how much", "purchase"
    ]

    is_inventory_question = any(word in message for word in inventory_intent_words)

    if message in ["hi", "hello", "hey", "help"]:
        return {
            "reply": (
                "Hi, I’m StockSense AI. I can help forecast ingredient orders, explain inventory predictions, "
                "and suggest ways to reduce waste. Try asking: 'How much milk should I buy next month?'"
            )
        }

    if detected_item is None and is_inventory_question:
        sample_items = get_known_items()[:6]

        return {
            "reply": (
                "I don’t see that item in the restaurant inventory data, so I can’t create an order forecast for it. "
                f"Try asking about items like {', '.join(sample_items)}."
            )
        }

    if detected_item and is_inventory_question:
        result = forecast_item(detected_item, detected_period)

        if "error" in result:
            return {
                "reply": result["error"]
            }

        history = result.get("monthly_history", {})
        history_text = ""

        if history:
            recent_history = list(history.items())[-3:]
            history_text = " Recent monthly totals were: " + ", ".join(
                [f"{month}: {qty} {result['unit']}" for month, qty in recent_history]
            ) + "."

        return {
            "reply": (
                f"Based on recent inventory trends, you should plan to buy about "
                f"{result['forecasted_quantity']} {result['unit']} of {result['item']} "
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