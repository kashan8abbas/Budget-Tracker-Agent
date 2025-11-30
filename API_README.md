# Budget Tracker Agent API

REST API backend for the Budget Tracker Agent with MongoDB Atlas integration.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure MongoDB (already done in `config/agent_config.json`):
```json
{
  "mongo_uri": "your_mongodb_connection_string",
  "mongo_db_name": "your_database_name"
}
```

3. Set OpenAI API key (for natural language queries):
```bash
export OPENAI_API_KEY="your_openai_api_key"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
```

## Running the API

### Option 1: Using uvicorn directly
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using Python
```bash
python app.py
```

The API will be available at:
- **API Base URL**: `http://localhost:8000`
- **Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### 1. Health Check
**GET** `/api/health`

Check if the service and MongoDB are connected.

**Response:**
```json
{
  "status": "healthy",
  "mongodb_connected": true,
  "database": "MERNApp"
}
```

### 2. Natural Language Query
**POST** `/api/query`

Process a natural language query about budget.

**Request:**
```json
{
  "query": "Check my budget: 50000 limit, 42000 spent"
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
  "response": "You currently have $8,000 remaining from your $50,000 budget..."
}
```

### 3. Analyze Budget
**POST** `/api/analyze`

Analyze budget with structured parameters (no natural language processing).

**Request:**
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

**Response:**
```json
{
  "success": true,
  "remaining": 8000.0,
  "spending_rate": 6500.0,
  "overshoot_risk": false,
  "predicted_spending": 42000.0,
  "anomalies": [],
  "recommendations": [...],
  "response": "..."
}
```

### 4. Update Budget
**POST** `/api/update`

Update budget information (spent, budget_limit, or history).

**Request:**
```json
{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000
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
    "history": [5000],
    "last_updated": "2025-11-29T20:00:00Z"
  }
}
```

### 5. Get Current Budget
**GET** `/api/budget`

Get the current budget state from LTM.

**Response:**
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

## Example Usage

### Using cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Natural language query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check my budget: 50000 limit, 42000 spent"}'

# Analyze budget
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "budget_limit": 50000,
      "spent": 42000,
      "history": [5000, 7000, 8000, 6000]
    },
    "intent": "check"
  }'

# Update budget
curl -X POST http://localhost:8000/api/update \
  -H "Content-Type: application/json" \
  -d '{
    "update_type": "add",
    "update_field": "spent",
    "update_value": 5000
  }'

# Get current budget
curl http://localhost:8000/api/budget
```

### Using Python

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/api/health")
print(response.json())

# Natural language query
response = requests.post(
    f"{BASE_URL}/api/query",
    json={"query": "Check my budget: 50000 limit, 42000 spent"}
)
print(response.json())

# Analyze budget
response = requests.post(
    f"{BASE_URL}/api/analyze",
    json={
        "parameters": {
            "budget_limit": 50000,
            "spent": 42000,
            "history": [5000, 7000, 8000, 6000]
        },
        "intent": "check"
    }
)
print(response.json())
```

### Using JavaScript/Fetch

```javascript
// Natural language query
fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Check my budget: 50000 limit, 42000 spent'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Deployment

### Local Development
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment

1. **Using uvicorn with workers:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

2. **Using Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

3. **Using cloud platforms:**
   - **Heroku**: Add `Procfile` with `web: uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Railway**: Auto-detects FastAPI
   - **AWS/GCP/Azure**: Use container services or serverless functions

## Environment Variables

- `OPENAI_API_KEY`: Required for natural language queries
- `MONGODB_URI`: Optional (can be set in config file)
- `PORT`: Optional (defaults to 8000)

## Notes

- The API automatically uses MongoDB Atlas if configured, otherwise falls back to file-based LTM
- Natural language queries require OpenAI API key
- All endpoints return JSON responses
- CORS is enabled for all origins (configure for production)

