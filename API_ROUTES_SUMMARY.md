# 📋 API Routes Summary

Your Budget Tracker API has **12 routes** organized into 2 main categories.

## 📊 Route Count by Category

- **Budget Operations**: 4 routes
- **Project Management**: 7 routes
- **Health Check**: 1 route

**Total: 12 routes**

---

## 🔵 Budget Operations (4 routes)

### 1. `POST /api/query`
**Natural Language Query Processing**
- Process natural language queries about budget
- Extracts parameters, detects intent, analyzes budget
- Supports project name detection
- Returns comprehensive budget analysis

**Example:**
```json
POST /api/query
{
  "query": "Check my budget: 50000 limit, 42000 spent"
}
```

### 2. `POST /api/analyze`
**Structured Budget Analysis**
- Analyze budget with provided JSON parameters
- No natural language processing required
- Direct parameter input

**Example:**
```json
POST /api/analyze
{
  "parameters": {
    "budget_limit": 50000,
    "spent": 42000,
    "history": [5000, 6000, 7000]
  },
  "intent": "check"
}
```

### 3. `POST /api/update`
**Update Budget Information**
- Add, replace, or set budget values
- Update spent, budget_limit, or history
- Supports spending descriptions

**Example:**
```json
POST /api/update
{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000,
  "project_id": "project_123"
}
```

### 4. `GET /api/budget`
**Get Current Budget**
- Get budget for current active project
- Returns budget_limit, spent, remaining, history

**Example:**
```bash
GET /api/budget
```

---

## 🟢 Project Management (7 routes)

### 5. `POST /api/projects`
**Create New Project**
- Create a new project with initial budget
- Returns created project details

**Example:**
```json
POST /api/projects
{
  "project_name": "Website Redesign",
  "budget_limit": 50000,
  "description": "Complete website overhaul"
}
```

### 6. `GET /api/projects`
**List All Projects**
- Get list of all projects
- Shows current active project
- Returns project count

**Example:**
```bash
GET /api/projects
```

### 7. `GET /api/projects/{project_id}`
**Get Project Details**
- Get specific project by ID
- Returns full project information

**Example:**
```bash
GET /api/projects/project_a2a3b989658a
```

### 8. `PUT /api/projects/{project_id}`
**Update Project**
- Update project information
- Can update budget_limit, description, status

**Example:**
```json
PUT /api/projects/project_123
{
  "budget_limit": 75000,
  "description": "Updated description"
}
```

### 9. `DELETE /api/projects/{project_id}`
**Delete Project**
- Delete a project (cannot delete current project)
- Returns deleted project info

**Example:**
```bash
DELETE /api/projects/project_123
```

### 10. `POST /api/projects/{project_id}/set-current`
**Set Current Project**
- Set a project as the active/current project
- All future queries use this project by default

**Example:**
```bash
POST /api/projects/project_123/set-current
```

### 11. `GET /api/projects/{project_id}/budget`
**Get Project Budget**
- Get budget for a specific project
- Returns budget details for that project

**Example:**
```bash
GET /api/projects/project_123/budget
```

---

## 🟡 System Routes (1 route)

### 12. `GET /api/health`
**Health Check**
- Check API and MongoDB connection status
- Returns service health information

**Example:**
```bash
GET /api/health
```

---

## 📊 Route Summary Table

| # | Method | Route | Category | Description |
|---|--------|-------|----------|-------------|
| 1 | POST | `/api/query` | Budget | Natural language query processing |
| 2 | POST | `/api/analyze` | Budget | Structured budget analysis |
| 3 | POST | `/api/update` | Budget | Update budget information |
| 4 | GET | `/api/budget` | Budget | Get current budget |
| 5 | POST | `/api/projects` | Project | Create new project |
| 6 | GET | `/api/projects` | Project | List all projects |
| 7 | GET | `/api/projects/{project_id}` | Project | Get project details |
| 8 | PUT | `/api/projects/{project_id}` | Project | Update project |
| 9 | DELETE | `/api/projects/{project_id}` | Project | Delete project |
| 10 | POST | `/api/projects/{project_id}/set-current` | Project | Set current project |
| 11 | GET | `/api/projects/{project_id}/budget` | Project | Get project budget |
| 12 | GET | `/api/health` | System | Health check |

---

## 🎯 Most Used Routes

**Top 3 Most Common:**
1. `POST /api/query` - Natural language queries (most user-friendly)
2. `GET /api/projects` - List all projects
3. `GET /api/budget` - Quick budget check

---

## 📝 Notes

- All routes are prefixed with `/api`
- All project routes support project-specific operations
- Budget routes can work with current project or specified project
- Health check doesn't require authentication
- All routes return JSON responses

---

## 🔗 Base URL

All routes are accessible at:
```
http://localhost:8000/api/...
```

Or your deployed URL:
```
https://your-domain.com/api/...
```


