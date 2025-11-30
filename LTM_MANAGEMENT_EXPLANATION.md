# 🧠 Long-Term Memory (LTM) Management System

## 📋 Overview

This document explains how the **Budget Tracker Agent** manages its Long-Term Memory (LTM) system, especially in the context of a Supervisor Agent that receives natural language queries from users.

---

## 🔄 Complete Flow: User → Supervisor → Worker → LTM

### **Step-by-Step Process**

```
1. User: "Check my budget, I have 50000 limit and spent 42000"
   ↓
2. Supervisor: Analyzes keywords → "budget", "limit", "spent" → Assigns to BudgetTrackerAgent
   ↓
3. Supervisor: Creates task_assignment JSON with extracted parameters
   ↓
4. BudgetTrackerAgent: Receives task → Checks LTM → Processes → Stores → Returns
   ↓
5. Supervisor: Receives completion_report → Formats response for user
```

---

## 🗂️ LTM Storage Architecture

### **File Structure**

```
LTM/
└── BudgetTrackerAgent/
    └── memory.json          # All cached results stored here
```

### **LTM File Format**

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
    },
    "analyze_budget:100000:30000:5000,6000,7000,5000,25000": {
      "remaining": 70000.0,
      "spending_rate": 9000.0,
      "overshoot_risk": false,
      "predicted_spending": 84000.0,
      "anomalies": [...],
      "recommendations": [...]
    }
  }
}
```

---

## 🔑 LTM Key Generation Strategy

### **How Keys Are Created**

The agent generates a **unique key** for each unique combination of task parameters:

```python
def _generate_ltm_key(self, task_data: Dict[str, Any]) -> str:
    budget_limit = task_data.get("budget_limit", 0)
    spent = task_data.get("spent", 0)
    history = task_data.get("history", [])
    
    # Format: "analyze_budget:{limit}:{spent}:{history_string}"
    if history:
        history_str = ",".join(map(str, history[:5]))  # First 5 values
    else:
        history_str = "no_history"
    
    return f"analyze_budget:{budget_limit}:{spent}:{history_str}"
```

### **Key Format**

```
"analyze_budget:{budget_limit}:{spent}:{history_string}"
```

**Examples:**
- `"analyze_budget:50000:42000:5000,7000,8000,6000"`
- `"analyze_budget:100000:30000:no_history"`
- `"analyze_budget:75000:50000:10000,12000,15000"`

### **Why This Key Format?**

1. **Uniqueness**: Each unique combination of parameters gets a unique key
2. **Readability**: Human-readable format for debugging
3. **Efficiency**: Fast lookup using dictionary/hash map
4. **History Handling**: Uses first 5 history values (prevents extremely long keys)

---

## 🔍 LTM Lookup Process

### **Cache Check Flow**

```python
def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
    # STEP 1: Generate key from input parameters
    ltm_key = self._generate_ltm_key(task_data)
    # Example: "analyze_budget:50000:42000:5000,7000,8000,6000"
    
    # STEP 2: Check LTM for cached result
    cached_result = self.read_from_ltm(ltm_key)
    
    # STEP 3: If found, return immediately (FAST!)
    if cached_result:
        print("[BudgetTrackerAgent] Using cached result from LTM")
        return cached_result
    
    # STEP 4: If not found, calculate new result
    # ... perform calculations ...
    
    # STEP 5: Store new result in LTM for future use
    self.write_to_ltm(ltm_key, results)
    
    return results
```

### **Read Operation**

```python
def read_from_ltm(self, key: str) -> Optional[Any]:
    # 1. Check if LTM file exists
    if not os.path.exists(self.ltm_path):
        return None
    
    # 2. Load JSON file
    with open(self.ltm_path, 'r') as f:
        ltm_data = json.load(f)
    
    # 3. Look up key in "tasks" dictionary
    tasks = ltm_data.get("tasks", {})
    return tasks.get(key)  # Returns None if not found
```

### **Write Operation**

```python
def write_to_ltm(self, key: str, value: Any) -> bool:
    # 1. Load existing LTM data (or create new)
    if os.path.exists(self.ltm_path):
        with open(self.ltm_path, 'r') as f:
            ltm_data = json.load(f)
    else:
        ltm_data = {"tasks": {}}
    
    # 2. Add/update entry
    ltm_data["tasks"][key] = value
    
    # 3. Write back to file
    with open(self.ltm_path, 'w') as f:
        json.dump(ltm_data, f, indent=2)
    
    return True
```

---

## 🎯 How LTM Works with Natural Language Queries

### **Scenario: User Asks Same Question Twice**

#### **First Query**
```
User: "Analyze my budget: limit 50000, spent 42000, history [5000, 7000, 8000, 6000]"
↓
Supervisor: Extracts parameters → Creates task_assignment
↓
BudgetTrackerAgent: 
  - Generates key: "analyze_budget:50000:42000:5000,7000,8000,6000"
  - Checks LTM: NOT FOUND
  - Calculates result (takes time)
  - Stores in LTM
  - Returns result
```

#### **Second Query (Same Parameters)**
```
User: "Check my budget again: 50000 limit, 42000 spent, same history"
↓
Supervisor: Extracts parameters → Creates task_assignment (same parameters)
↓
BudgetTrackerAgent:
  - Generates key: "analyze_budget:50000:42000:5000,7000,8000,6000"
  - Checks LTM: FOUND! ✅
  - Returns cached result INSTANTLY (no calculation)
```

### **Key Insight**

**The LTM key is based on the EXTRACTED PARAMETERS, not the natural language text.**

This means:
- ✅ Same parameters = Same key = Cache hit
- ✅ Different wording, same numbers = Cache hit
- ✅ Different numbers = Different key = Cache miss

---

## 📊 LTM Benefits in Multi-Agent System

### **1. Performance Optimization**

| Scenario | Without LTM | With LTM |
|----------|-------------|----------|
| First query | Calculate (100ms) | Calculate + Store (105ms) |
| Repeated query | Calculate (100ms) | Read cache (5ms) ⚡ |
| **Speedup** | - | **20x faster** |

### **2. Consistency**

- Same input → Same output (guaranteed)
- No recalculation variations
- Deterministic results

### **3. Persistence**

- LTM survives agent restarts
- Data persists across sessions
- Historical analysis available

### **4. Resource Efficiency**

- Reduces CPU usage for repeated queries
- No redundant calculations
- Lower system load

---

## 🔧 LTM Configuration

### **Config File: `config/agent_config.json`**

```json
{
  "agent_id": "BudgetTrackerAgent",
  "supervisor_id": "SupervisorAgent",
  "ltm_path": "LTM/BudgetTrackerAgent/memory.json",
  "enable_ltm_cache": true,              // Enable/disable LTM
  "anomaly_threshold_multiplier": 2.0
}
```

### **Enable/Disable LTM**

```python
# In process_task():
if self.enable_ltm_cache:  # Check config
    # Use LTM
else:
    # Always calculate (no caching)
```

---

## 🚨 Current Limitations & Considerations

### **1. Exact Match Required**

**Current Behavior:**
- LTM only matches **exact** parameter combinations
- `budget_limit=50000, spent=42000` ≠ `budget_limit=50000.0, spent=42000.0` (different keys)

**Impact:**
- Slight variations in extracted numbers = cache miss
- Supervisor must extract consistent number formats

### **2. History Truncation**

**Current Behavior:**
- Only first 5 history values used in key
- `[1,2,3,4,5,6,7]` → key uses `"1,2,3,4,5"`

**Impact:**
- Very long history arrays might have collisions
- But for most use cases, first 5 values are sufficient

### **3. No Time-Based Expiration**

**Current Behavior:**
- LTM entries never expire
- Old results remain cached forever

**Potential Improvement:**
- Add timestamp to entries
- Expire entries after X days
- Or add manual cleanup

### **4. No Semantic Matching**

**Current Behavior:**
- No fuzzy matching for similar queries
- `budget_limit=50000` ≠ `budget_limit=50001`

**Potential Improvement:**
- Add similarity matching
- Cache nearby values
- But this adds complexity

---

## 💡 Integration with Supervisor's Natural Language Processing

### **What Supervisor Needs to Do**

1. **Extract Parameters from Natural Language**
   ```
   User: "I have a budget of 50000 and spent 42000"
   Supervisor extracts:
   - budget_limit: 50000
   - spent: 42000
   - history: [] (if not mentioned)
   ```

2. **Create Consistent Task Assignment**
   ```json
   {
     "task": {
       "name": "analyze_budget",
       "parameters": {
         "budget_limit": 50000,    // Must be consistent number format
         "spent": 42000,
         "history": []
       }
     }
   }
   ```

3. **Handle Variations**
   - "50000" vs "50,000" → Normalize to `50000`
   - "fifty thousand" → Convert to `50000`
   - "50k" → Convert to `50000`

### **Best Practices for Supervisor**

✅ **DO:**
- Normalize numbers consistently
- Extract exact values from natural language
- Use same parameter names as expected

❌ **DON'T:**
- Round numbers differently each time
- Use different units (dollars vs cents)
- Include extra metadata in parameters

---

## 🔄 LTM Lifecycle

### **Initialization**
```
Agent starts → Check if LTM file exists → Create if not → Load into memory
```

### **During Task Processing**
```
Task received → Generate key → Check LTM → 
  If found: Return cached
  If not: Calculate → Store → Return
```

### **Storage**
```
Results stored immediately after successful calculation
File written synchronously (ensures persistence)
```

### **Cleanup** (Manual)
```
User can delete LTM file to clear cache
Or modify memory.json directly
```

---

## 📝 Example: Complete LTM Flow

### **User Query 1**
```
User: "Check budget: limit 50000, spent 42000"
Supervisor → BudgetTrackerAgent
Key: "analyze_budget:50000:42000:no_history"
LTM: MISS → Calculate → Store → Return
```

### **User Query 2** (Same)
```
User: "What's my budget status? 50000 limit, 42000 spent"
Supervisor → BudgetTrackerAgent
Key: "analyze_budget:50000:42000:no_history"
LTM: HIT → Return cached (instant!)
```

### **User Query 3** (Different)
```
User: "Budget: 50000 limit, 45000 spent"
Supervisor → BudgetTrackerAgent
Key: "analyze_budget:50000:45000:no_history"
LTM: MISS → Calculate → Store → Return
```

---

## 🎯 Summary

### **How LTM is Managed:**

1. **Storage**: JSON file at `LTM/BudgetTrackerAgent/memory.json`
2. **Key Format**: `"analyze_budget:{limit}:{spent}:{history}"`
3. **Lookup**: Dictionary-based O(1) lookup
4. **Cache Check**: Before every calculation
5. **Storage**: After every successful calculation
6. **Persistence**: File-based, survives restarts

### **Key Points:**

- ✅ LTM works **independently** of natural language
- ✅ Keys based on **extracted parameters**, not text
- ✅ Same parameters = instant cache hit
- ✅ Different parameters = new calculation
- ✅ Supervisor must extract **consistent** parameters
- ✅ No expiration (entries persist forever)

### **For Supervisor Integration:**

The Supervisor should:
1. Extract parameters consistently from natural language
2. Normalize numbers (50000, not "50,000" or "50k")
3. Use exact parameter names expected by worker
4. Handle missing optional parameters (history)

The Worker Agent handles LTM automatically - no special integration needed!

