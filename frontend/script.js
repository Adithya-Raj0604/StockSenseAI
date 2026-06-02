const itemDefaults = {
  Chicken: { Category: "Non-Veg", Subcategory: "Meat", Unit: "kg", Current_Stock: 8.36, Reorder_Level: 3.16, Daily_Usage: 3.25, Lead_Time: 3, Price_per_Unit: 250, Seasonal_Factor: 0.9, Waste_Percentage: 3.06 },
  Eggs: { Category: "Non-Veg", Subcategory: "Poultry", Unit: "pieces", Current_Stock: 16.5, Reorder_Level: 6.94, Daily_Usage: 4, Lead_Time: 2, Price_per_Unit: 6, Seasonal_Factor: 0.87, Waste_Percentage: 1.52 },
  Milk: { Category: "Veg", Subcategory: "Dairy", Unit: "liter", Current_Stock: 18.25, Reorder_Level: 8.9, Daily_Usage: 6, Lead_Time: 4, Price_per_Unit: 50, Seasonal_Factor: 1.43, Waste_Percentage: 4.7 },
  Mutton: { Category: "Non-Veg", Subcategory: "Meat", Unit: "kg", Current_Stock: 11.2, Reorder_Level: 6.19, Daily_Usage: 1.81, Lead_Time: 3, Price_per_Unit: 600, Seasonal_Factor: 1.07, Waste_Percentage: 3.09 },
  Onion: { Category: "Veg", Subcategory: "Vegetable", Unit: "kg", Current_Stock: 22.35, Reorder_Level: 4.49, Daily_Usage: 4.86, Lead_Time: 4, Price_per_Unit: 35, Seasonal_Factor: 1.23, Waste_Percentage: 4.96 },
  Paneer: { Category: "Veg", Subcategory: "Dairy", Unit: "kg", Current_Stock: 21.45, Reorder_Level: 8.12, Daily_Usage: 2.19, Lead_Time: 1, Price_per_Unit: 450, Seasonal_Factor: 1.11, Waste_Percentage: 2.98 },
  Rice: { Category: "Veg", Subcategory: "Grain", Unit: "kg", Current_Stock: 12.8, Reorder_Level: 3.85, Daily_Usage: 3.58, Lead_Time: 1, Price_per_Unit: 70, Seasonal_Factor: 0.92, Waste_Percentage: 4.17 },
  "Rohu Fish": { Category: "Non-Veg", Subcategory: "Fish", Unit: "kg", Current_Stock: 14.1, Reorder_Level: 9.02, Daily_Usage: 4.92, Lead_Time: 3, Price_per_Unit: 280, Seasonal_Factor: 0.85, Waste_Percentage: 0.85 },
  Sugar: { Category: "Veg", Subcategory: "Grocery", Unit: "kg", Current_Stock: 17.8, Reorder_Level: 8.29, Daily_Usage: 2.26, Lead_Time: 2, Price_per_Unit: 50, Seasonal_Factor: 1.18, Waste_Percentage: 2.6 },
  Tomato: { Category: "Veg", Subcategory: "Vegetable", Unit: "kg", Current_Stock: 12.84, Reorder_Level: 5.34, Daily_Usage: 0.95, Lead_Time: 4, Price_per_Unit: 40, Seasonal_Factor: 0.81, Waste_Percentage: 3.54 },
};

const API_URL = "https://h9wwvfoq84.execute-api.us-east-1.amazonaws.com";
const apiStatus = document.querySelector("#apiStatus");
const itemSelect = document.querySelector("#Item_Name");
const predictForm = document.querySelector("#predictForm");
const predictionResult = document.querySelector("#predictionResult");
const chatForm = document.querySelector("#chatForm");
const chatMessage = document.querySelector("#chatMessage");
const chatLog = document.querySelector("#chatLog");
const loadItemsButton = document.querySelector("#loadItemsButton");
const infoPopover = document.querySelector("#infoPopover");
const infoTitle = document.querySelector("#infoTitle");
const infoBody = document.querySelector("#infoBody");
const infoClose = document.querySelector("#infoClose");

const parameterInfo = {
  Item_Name: {
    title: "Item",
    body: "Identifies which ingredient is being predicted. The model learns item-specific patterns, so the same stock and usage values can produce different recommendations for chicken, milk, rice, or other items.",
  },
  Category: {
    title: "Category",
    body: "Groups the item into a broad inventory type such as Veg or Non-Veg. It gives the model context about storage behavior, demand patterns, and how similar items tend to be reordered.",
  },
  Subcategory: {
    title: "Subcategory",
    body: "Adds a more specific item family such as Dairy, Meat, Vegetable, or Grain. This helps the prediction compare the item against closer inventory peers than category alone.",
  },
  Unit: {
    title: "Unit",
    body: "Defines how the reorder amount is measured, such as kg, liter, or pieces. It keeps the result interpretable and helps the model understand scale when paired with usage and stock values.",
  },
  Current_Stock: {
    title: "Current Stock",
    body: "Shows how much is currently available. Higher current stock usually lowers the recommended order, while low stock raises urgency when daily usage, lead time, or reorder level are high.",
  },
  Reorder_Level: {
    title: "Reorder Level",
    body: "Represents the minimum stock threshold before replenishment is needed. A higher reorder level typically increases the recommendation because the system tries to avoid falling below that safety point.",
  },
  Daily_Usage: {
    title: "Daily Usage",
    body: "Estimates how quickly the item is consumed each day. It is one of the strongest drivers: higher usage increases the order amount, especially when lead time is long or current stock is low.",
  },
  Lead_Time: {
    title: "Lead Time",
    body: "Measures how many days it takes for a supplier order to arrive. Longer lead time usually increases the recommendation because the restaurant must cover more days before restocking.",
  },
  Price_per_Unit: {
    title: "Price Per Unit",
    body: "Captures the cost of each unit. It can help the model learn purchasing behavior, since expensive items may have different stocking patterns than low-cost staples.",
  },
  Seasonal_Factor: {
    title: "Seasonal Factor",
    body: "Adjusts for demand changes during busier or slower periods. Values above 1 suggest higher expected demand and often increase the reorder recommendation.",
  },
  Waste_Percentage: {
    title: "Waste Percentage",
    body: "Estimates expected loss from spoilage, trimming, over-preparation, or unused stock. Higher waste can increase the suggested order because some inventory may not be usable.",
  },
};

function getApiUrl() {
  return API_URL.replace(/\/$/, "");
}

function setStatus(message, mode = "idle") {
  apiStatus.textContent = message;
  apiStatus.dataset.mode = mode;
}

function fillItemSelect(items = Object.keys(itemDefaults)) {
  itemSelect.innerHTML = "";
  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item;
    option.textContent = item;
    itemSelect.appendChild(option);
  });
  fillDefaults(itemSelect.value);
}

function fillDefaults(item) {
  const defaults = itemDefaults[item] || itemDefaults.Milk;
  Object.entries(defaults).forEach(([key, value]) => {
    const input = document.querySelector(`#${key}`);
    if (input) input.value = value;
  });
  updateWholeNumberInputs();
}

function usesWholeNumberUnits() {
  return itemSelect.value === "Eggs" || document.querySelector("#Unit").value.trim().toLowerCase() === "pieces";
}

function updateWholeNumberInputs() {
  const wholeNumberFields = ["Current_Stock", "Reorder_Level", "Daily_Usage"];
  const shouldUseWholeNumbers = usesWholeNumberUnits();

  wholeNumberFields.forEach((fieldId) => {
    const input = document.querySelector(`#${fieldId}`);
    input.step = shouldUseWholeNumbers ? "1" : "0.01";

    if (shouldUseWholeNumbers && input.value !== "") {
      input.value = Math.max(0, Math.round(Number(input.value)));
    }
  });
}

async function request(path, options = {}) {
  const response = await fetch(`${getApiUrl()}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return response.json();
}

async function loadItems() {
  setStatus("Checking API", "busy");

  try {
    const health = await request("/health");
    const data = await request("/items");
    fillItemSelect(data.items.length ? data.items : Object.keys(itemDefaults));
    setStatus(health.status === "ok" ? "API connected" : "API reachable", "ok");
  } catch (error) {
    fillItemSelect();
    setStatus("Using sample defaults", "warn");
  }
}

function readPredictionPayload() {
  const payload = { Item_Name: itemSelect.value };
  new FormData(predictForm).forEach((value, key) => {
    if (key !== "Item_Name") {
      const numericValue = Number(value);
      payload[key] = Number.isNaN(numericValue) ? value : numericValue;
    }
  });
  return payload;
}

function displayUnit(quantity, unit) {
  const numericQuantity = Number(quantity);
  const normalizedUnit = unit.trim().toLowerCase();

  if (["kg", "g", "ml"].includes(normalizedUnit)) {
    return normalizedUnit;
  }

  if (["liter", "liters", "litre", "litres"].includes(normalizedUnit)) {
    return Math.abs(numericQuantity - 1) < 1e-6 ? "liter" : "liters";
  }

  if (normalizedUnit === "pieces" || normalizedUnit === "piece") {
    return Math.abs(numericQuantity - 1) < 1e-6 ? "piece" : "pieces";
  }

  if (normalizedUnit === "units" || normalizedUnit === "unit") {
    return Math.abs(numericQuantity - 1) < 1e-6 ? "unit" : "units";
  }

  return unit;
}

function showPrediction(data) {
  const isEggPieceResult = data.item === "Eggs" || data.unit === "pieces";
  const predictedOrder = isEggPieceResult
    ? Math.ceil(Number(data.predicted_order))
    : Number(data.predicted_order).toFixed(2);
  const modelPrediction = isEggPieceResult
    ? Math.ceil(Number(data.model_prediction))
    : Number(data.model_prediction).toFixed(2);
  const operationalMinimum = isEggPieceResult
    ? Math.ceil(Number(data.operational_minimum))
    : Number(data.operational_minimum).toFixed(2);
  const predictedUnit = displayUnit(predictedOrder, data.unit);
  const modelUnit = displayUnit(modelPrediction, data.unit);
  const minimumUnit = displayUnit(operationalMinimum, data.unit);
  const message = `The recommended order is ${predictedOrder} ${predictedUnit} of ${data.item}.`;
  const explanation = data.adjusted_by_guardrail
    ? `Adjusted from the ML estimate of ${modelPrediction} ${modelUnit}; the operational minimum is ${operationalMinimum} ${minimumUnit} based on stock, reorder level, usage, lead time, and waste.`
    : data.explanation;

  predictionResult.innerHTML = `
    <span>${data.risk_level} reorder risk</span>
    <strong>${predictedOrder} ${predictedUnit}</strong>
    <p>${message}</p>
    <p class="result-detail">${explanation}</p>
  `;
}

function addChatMessage(text, role) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function openParameterInfo(key, button) {
  const info = parameterInfo[key];
  if (!info) return;

  infoTitle.textContent = info.title;
  infoBody.textContent = info.body;
  infoPopover.hidden = false;

  const buttonRect = button.getBoundingClientRect();
  const panelRect = document.querySelector(".forecast-panel").getBoundingClientRect();
  const left = Math.max(16, Math.min(buttonRect.left - panelRect.left, panelRect.width - 356));
  infoPopover.style.left = `${left}px`;
  infoPopover.style.top = `${buttonRect.bottom - panelRect.top + 8}px`;
}

function closeParameterInfo() {
  infoPopover.hidden = true;
}

itemSelect.addEventListener("change", () => fillDefaults(itemSelect.value));
document.querySelector("#Unit").addEventListener("input", updateWholeNumberInputs);
loadItemsButton.addEventListener("click", loadItems);
infoClose.addEventListener("click", closeParameterInfo);

document.querySelectorAll(".info-button").forEach((button) => {
  button.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    openParameterInfo(button.dataset.infoKey, button);
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    closeParameterInfo();
  }
});

document.addEventListener("click", (event) => {
  if (!infoPopover.hidden && !infoPopover.contains(event.target)) {
    closeParameterInfo();
  }
});

predictForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Predicting", "busy");

  try {
    const data = await request("/predict", {
      method: "POST",
      body: JSON.stringify(readPredictionPayload()),
    });
    showPrediction(data);
    setStatus("API connected", "ok");
  } catch (error) {
    setStatus("Prediction failed", "warn");
    predictionResult.innerHTML = `
      <span>Unable to predict</span>
      <strong>Check API URL</strong>
      <p>${error.message}</p>
    `;
  }
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatMessage.value.trim();
  if (!message) return;

  addChatMessage(message, "user");
  chatMessage.value = "";

  try {
    const data = await request("/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    addChatMessage(data.reply, "assistant");
    setStatus("API connected", "ok");
  } catch (error) {
    addChatMessage("I could not reach the API. Check the URL and try again.", "assistant");
    setStatus("Chat failed", "warn");
  }
});

fillItemSelect();
addChatMessage("Ask for reorder forecasts, waste guidance, or why an order is high.", "assistant");
loadItems();
