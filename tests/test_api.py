from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True
    assert response.json()["items_loaded"] is True


def test_items_returns_known_inventory():
    response = client.get("/items")

    assert response.status_code == 200
    assert "Milk" in response.json()["items"]


def test_chat_forecasts_known_item():
    response = client.post("/chat", json={"message": "How much milk should I buy next month?"})

    assert response.status_code == 200
    assert "Milk" in response.json()["reply"]
    assert "next month" in response.json()["reply"]


def test_predict_returns_reorder_recommendation():
    payload = {
        "Item_Name": "Milk",
        "Category": "Veg",
        "Subcategory": "Dairy",
        "Unit": "liter",
        "Current_Stock": 18.25,
        "Reorder_Level": 8.9,
        "Daily_Usage": 6.0,
        "Lead_Time": 4.0,
        "Price_per_Unit": 50.0,
        "Seasonal_Factor": 1.43,
        "Waste_Percentage": 4.7,
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200
    assert response.json()["item"] == "Milk"
    assert response.json()["predicted_order"] >= 0
    assert response.json()["risk_level"] in ["Low", "Medium", "High"]

