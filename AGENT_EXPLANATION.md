# 📊 Budget Tracker Agent - Complete Explanation

## 🎯 What Does This Agent Do?

The **Budget Tracker Agent** is a Worker AI Agent in a multi-agent system that:

1. **Analyzes Budget Status** - Calculates remaining budget and spending patterns
2. **Predicts Overspending** - Forecasts if you'll exceed your budget limit
3. **Detects Anomalies** - Identifies unusual spending spikes in your history
4. **Provides Recommendations** - Suggests actions to stay within budget
5. **Remembers Past Analyses** - Stores results in Long-Term Memory (LTM) for faster future responses

---

## 🔄 How It Works (Step-by-Step Workflow)

### **Step 1: Receive Task Assignment**
```
Supervisor Agent → Budget Tracker Agent
"Hey, analyze this budget: limit=50000, spent=42000, history=[5000,7000,8000,6000]"
```

### **Step 2: Check Long-Term Memory (LTM)**
- Agent generates a unique key: `"analyze_budget:50000:42000:5000,7000,8000,6000"`
- Checks if this exact analysis was done before
- **If found in LTM**: Returns cached result immediately (fast!)
- **If not found**: Proceeds to Step 3

### **Step 3: Process Task (Rule-Based Analysis)**

The agent performs **5 calculations**:

#### **3.1 Calculate Remaining Budget**
```python
remaining = budget_limit - spent
# Example: 50000 - 42000 = 8000
```

#### **3.2 Calculate Spending Rate**
```python
if history exists:
    spending_rate = average(history)
    # Example: (5000 + 7000 + 8000 + 6000) / 4 = 6500 per period
```

#### **3.3 Predict Overspend Risk**
```python
predicted_spending = spent + (spending_rate × remaining_periods)
if predicted_spending > budget_limit:
    overshoot_risk = True
# Example: 42000 + (6500 × 4) = 68000 > 50000 → RISK!
```

#### **3.4 Detect Anomalies**
```python
mean = average(history)
std = standard_deviation(history)
threshold = mean + (2 × std)

for each value in history:
    if value > threshold:
        mark as anomaly
# Example: If 25000 > (6500 + 2×std) → ANOMALY detected
```

#### **3.5 Generate Recommendations**
Based on:
- Remaining budget percentage
- Overshoot risk status
- Spending patterns

Examples:
- "⚠️ HIGH RISK: Reduce spending by 10-20%"
- "✅ Good budget health: Continue current patterns"

### **Step 4: Store in LTM**
- Saves the complete analysis result to `LTM/BudgetTrackerAgent/memory.json`
- Key format: `"analyze_budget:{limit}:{spent}:{history}"`
- Next time same input → instant cached response

### **Step 5: Send Completion Report**
```
Budget Tracker Agent → Supervisor Agent
{
  "status": "SUCCESS",
  "results": {
    "remaining": 8000,
    "overshoot_risk": true,
    "recommendations": [...]
  }
}
```

---

## 📥 Input Format (What the Agent Expects)

### **Required JSON Structure**

The agent expects a **task_assignment** message from the Supervisor:

```json
{
  "message_id": "unique-id-123",
  "sender": "SupervisorAgent",
  "recipient": "BudgetTrackerAgent",
  "type": "task_assignment",
  "task": {
    "name": "analyze_budget",
    "priority": 1,
    "parameters": {
      "budget_limit": <number>,    // REQUIRED: Total budget limit
      "spent": <number>,            // REQUIRED: Amount already spent
      "history": [<numbers>]        // OPTIONAL: Array of past spending amounts
    }
  },
  "timestamp": "2025-11-29T19:00:00Z"
}
```

### **Parameter Details**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `budget_limit` | number | ✅ Yes | Total budget available | `50000` |
| `spent` | number | ✅ Yes | Amount already spent | `42000` |
| `history` | array of numbers | ❌ No | Past spending amounts (daily/weekly/monthly) | `[5000, 7000, 8000, 6000]` |

### **Input Examples**

#### **Example 1: Basic Analysis (No History)**
```json
{
  "message_id": "task-1",
  "sender": "SupervisorAgent",
  "recipient": "BudgetTrackerAgent",
  "type": "task_assignment",
  "task": {
    "name": "analyze_budget",
    "parameters": {
      "budget_limit": 100000,
      "spent": 45000
    }
  }
}
```
**What it does:**
- Calculates remaining: `100000 - 45000 = 55000`
- No spending rate (no history)
- No prediction (no history)
- Basic recommendations based on remaining percentage

#### **Example 2: Full Analysis (With History)**
```json
{
  "message_id": "task-2",
  "sender": "SupervisorAgent",
  "recipient": "BudgetTrackerAgent",
  "type": "task_assignment",
  "task": {
    "name": "analyze_budget",
    "parameters": {
      "budget_limit": 50000,
      "spent": 42000,
      "history": [5000, 7000, 8000, 6000]
    }
  }
}
```
**What it does:**
- Calculates remaining: `50000 - 42000 = 8000`
- Calculates spending rate: `(5000+7000+8000+6000)/4 = 6500`
- Predicts: `42000 + (6500×4) = 68000` → **RISK!**
- Detects anomalies (if any)
- Generates detailed recommendations

#### **Example 3: Anomaly Detection**
```json
{
  "message_id": "task-3",
  "sender": "SupervisorAgent",
  "recipient": "BudgetTrackerAgent",
  "type": "task_assignment",
  "task": {
    "name": "analyze_budget",
    "parameters": {
      "budget_limit": 100000,
      "spent": 30000,
      "history": [5000, 6000, 7000, 5000, 25000, 6000]
    }
  }
}
```
**What it does:**
- Detects `25000` as anomaly (exceeds mean + 2×std)
- Reports anomaly with index, value, and deviation

---

## 📤 Output Format (What the Agent Returns)

### **Completion Report Structure**

```json
{
  "message_id": "uuid-generated",
  "sender": "BudgetTrackerAgent",
  "recipient": "SupervisorAgent",
  "type": "completion_report",
  "related_message_id": "original-task-id",
  "status": "SUCCESS" | "FAILURE",
  "results": {
    "remaining": <number>,              // Budget remaining
    "spending_rate": <number | null>,   // Average spending per period
    "overshoot_risk": true | false,     // Will budget be exceeded?
    "predicted_spending": <number>,      // Forecasted total spending
    "anomalies": [                       // Unusual spending detected
      {
        "index": 4,
        "value": 25000.0,
        "threshold": 24748.02,
        "deviation": 16000.0
      }
    ],
    "recommendations": [                // Actionable advice
      "⚠️ HIGH RISK: Predicted spending exceeds budget",
      "Reduce upcoming spending by 10-20%",
      "Consider pausing low-priority expenses"
    ]
  },
  "timestamp": "2025-11-29T14:19:52Z"
}
```

### **Results Field Details**

| Field | Type | Description |
|-------|------|-------------|
| `remaining` | number | `budget_limit - spent` |
| `spending_rate` | number or null | Average of history array (null if no history) |
| `overshoot_risk` | boolean | `true` if predicted spending > budget limit |
| `predicted_spending` | number | Forecasted total: `spent + (spending_rate × periods)` |
| `anomalies` | array | Spending values exceeding `mean + 2×std` |
| `recommendations` | array of strings | Actionable budget management advice |

---

## 🧠 Long-Term Memory (LTM) System

### **How LTM Works**

1. **Storage Location**: `LTM/BudgetTrackerAgent/memory.json`

2. **Key Generation**: 
   ```
   "analyze_budget:{budget_limit}:{spent}:{history_string}"
   ```
   Example: `"analyze_budget:50000:42000:5000,7000,8000,6000"`

3. **Cache Lookup Flow**:
   ```
   Input received → Generate key → Check LTM → 
   If found: Return cached result (FAST!)
   If not found: Calculate → Store → Return
   ```

4. **LTM File Structure**:
   ```json
   {
     "tasks": {
       "analyze_budget:50000:42000:5000,7000,8000,6000": {
         "remaining": 8000.0,
         "spending_rate": 6500.0,
         "overshoot_risk": true,
         "predicted_spending": 68000.0,
         "anomalies": [],
         "recommendations": [...]
       }
     }
   }
   ```

### **Benefits of LTM**
- ⚡ **Faster responses** for repeated queries
- 💾 **Persistent memory** across agent restarts
- 🔄 **No redundant calculations**

---

## 🧮 Business Logic Rules

### **Rule 1: Remaining Budget**
```
remaining = budget_limit - spent
```
Always calculated, regardless of history.

### **Rule 2: Spending Rate**
```
if history exists and len(history) > 0:
    spending_rate = sum(history) / len(history)
else:
    spending_rate = null
```

### **Rule 3: Overspend Prediction**
```
if spending_rate exists:
    periods_remaining = len(history)  # Estimate
    predicted_spending = spent + (spending_rate × periods_remaining)
    
    if predicted_spending > budget_limit:
        overshoot_risk = true
```

### **Rule 4: Anomaly Detection**
```
if len(history) > 2:
    mean = average(history)
    std = standard_deviation(history)
    threshold = mean + (2.0 × std)
    
    for each value in history:
        if value > threshold:
            mark as anomaly
```

### **Rule 5: Recommendations**
Based on:
- **Overshoot Risk**: "Reduce spending by 10-20%"
- **Remaining < 20%**: "Warning: Low budget remaining"
- **Remaining < 50%**: "Monitor spending closely"
- **Remaining ≥ 50%**: "Good budget health"

---

## 🚀 How to Use

### **Standalone Testing**
```bash
# Run with sample input
python main.py --input sample_input.json

# Run with custom input
python main.py --input my_budget_data.json

# Use default sample_input.json
python main.py
```

### **Integration with Supervisor**
The agent is ready to receive messages from Supervisor Agent via:
- HTTP POST endpoint (can be added)
- Message queue
- Direct function call: `agent.handle_incoming_message(json_string)`

---

## 📋 Summary

**What it does**: Analyzes budgets, predicts overspending, detects anomalies, provides recommendations

**How it works**: Receives task → Checks LTM → Calculates → Stores → Reports

**Input**: JSON with `budget_limit`, `spent`, optional `history` array

**Output**: JSON with analysis results, predictions, anomalies, recommendations

**Special Feature**: Long-Term Memory caching for instant repeated queries

---

## ✅ Validation Rules

- ✅ `budget_limit` ≥ 0
- ✅ `spent` ≥ 0
- ✅ `spent` can be > `budget_limit` (overspending already occurred)
- ✅ `history` array can be empty or omitted
- ✅ All numbers can be integers or floats

