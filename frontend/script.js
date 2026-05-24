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

const apiUrlInput = document.querySelector("#apiUrl");
const apiStatus = document.querySelector("#apiStatus");
const itemSelect = document.querySelector("#Item_Name");
const predictForm = document.querySelector("#predictForm");
const predictionResult = document.querySelector("#predictionResult");
const chatForm = document.querySelector("#chatForm");
const chatMessage = document.querySelector("#chatMessage");
const chatLog = document.querySelector("#chatLog");
const loadItemsButton = document.querySelector("#loadItemsButton");

const savedApiUrl = localStorage.getItem("stocksenseApiUrl") || "http://localhost:8000";
apiUrlInput.value = savedApiUrl;

function getApiUrl() {
  return apiUrlInput.value.trim().replace(/\/$/, "");
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
  localStorage.setItem("stocksenseApiUrl", getApiUrl());

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

function showPrediction(data) {
  predictionResult.innerHTML = `
    <span>${data.risk_level} reorder risk</span>
    <strong>${data.predicted_order} ${data.unit}</strong>
    <p>${data.message}</p>
  `;
}

function addChatMessage(text, role) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  bubble.textContent = text;
  chatLog.appendChild(bubble);
  chatLog.scrollTop = chatLog.scrollHeight;
}

itemSelect.addEventListener("change", () => fillDefaults(itemSelect.value));
apiUrlInput.addEventListener("change", loadItems);
loadItemsButton.addEventListener("click", loadItems);

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

