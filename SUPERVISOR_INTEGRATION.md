# Supervisor Agent Integration Details

This document contains all the information needed to integrate the Budget Tracker Agent with a supervisor agent.

## Integration Details

### 1. Agent Name
```
budget_tracker_agent
```

### 2. Description
```
A budget tracking and analysis agent that monitors spending, predicts overspending risks, detects anomalies in expense patterns, and provides recommendations for budget management. Supports natural language queries and multi-project budget tracking.
```

### 3. Intents
```json
[
  "budget.check",
  "budget.update",
  "budget.predict",
  "budget.recommend",
  "budget.analyze",
  "budget.report",
  "budget.question",
  "budget.list"
]
```

**Intent Descriptions:**
- `budget.check`: Check budget status, remaining amount, current spending
- `budget.update`: Update spending amounts or budget limits
- `budget.predict`: Predict future spending and overspending risks
- `budget.recommend`: Get recommendations for budget management
- `budget.analyze`: Analyze spending patterns, trends, and anomalies
- `budget.report`: Generate budget reports and summaries
- `budget.question`: Answer general questions about budget status
- `budget.list`: List all projects and their budgets

### 4. Endpoint URL
```
https://YOUR-APP-NAME.onrender.com/api/query
```

**Note:** Replace `YOUR-APP-NAME` with your actual Render deployment name. For example:
- `https://budget-tracker-agent.onrender.com/api/query`
- `https://my-budget-agent.onrender.com/api/query`

### 5. Health Check URL
```
https://YOUR-APP-NAME.onrender.com/api/health
```

**Note:** Replace `YOUR-APP-NAME` with your actual Render deployment name.

### 6. Timeout
```
5000
```
(5000 milliseconds = 5 seconds)

---

## API Endpoint Details

### Main Query Endpoint
**POST** `/api/query`

**Request Body:**
```json
{
  "query": "Check my budget status",
  "project_id": "optional-project-id"
}
```

**Response:**
```json
{
  "success": true,
  "project_id": "project_abc123",
  "project_name": "My Project",
  "remaining": 8000.00,
  "spending_rate": 500.00,
  "overshoot_risk": false,
  "predicted_spending": 48000.00,
  "anomalies": [],
  "recommendations": ["Continue monitoring spending patterns"],
  "response": "You currently have $8,000 remaining from your $50,000 budget..."
}
```

### Health Check Endpoint
**GET** `/api/health`

**Response:**
```json
{
  "status": "healthy",
  "mongodb_connected": true,
  "database": "budget_tracker"
}
```

---

## Example Integration Configuration

```json
{
  "agent_name": "budget_tracker_agent",
  "description": "A budget tracking and analysis agent that monitors spending, predicts overspending risks, detects anomalies in expense patterns, and provides recommendations for budget management. Supports natural language queries and multi-project budget tracking.",
  "intents": [
    "budget.check",
    "budget.update",
    "budget.predict",
    "budget.recommend",
    "budget.analyze",
    "budget.report",
    "budget.question",
    "budget.list"
  ],
  "endpoint_url": "https://YOUR-APP-NAME.onrender.com/api/query",
  "health_check_url": "https://YOUR-APP-NAME.onrender.com/api/health",
  "timeout": 5000
}
```

---

## What Can Be Done Through `/api/query` (Primary Endpoint)

✅ **YES - The `/api/query` endpoint can handle ALL core operations through natural language:**

### Budget Operations (All Supported via Natural Language):
- ✅ **Check Budget**: "Check my budget status", "How much remaining?", "What's the budget for Mobile App project?"
- ✅ **Update Spending**: "I spent 5000 today", "Add 3000 to expenses", "Set budget limit to 60000"
- ✅ **Predict Risks**: "Will we exceed budget?", "Predict if we'll overshoot", "Check overspending risk"
- ✅ **Get Recommendations**: "Suggest ways to reduce spending", "How can we prevent overspending?"
- ✅ **Analyze Patterns**: "Analyze my spending", "Find anomalies in expenses", "Show spending trends"
- ✅ **Generate Reports**: "Generate a budget report", "Give me a financial summary"
- ✅ **Answer Questions**: "Are we going over budget?", "What's our financial position?"
- ✅ **List All Projects**: "List all my projects", "Show all projects and their budgets", "List all my projects and their budget"

### Project Operations (Automatically Handled):
- ✅ **Create Projects**: Automatically creates projects when mentioned in queries
  - Example: "Check budget for Website Redesign project" → Creates "Website Redesign" if it doesn't exist
- ✅ **Select Projects**: Automatically selects projects when mentioned
  - Example: "How is Mobile App Development doing?" → Uses "Mobile App Development" project
- ✅ **Multi-Project Support**: Can work with multiple projects by mentioning project names

### What the Query Endpoint Does:
1. **Natural Language Processing**: Understands queries in plain English (and mixed languages)
2. **Intent Detection**: Automatically detects what you want to do (check, update, predict, etc.)
3. **Parameter Extraction**: Extracts budget amounts, project names, and other details from text
4. **Context Awareness**: Uses stored budget data from previous queries
5. **Automatic Project Management**: Creates and selects projects automatically
6. **Conversational Responses**: Returns natural language answers, not just JSON

---

## Additional API Endpoints (Optional - For Programmatic Access)

The agent also supports these structured endpoints for programmatic access (not required for supervisor integration):

- **POST** `/api/analyze` - Direct budget analysis with structured JSON (no natural language)
- **POST** `/api/update` - Update budget with structured JSON
- **GET** `/api/budget` - Get current budget state (for current project)
- **GET** `/api/projects` - List all projects (structured response)
- **POST** `/api/projects` - Create a new project (structured request)
- **GET** `/api/projects/{project_id}` - Get specific project details
- **PUT** `/api/projects/{project_id}` - Update project information
- **DELETE** `/api/projects/{project_id}` - Delete a project
- **POST** `/api/projects/{project_id}/set-current` - Set current project
- **GET** `/api/projects/{project_id}/budget` - Get budget for specific project

**Note:** For supervisor agent integration, you only need `/api/query` - it handles everything through natural language!

### Examples: How `/api/query` Replaces Other Endpoints

Instead of using multiple endpoints, you can use natural language queries:

| Structured Endpoint | Natural Language Query Equivalent |
|---------------------|-----------------------------------|
| `POST /api/analyze` with JSON | `POST /api/query` with `{"query": "Analyze budget: 50000 limit, 42000 spent"}` |
| `POST /api/update` with JSON | `POST /api/query` with `{"query": "I spent 5000 today"}` |
| `GET /api/budget` | `POST /api/query` with `{"query": "Check my budget status"}` |
| `POST /api/projects` with JSON | `POST /api/query` with `{"query": "Check budget for Mobile App project"}` (auto-creates) |
| `GET /api/projects/{id}/budget` | `POST /api/query` with `{"query": "What's the budget for Mobile App project?"}` |

**All operations can be done through the single `/api/query` endpoint!**

---

## Quick Reference

| Field | Value |
|-------|-------|
| **Agent Name** | `budget_tracker_agent` |
| **Description** | Budget tracking and analysis agent with natural language support |
| **Intents** | `["budget.check", "budget.update", "budget.predict", "budget.recommend", "budget.analyze", "budget.report", "budget.question", "budget.list"]` |
| **Endpoint URL** | `https://YOUR-APP-NAME.onrender.com/api/query` |
| **Health Check URL** | `https://YOUR-APP-NAME.onrender.com/api/health` |
| **Timeout** | `5000` (milliseconds) |

---

## Next Steps

1. Replace `YOUR-APP-NAME` in the URLs above with your actual Render deployment name
2. Use the configuration above to integrate with your supervisor agent
3. Test the integration using the health check endpoint first
4. Send test queries to verify the agent responds correctly

---

**Note:** Make sure your Render deployment is active and accessible before integrating with the supervisor agent.

