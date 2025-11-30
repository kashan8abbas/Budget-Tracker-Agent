# ⚡ Postman Quick Reference - Your Replit API

## 🎯 Your Base URL

```
https://Budget-Tracker-Agent.i222728.repl.co
```

**Replace with your actual Replit URL if different!**

---

## 🚀 Quick Start in Postman

### Step 1: Import Collection
1. Open Postman
2. Click **Import** (top left)
3. Select file: `Budget_Tracker_Agent_API.postman_collection.json`
4. All endpoints will be imported!

### Step 2: Set Base URL
1. Click on the collection name: **"Budget Tracker Agent API"**
2. Go to **Variables** tab
3. Change `base_url` from `http://localhost:8000` to:
   ```
   https://Budget-Tracker-Agent.i222728.repl.co
   ```
4. Click **Save**

### Step 3: Test Health Endpoint
1. Open **"Health Check"** request
2. Click **Send**
3. Should return: `{"status": "healthy", ...}`

---

## 📝 All Endpoints (Copy & Paste Ready)

### 1. Health Check
```
GET https://Budget-Tracker-Agent.i222728.repl.co/api/health
```

### 2. Natural Language Query
```
POST https://Budget-Tracker-Agent.i222728.repl.co/api/query
Content-Type: application/json

{
  "query": "Check my budget: 50000 limit, 42000 spent"
}
```

### 3. Analyze Budget
```
POST https://Budget-Tracker-Agent.i222728.repl.co/api/analyze
Content-Type: application/json

{
  "parameters": {
    "budget_limit": 50000,
    "spent": 42000,
    "history": [5000, 6000, 7000]
  },
  "intent": "check"
}
```

### 4. Create Project
```
POST https://Budget-Tracker-Agent.i222728.repl.co/api/projects
Content-Type: application/json

{
  "project_name": "My Project",
  "budget_limit": 100000,
  "description": "Test project"
}
```

### 5. List Projects
```
GET https://Budget-Tracker-Agent.i222728.repl.co/api/projects
```

### 6. Get Current Budget
```
GET https://Budget-Tracker-Agent.i222728.repl.co/api/budget
```

### 7. Update Budget
```
POST https://Budget-Tracker-Agent.i222728.repl.co/api/update
Content-Type: application/json

{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000
}
```

### 8. Get Project by ID
```
GET https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}
```

### 9. Update Project
```
PUT https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}
Content-Type: application/json

{
  "project_name": "Updated Name",
  "budget_limit": 60000
}
```

### 10. Delete Project
```
DELETE https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}
```

### 11. Set Current Project
```
POST https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}/set-current
```

### 12. Get Project Budget
```
GET https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}/budget
```

---

## 🎯 Recommended Test Sequence

1. ✅ **Health Check** - Verify API is running
2. ✅ **Create Project** - Create a test project (save the `project_id`)
3. ✅ **Natural Language Query** - Test: `"Check my budget: 50000 limit, 42000 spent"`
4. ✅ **Analyze Budget** - Test structured analysis
5. ✅ **List Projects** - See all your projects
6. ✅ **Get Current Budget** - Check budget status

---

## 💡 Pro Tips

1. **Use Collection Variables**: Set `base_url` once in collection variables
2. **Save Responses**: Right-click response → Save as Example
3. **Use Environment**: Create environment with `base_url` variable
4. **Test in Browser**: Visit `/docs` for interactive Swagger UI

---

## 🔗 Interactive Docs

Test endpoints directly in browser:
```
https://Budget-Tracker-Agent.i222728.repl.co/docs
```

---

For detailed instructions, see `POSTMAN_TESTING_GUIDE.md`


