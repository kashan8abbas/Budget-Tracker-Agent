# Postman API Routes - Budget Tracker Agent

Base URL: `http://localhost:8000`

## 1. Health Check

**GET** `/api/health`

Check if the service and MongoDB are connected.

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/api/health`
- Headers: None required

**Response:**
```json
{
  "status": "healthy",
  "mongodb_connected": true,
  "database": "MERNApp"
}
```

---

## 2. Natural Language Query

**POST** `/api/query`

Process a natural language query about budget (requires OpenAI API key).

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/query`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "query": "Check my budget: 50000 limit, 42000 spent"
}
```

**Example Queries:**
```json
// Check budget
{
  "query": "Check my budget: 50000 limit, 42000 spent"
}

// Update spending
{
  "query": "I spent 5000 today"
}

// Predict overspending
{
  "query": "Will I exceed my budget? Budget is 50000, spent 42000, history [5000, 7000, 8000, 6000]"
}

// Analyze with history
{
  "query": "Analyze my spending: budget 100000, spent 30000, history [5000, 6000, 7000, 8000, 4000]"
}

// Get recommendations
{
  "query": "Give me recommendations for my budget: 50000 limit, 45000 spent"
}
```

**Response:**
```json
{
  "success": true,
  "remaining": 8000.0,
  "spending_rate": null,
  "overshoot_risk": false,
  "predicted_spending": 42000.0,
  "anomalies": [],
  "recommendations": [
    "⚠️ WARNING: Only 16.0% of budget remaining",
    "Monitor spending closely and avoid unnecessary expenses"
  ],
  "response": "You currently have $8,000 remaining from your $50,000 budget. That's about 16% left, so you're doing well but should keep an eye on spending."
}
```

---

## 3. Analyze Budget (Structured)

**POST** `/api/analyze`

Analyze budget with structured parameters (no natural language processing needed).

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/analyze`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "parameters": {
    "budget_limit": 50000,
    "spent": 42000,
    "history": [5000, 7000, 8000, 6000]
  },
  "intent": "check"
}
```

**Example Requests:**
```json
// Basic check
{
  "parameters": {
    "budget_limit": 50000,
    "spent": 42000
  },
  "intent": "check"
}

// With spending history
{
  "parameters": {
    "budget_limit": 100000,
    "spent": 30000,
    "history": [5000, 6000, 7000, 8000, 4000]
  },
  "intent": "analyze"
}

// Predict overspending
{
  "parameters": {
    "budget_limit": 50000,
    "spent": 45000,
    "history": [10000, 12000, 11000, 12000]
  },
  "intent": "predict"
}

// Get recommendations
{
  "parameters": {
    "budget_limit": 50000,
    "spent": 48000,
    "history": [5000, 7000, 8000, 6000, 10000, 12000]
  },
  "intent": "recommend"
}
```

**Intent Options:**
- `"check"` - Check budget status (default)
- `"predict"` - Predict overspending risk
- `"analyze"` - Analyze spending patterns
- `"recommend"` - Get recommendations
- `"report"` - Generate full report

**Response:**
```json
{
  "success": true,
  "remaining": 8000.0,
  "spending_rate": 6500.0,
  "overshoot_risk": false,
  "predicted_spending": 42000.0,
  "anomalies": [],
  "recommendations": [
    "⚠️ WARNING: Only 16.0% of budget remaining",
    "Monitor spending closely and avoid unnecessary expenses",
    "Consider reallocating budget from completed or low-priority items"
  ],
  "response": "You have $8,000 remaining from your $50,000 budget..."
}
```

---

## 4. Update Budget

**POST** `/api/update`

Update budget information (spent, budget_limit, or history).

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/update`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000
}
```

**Update Types:**
- `"add"` - Add to existing value (for spent, also adds to history)
- `"replace"` - Replace existing value
- `"set"` - Set value (same as replace)

**Update Fields:**
- `"spent"` - Update spent amount
- `"budget_limit"` - Update budget limit
- `"history"` - Update spending history

**Example Requests:**
```json
// Add to spent (also adds to history)
{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000
}

// Replace spent amount
{
  "update_type": "replace",
  "update_field": "spent",
  "update_value": 45000
}

// Set budget limit
{
  "update_type": "set",
  "update_field": "budget_limit",
  "update_value": 60000
}

// Add to history
{
  "update_type": "add",
  "update_field": "history",
  "update_value": [5000, 6000, 7000]
}

// Replace history
{
  "update_type": "replace",
  "update_field": "history",
  "update_value": [1000, 2000, 3000, 4000, 5000]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully updated spent",
  "budget": {
    "success": true,
    "budget_limit": 50000.0,
    "spent": 47000.0,
    "remaining": 3000.0,
    "history": [5000, 7000, 8000, 6000, 5000],
    "last_updated": "2025-11-29T20:00:00Z"
  }
}
```

---

## 5. Get Current Budget

**GET** `/api/budget`

Get the current budget state from LTM (Long-Term Memory).

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/api/budget`
- Headers: None required

**Response (when budget exists):**
```json
{
  "success": true,
  "budget_limit": 50000.0,
  "spent": 42000.0,
  "remaining": 8000.0,
  "history": [5000, 7000, 8000, 6000],
  "last_updated": "2025-11-29T20:00:00Z"
}
```

**Response (when no budget set):**
```json
{
  "success": true,
  "budget_limit": null,
  "spent": null,
  "remaining": null,
  "history": [],
  "last_updated": null
}
```

---

## 6. Root Endpoint

**GET** `/`

Get API information.

**Request:**
- Method: `GET`
- URL: `http://localhost:8000/`
- Headers: None required

**Response:**
```json
{
  "message": "Budget Tracker Agent API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/health"
}
```

---

## Postman Collection Setup

### Step 1: Create a New Collection
1. Open Postman
2. Click "New" → "Collection"
3. Name it: "Budget Tracker Agent API"

### Step 2: Set Collection Variables
1. Click on the collection
2. Go to "Variables" tab
3. Add variable:
   - Variable: `base_url`
   - Initial Value: `http://localhost:8000`
   - Current Value: `http://localhost:8000`

### Step 3: Create Requests

For each route above, create a new request:

1. **Health Check**
   - Method: `GET`
   - URL: `{{base_url}}/api/health`

2. **Natural Language Query**
   - Method: `POST`
   - URL: `{{base_url}}/api/query`
   - Headers: `Content-Type: application/json`
   - Body: raw JSON (use examples above)

3. **Analyze Budget**
   - Method: `POST`
   - URL: `{{base_url}}/api/analyze`
   - Headers: `Content-Type: application/json`
   - Body: raw JSON (use examples above)

4. **Update Budget**
   - Method: `POST`
   - URL: `{{base_url}}/api/update`
   - Headers: `Content-Type: application/json`
   - Body: raw JSON (use examples above)

5. **Get Current Budget**
   - Method: `GET`
   - URL: `{{base_url}}/api/budget`

6. **Root**
   - Method: `GET`
   - URL: `{{base_url}}/`

---

## Quick Test Sequence

1. **Health Check** → Should return `{"status": "healthy", ...}`
2. **Get Current Budget** → May return empty if no budget set
3. **Analyze Budget** → Test with sample data
4. **Update Budget** → Add some spending
5. **Get Current Budget** → Should show updated values
6. **Natural Language Query** → Test with a query string

---

## Common Issues

### Connection Refused
- Make sure the server is running: `uvicorn app:app --reload --host 0.0.0.0 --port 8000`
- Check if port 8000 is available

### 400 Bad Request
- Check JSON syntax in request body
- Ensure `Content-Type: application/json` header is set
- Verify all required fields are present

### 500 Internal Server Error
- Check server logs for error details
- Verify MongoDB connection (check `/api/health`)
- Ensure OpenAI API key is set (for `/api/query` endpoint)

### Natural Language Query Not Working
- Ensure `OPENAI_API_KEY` environment variable is set
- Check if OpenAI API key is valid
- Verify you have credits in your OpenAI account

---

## Response Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error (check logs)

