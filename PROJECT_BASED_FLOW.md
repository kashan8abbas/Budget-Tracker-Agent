# 🏗️ Project-Based Budget Management System - Flow Design

## 📋 Overview

Transform the single-budget system into a **multi-project budget management system** where each project has its own independent budget tracking.

---

## 🎯 Core Concepts

### **Project Entity**
Each project is an independent budget container with:
- **Project ID/Name** (unique identifier)
- **Budget Limit** (per project)
- **Spent Amount** (per project)
- **Spending History** (per project)
- **Metadata** (created_at, last_updated, description, etc.)

### **Key Principle**
- **One Budget = One Project**
- All budget operations are scoped to a specific project
- Projects are isolated from each other

---

## 🗂️ Data Structure Changes

### **MongoDB Schema**

#### **Collection: `projects`**
```json
{
  "_id": ObjectId("..."),
  "project_id": "project_abc123",
  "project_name": "Website Redesign",
  "agent_id": "BudgetTrackerAgent",
  "budget_limit": 50000.0,
  "spent": 42000.0,
  "history": [5000, 7000, 8000, 6000, 10000, 6000],
  "metadata": {
    "description": "Complete website redesign project",
    "created_at": "2025-11-29T10:00:00Z",
    "last_updated": "2025-11-29T20:00:00Z",
    "status": "active" // active, completed, archived
  },
  "created_at": "2025-11-29T10:00:00Z",
  "updated_at": "2025-11-29T20:00:00Z"
}
```

#### **Collection: `tasks` (Updated)**
```json
{
  "_id": ObjectId("..."),
  "key": "project_abc123:analyze_budget:50000:42000:5000,7000,8000",
  "project_id": "project_abc123",
  "agent_id": "BudgetTrackerAgent",
  "value": {
    "remaining": 8000.0,
    "spending_rate": 6500.0,
    "overshoot_risk": false,
    "predicted_spending": 42000.0,
    "anomalies": [],
    "recommendations": [...]
  },
  "updated_at": "2025-11-29T20:00:00Z"
}
```

#### **Collection: `current_project` (Optional - for default project)**
```json
{
  "_id": ObjectId("..."),
  "agent_id": "BudgetTrackerAgent",
  "current_project_id": "project_abc123",
  "updated_at": "2025-11-29T20:00:00Z"
}
```

### **File-Based LTM Structure (Fallback)**
```json
{
  "projects": {
    "project_abc123": {
      "budget_limit": 50000.0,
      "spent": 42000.0,
      "history": [5000, 7000, 8000, 6000],
      "last_updated": "2025-11-29T20:00:00Z"
    },
    "project_xyz789": {
      "budget_limit": 100000.0,
      "spent": 30000.0,
      "history": [5000, 6000, 7000, 8000, 4000],
      "last_updated": "2025-11-29T18:00:00Z"
    }
  },
  "current_project": "project_abc123",
  "tasks": {
    "project_abc123:analyze_budget:50000:42000:5000,7000": {...},
    "project_xyz789:analyze_budget:100000:30000:5000,6000": {...}
  }
}
```

---

## 🔄 API Flow Design

### **1. Project Management Endpoints**

#### **Create Project**
```
POST /api/projects
Body: {
  "project_name": "Website Redesign",
  "budget_limit": 50000,
  "description": "Complete website redesign project" (optional)
}

Response: {
  "success": true,
  "project": {
    "project_id": "project_abc123",
    "project_name": "Website Redesign",
    "budget_limit": 50000.0,
    "spent": 0.0,
    "history": [],
    "created_at": "2025-11-29T10:00:00Z"
  }
}
```

#### **List Projects**
```
GET /api/projects

Response: {
  "success": true,
  "projects": [
    {
      "project_id": "project_abc123",
      "project_name": "Website Redesign",
      "budget_limit": 50000.0,
      "spent": 42000.0,
      "remaining": 8000.0,
      "status": "active",
      "last_updated": "2025-11-29T20:00:00Z"
    },
    ...
  ],
  "current_project": "project_abc123"
}
```

#### **Get Project Details**
```
GET /api/projects/{project_id}

Response: {
  "success": true,
  "project": {
    "project_id": "project_abc123",
    "project_name": "Website Redesign",
    "budget_limit": 50000.0,
    "spent": 42000.0,
    "remaining": 8000.0,
    "history": [5000, 7000, 8000, 6000],
    "metadata": {...},
    "last_updated": "2025-11-29T20:00:00Z"
  }
}
```

#### **Update Project**
```
PUT /api/projects/{project_id}
Body: {
  "project_name": "Website Redesign v2" (optional),
  "budget_limit": 60000 (optional),
  "description": "Updated description" (optional),
  "status": "active" (optional)
}
```

#### **Delete Project**
```
DELETE /api/projects/{project_id}

Response: {
  "success": true,
  "message": "Project deleted successfully"
}
```

#### **Set Current/Active Project**
```
POST /api/projects/{project_id}/set-current

Response: {
  "success": true,
  "message": "Current project set to 'Website Redesign'",
  "project_id": "project_abc123"
}
```

---

### **2. Budget Operations (Project-Scoped)**

#### **Natural Language Query (with Project)**
```
POST /api/query
Body: {
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent",
  "project_id": "project_abc123" (optional - uses current if not provided)
}

OR

Body: {
  "query": "Check my budget: 50000 limit, 42000 spent",
  "project_id": "project_abc123" (required if no project in query)
}
```

**Natural Language Project Detection:**
- "Check budget for **Website Redesign** project"
- "How much remaining in **Project ABC**?"
- "Update spending for **Marketing Campaign**"
- If project not mentioned → use `project_id` from request or current project

#### **Analyze Budget (with Project)**
```
POST /api/analyze
Body: {
  "project_id": "project_abc123" (optional - uses current if not provided),
  "parameters": {
    "budget_limit": 50000,
    "spent": 42000,
    "history": [5000, 7000, 8000, 6000]
  },
  "intent": "check"
}
```

#### **Update Budget (with Project)**
```
POST /api/update
Body: {
  "project_id": "project_abc123" (optional - uses current if not provided),
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000
}
```

#### **Get Project Budget**
```
GET /api/projects/{project_id}/budget

Response: {
  "success": true,
  "project_id": "project_abc123",
  "project_name": "Website Redesign",
  "budget_limit": 50000.0,
  "spent": 42000.0,
  "remaining": 8000.0,
  "history": [5000, 7000, 8000, 6000],
  "last_updated": "2025-11-29T20:00:00Z"
}
```

#### **Get Current Project Budget**
```
GET /api/budget
(No project_id needed - uses current project)

Response: {
  "success": true,
  "project_id": "project_abc123",
  "project_name": "Website Redesign",
  "budget_limit": 50000.0,
  "spent": 42000.0,
  "remaining": 8000.0,
  "history": [5000, 7000, 8000, 6000]
}
```

---

## 🔀 Request Flow Examples

### **Scenario 1: Create and Use a Project**

```
1. User creates project:
   POST /api/projects
   → Creates "Website Redesign" project
   → Returns project_id: "project_abc123"

2. User sets as current:
   POST /api/projects/project_abc123/set-current
   → Sets as active project

3. User queries budget:
   POST /api/query
   Body: {"query": "Check my budget: 50000 limit, 42000 spent"}
   → Uses current project (project_abc123)
   → Stores budget data in project_abc123
   → Returns analysis

4. User updates spending:
   POST /api/update
   Body: {"update_type": "add", "update_field": "spent", "update_value": 5000}
   → Updates project_abc123's spent amount
   → Adds 5000 to history
```

### **Scenario 2: Multiple Projects**

```
1. User has 3 projects:
   - "Website Redesign" (project_abc123)
   - "Marketing Campaign" (project_xyz789)
   - "Mobile App" (project_def456)

2. User queries specific project:
   POST /api/query
   Body: {
     "query": "Check budget for Marketing Campaign: 100000 limit, 30000 spent",
     "project_id": "project_xyz789"
   }
   → Analyzes project_xyz789's budget
   → Doesn't affect other projects

3. User switches current project:
   POST /api/projects/project_def456/set-current
   → Now all operations without project_id use project_def456

4. User queries without project_id:
   POST /api/query
   Body: {"query": "How much remaining?"}
   → Uses current project (project_def456)
   → Returns project_def456's budget
```

### **Scenario 3: Natural Language Project Detection**

```
User: "Check budget for Website Redesign project: 50000 limit, 42000 spent"

Flow:
1. QueryParser extracts:
   - project_name: "Website Redesign"
   - budget_limit: 50000
   - spent: 42000
   - intent: "check"

2. API looks up project by name:
   - Finds project_id: "project_abc123"
   - Uses that project for budget operations

3. If project not found:
   - Option A: Create new project with that name
   - Option B: Return error asking to create project first
```

---

## 🧠 Agent Changes Required

### **BudgetTrackerAgent Modifications**

#### **1. LTM Key Generation (Include Project)**
```python
def _generate_ltm_key(self, task_data: Dict[str, Any], project_id: str = None) -> str:
    project_id = project_id or self.get_current_project_id()
    budget_limit = task_data.get("budget_limit", 0)
    spent = task_data.get("spent", 0)
    history = task_data.get("history", [])
    
    history_str = ",".join(map(str, history[:5])) if history else "no_history"
    
    # Format: "{project_id}:analyze_budget:{limit}:{spent}:{history}"
    return f"{project_id}:analyze_budget:{budget_limit}:{spent}:{history_str}"
```

#### **2. Project-Aware Budget Methods**
```python
def get_current_budget(self, project_id: str = None) -> Optional[Dict[str, Any]]:
    project_id = project_id or self.get_current_project_id()
    # Fetch budget for specific project
    
def update_current_budget(self, project_id: str = None, ...):
    project_id = project_id or self.get_current_project_id()
    # Update budget for specific project
```

#### **3. Project Management Methods**
```python
def create_project(self, project_name: str, budget_limit: float = 0.0) -> str:
    # Create new project, return project_id
    
def list_projects(self) -> List[Dict[str, Any]]:
    # List all projects
    
def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
    # Get project details
    
def set_current_project(self, project_id: str) -> bool:
    # Set active project
    
def delete_project(self, project_id: str) -> bool:
    # Delete project (and its data)
```

---

## 📊 Database Queries (MongoDB)

### **Get Project Budget**
```python
projects_collection.find_one({
    "project_id": "project_abc123",
    "agent_id": "BudgetTrackerAgent"
})
```

### **Update Project Budget**
```python
projects_collection.update_one(
    {"project_id": "project_abc123", "agent_id": "BudgetTrackerAgent"},
    {
        "$set": {
            "spent": 47000.0,
            "history": [5000, 7000, 8000, 6000, 5000],
            "updated_at": datetime.utcnow()
        }
    }
)
```

### **List All Projects**
```python
projects_collection.find({
    "agent_id": "BudgetTrackerAgent"
}).sort("created_at", -1)
```

### **Get Cached Task Result**
```python
tasks_collection.find_one({
    "key": "project_abc123:analyze_budget:50000:42000:5000,7000",
    "project_id": "project_abc123",
    "agent_id": "BudgetTrackerAgent"
})
```

---

## 🎯 Natural Language Query Enhancement

### **Project Detection in Queries**

The QueryParser should extract:
```json
{
  "intent": "check",
  "project_name": "Website Redesign",  // NEW
  "project_id": null,  // Will be resolved from project_name
  "parameters": {
    "budget_limit": 50000,
    "spent": 42000,
    "history": null
  }
}
```

### **Query Examples with Projects**

1. **Explicit Project Mention:**
   - "Check budget for **Website Redesign** project"
   - "How much remaining in **Marketing Campaign**?"
   - "Update spending for **Project ABC**"

2. **Implicit Project (uses current):**
   - "Check my budget" → Uses current project
   - "How much remaining?" → Uses current project
   - "I spent 5000 today" → Uses current project

3. **Project Creation:**
   - "Create project **Mobile App** with budget 75000"
   - "New project: **Website Redesign**, budget 50000"

---

## 🔐 Project ID Generation

### **Options:**

1. **Auto-generated UUID:**
   ```python
   project_id = f"project_{uuid.uuid4().hex[:12]}"
   # Example: "project_abc123def456"
   ```

2. **Slug from Name:**
   ```python
   project_id = project_name.lower().replace(" ", "_").replace("-", "_")
   # "Website Redesign" → "website_redesign"
   ```

3. **User-provided:**
   ```python
   # User provides project_id in request
   project_id = request.project_id
   ```

**Recommendation:** Use UUID for uniqueness, but also store project_name for human readability.

---

## 📝 Migration Strategy

### **From Single Budget to Multi-Project**

1. **Create Default Project:**
   - Migrate existing `current_budget` to a default project
   - Project name: "Default Project" or "Main Budget"
   - Preserve all existing data

2. **Update LTM Keys:**
   - Old: `"analyze_budget:50000:42000:5000,7000"`
   - New: `"default_project:analyze_budget:50000:42000:5000,7000"`

3. **Set Current Project:**
   - Set default project as current
   - All existing queries continue to work

---

## ✅ Implementation Checklist

### **Phase 1: Core Project Management**
- [ ] Add `project_id` to all budget operations
- [ ] Create project management methods in agent
- [ ] Update MongoDB schema (projects collection)
- [ ] Update LTM key generation to include project_id
- [ ] Create project CRUD endpoints

### **Phase 2: Project-Aware Budget Operations**
- [ ] Update `get_current_budget()` to accept project_id
- [ ] Update `update_current_budget()` to accept project_id
- [ ] Update `process_task()` to handle project context
- [ ] Update all API endpoints to accept project_id

### **Phase 3: Natural Language Enhancement**
- [ ] Enhance QueryParser to detect project names
- [ ] Add project name → project_id resolution
- [ ] Support project creation via natural language
- [ ] Update query examples in documentation

### **Phase 4: Migration & Testing**
- [ ] Create migration script for existing data
- [ ] Test project isolation
- [ ] Test multi-project scenarios
- [ ] Update API documentation
- [ ] Update Postman collection

---

## 🎨 UI/UX Considerations (Future)

### **Project Selection**
- Dropdown/selector for current project
- Project switcher in header
- Recent projects list

### **Project Dashboard**
- List all projects with summary
- Quick stats per project
- Project status indicators

### **Project Creation Flow**
- Quick create from query
- Full create form with details
- Duplicate project option

---

## 📚 Summary

### **Key Changes:**
1. ✅ **Projects Collection** - Store each project's budget separately
2. ✅ **Project-Scoped Operations** - All budget ops require/use project_id
3. ✅ **Current Project** - Default project for operations without explicit project_id
4. ✅ **Project Detection** - NLP can identify projects from queries
5. ✅ **Isolated Data** - Each project's data is completely separate

### **Benefits:**
- 🎯 **Organization** - Manage multiple budgets independently
- 🔒 **Isolation** - Projects don't interfere with each other
- 📊 **Scalability** - Easy to add more projects
- 🧠 **Context** - Natural language can identify projects
- 💾 **Persistence** - Each project's history is preserved

---

**Next Steps:** Review this flow, then we can start implementing! 🚀

