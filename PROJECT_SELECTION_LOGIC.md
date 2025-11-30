# 🎯 Project Selection Logic - How the System Chooses Which Project

## Overview

The system uses a **priority-based decision tree** to determine which project to use for a budget operation. Here's the complete flow:

---

## 🔄 Complete Decision Flow

```
User sends query
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Extract Information from Query                 │
└─────────────────────────────────────────────────────────┘
    ↓
QueryParser analyzes natural language:
    - Extracts project_name (if mentioned)
    - Extracts budget parameters
    - Extracts intent
    ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: Project Resolution (Priority Order)             │
└─────────────────────────────────────────────────────────┘
    ↓
    ├─→ Priority 1: project_id in request body?
    │   └─→ YES → Use that project_id (verify exists)
    │       └─→ EXISTS → ✅ Use it
    │       └─→ NOT EXISTS → ❌ Continue to next priority
    │
    ├─→ Priority 2: project_name extracted from query?
    │   └─→ YES → Look up project by name
    │       └─→ FOUND → ✅ Use that project_id
    │       └─→ NOT FOUND → Create new project with that name
    │           └─→ ✅ Use newly created project
    │
    └─→ Priority 3: No project specified?
        └─→ Use current/active project
            └─→ EXISTS → ✅ Use it
            └─→ NOT EXISTS → Create "Default Project"
                └─→ ✅ Use default project
```

---

## 📋 Detailed Step-by-Step

### **Step 1: Query Parsing**

When you send a query like:
```json
{
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent",
  "project_id": null  // Optional - can be provided in request
}
```

The `QueryParser` (using OpenAI) extracts:
- `project_name`: "Website Redesign" ✅ (detected from natural language)
- `budget_limit`: 50000
- `spent`: 42000
- `intent`: "check"

---

### **Step 2: Project Resolution Function**

The `resolve_project_id()` function follows this logic:

```python
def resolve_project_id(agent, project_id=None, project_name=None):
    # PRIORITY 1: Direct project_id provided?
    if project_id:
        if agent.get_project(project_id):  # Verify exists
            return project_id  # ✅ Use it
        return None  # Doesn't exist, continue
    
    # PRIORITY 2: Project name extracted from query?
    if project_name:
        found_id = agent.find_project_by_name(project_name)
        if found_id:
            return found_id  # ✅ Found by name
        return None  # Not found, caller will create it
    
    # PRIORITY 3: No project specified - use current
    return agent.get_current_project_id()  # ✅ Current project or None
```

---

### **Step 3: Auto-Creation Logic**

After `resolve_project_id()` returns, the API endpoint handles auto-creation:

```python
# If project not found but name was mentioned, create it
if not project_id and project_name:
    # Extract budget_limit from query if available
    budget_limit = params.get("budget_limit", 0.0)
    project_id = agent.create_project(project_name, budget_limit)
    if project_id:
        agent.set_current_project(project_id)  # Set as current

# If still no project, use current or create default
if not project_id:
    project_id = agent.get_current_project_id()
    if not project_id:
        # Create a default project
        project_id = agent.create_project("Default Project", 0.0)
        if project_id:
            agent.set_current_project(project_id)
```

---

## 🎯 Priority Examples

### **Example 1: Project ID in Request (Highest Priority)**

```json
POST /api/query
{
  "query": "Check my budget: 50000 limit, 42000 spent",
  "project_id": "project_abc123"  // ← Explicit project_id
}
```

**Decision:**
1. ✅ `project_id` provided → Use `project_abc123`
2. Verify it exists → ✅ Use it
3. **Result:** Uses `project_abc123` regardless of query content

---

### **Example 2: Project Name in Query (Second Priority)**

```json
POST /api/query
{
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent"
  // No project_id in request
}
```

**Decision:**
1. ❌ No `project_id` in request
2. ✅ QueryParser extracts `project_name: "Website Redesign"`
3. Look up "Website Redesign" by name
   - **If found:** ✅ Use that project
   - **If not found:** ✅ Create new project "Website Redesign" → Use it

**Result:** Uses "Website Redesign" project (created if needed)

---

### **Example 3: No Project Mentioned (Third Priority)**

```json
POST /api/query
{
  "query": "Check my budget: 50000 limit, 42000 spent"
  // No project mentioned, no project_id
}
```

**Decision:**
1. ❌ No `project_id` in request
2. ❌ No `project_name` extracted from query
3. ✅ Use current/active project
   - **If current exists:** ✅ Use it
   - **If no current:** ✅ Create "Default Project" → Use it

**Result:** Uses current project or creates default

---

### **Example 4: Project Name in Query + project_id in Request**

```json
POST /api/query
{
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent",
  "project_id": "project_xyz789"  // ← Explicit override
}
```

**Decision:**
1. ✅ `project_id` provided → **Priority 1 wins!**
2. Use `project_xyz789` (ignores "Website Redesign" from query)

**Result:** Uses `project_xyz789` (explicit override takes precedence)

---

## 🔍 How Project Name Detection Works

The `QueryParser` uses OpenAI to detect project names from patterns like:

- **"for [Project Name] project"**
  - "Check budget **for Website Redesign project**"
  - Extracts: `project_name = "Website Redesign"`

- **"in [Project Name]"**
  - "How much remaining **in Marketing Campaign**?"
  - Extracts: `project_name = "Marketing Campaign"`

- **"[Project Name] project"**
  - "**Website Redesign project** budget status"
  - Extracts: `project_name = "Website Redesign"`

- **"project [Project Name]"**
  - "Budget for **project Mobile App**"
  - Extracts: `project_name = "Mobile App"`

The OpenAI model is trained to recognize these patterns and extract the project name.

---

## 📊 Decision Matrix

| Request Has | Query Has | Current Project | Result |
|-------------|-----------|----------------|---------|
| `project_id` | - | - | ✅ Use `project_id` |
| - | `project_name` | - | ✅ Use project by name (create if needed) |
| - | - | Exists | ✅ Use current project |
| - | - | None | ✅ Create "Default Project" |

---

## 🎯 Key Points

1. **Explicit `project_id` always wins** - If provided in request, it's used regardless of query content

2. **Project name from query is second priority** - If detected, system looks it up or creates it

3. **Current project is fallback** - If nothing specified, uses the active/current project

4. **Auto-creation is smart** - If project name mentioned but doesn't exist, creates it automatically

5. **Default project safety net** - If no project exists at all, creates "Default Project"

---

## 💡 Best Practices

### **For Explicit Control:**
```json
{
  "query": "Check my budget",
  "project_id": "project_abc123"  // Explicit control
}
```

### **For Natural Language:**
```json
{
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent"
  // Let system detect and create if needed
}
```

### **For Current Project:**
```json
{
  "query": "How much remaining?"
  // Uses current project automatically
}
```

---

## 🔧 Code Location

The logic is implemented in:
- **`api/routes.py`** - `resolve_project_id()` function (lines 27-58)
- **`api/routes.py`** - `process_natural_language_query()` endpoint (lines 61-161)
- **`query_parser.py`** - `detect_intent_and_extract()` method (extracts project_name)

---

This ensures the system always knows which project to use, with clear priority rules! 🎯

