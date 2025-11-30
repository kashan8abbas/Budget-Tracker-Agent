# 🚀 Postman Testing Guide for Budget Tracker Agent API

## Base URL

Your Replit API base URL is:
```
https://Budget-Tracker-Agent.i222728.repl.co
```

**Replace this with your actual Replit URL if different!**

---

## 📋 All Available Endpoints

### 1. **Health Check** (No authentication needed)
- **Method**: `GET`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/health`
- **Description**: Check if API is running and MongoDB is connected
- **Request Body**: None
- **Expected Response**: 
  ```json
  {
    "status": "healthy",
    "mongodb_connected": true,
    "database": "budget_tracker"
  }
  ```

---

### 2. **Root/Info Endpoint**
- **Method**: `GET`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/`
- **Description**: Get API information
- **Request Body**: None

---

### 3. **Natural Language Query** (Needs GEMINI_API_KEY)
- **Method**: `POST`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/query`
- **Description**: Process natural language queries about budget
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Request Body** (JSON):
  ```json
  {
    "query": "Check my budget: 50000 limit, 42000 spent",
    "project_id": null
  }
  ```
- **Example Queries**:
  ```json
  {"query": "I have a budget of 50000 and spent 42000"}
  {"query": "Will I exceed my budget?"}
  {"query": "I spent 5000 today"}
  {"query": "Analyze my spending with history [5000, 6000, 7000]"}
  ```

---

### 4. **Analyze Budget** (No API key needed)
- **Method**: `POST`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/analyze`
- **Description**: Analyze budget with structured JSON data
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Request Body** (JSON):
  ```json
  {
    "project_id": null,
    "parameters": {
      "budget_limit": 50000,
      "spent": 42000,
      "history": [5000, 6000, 7000, 5000, 25000, 6000]
    },
    "intent": "check"
  }
  ```
- **Intent Options**: `check`, `predict`, `analyze`, `recommend`, `report`

---

### 5. **Update Budget**
- **Method**: `POST`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/update`
- **Description**: Update budget information
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Request Body** (JSON):
  ```json
  {
    "project_id": null,
    "update_type": "add",
    "update_field": "spent",
    "update_value": 5000
  }
  ```
- **Update Types**: `add`, `replace`, `set`
- **Update Fields**: `spent`, `budget_limit`, `history`
- **Update Value**: `float` for spent/budget_limit, `array` for history

---

### 6. **Get Current Budget**
- **Method**: `GET`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/budget`
- **Description**: Get current budget status
- **Query Parameters** (optional):
  - `project_id`: Project ID to get budget for
- **Example**: `https://Budget-Tracker-Agent.i222728.repl.co/api/budget?project_id=your-project-id`

---

### 7. **Create Project**
- **Method**: `POST`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects`
- **Description**: Create a new budget project
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Request Body** (JSON):
  ```json
  {
    "project_name": "Website Redesign",
    "budget_limit": 50000,
    "description": "Redesign company website"
  }
  ```

---

### 8. **List All Projects**
- **Method**: `GET`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects`
- **Description**: Get list of all projects
- **Request Body**: None

---

### 9. **Get Project by ID**
- **Method**: `GET`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}`
- **Description**: Get specific project details
- **Example**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/abc123`

---

### 10. **Update Project**
- **Method**: `PUT`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}`
- **Description**: Update project information
- **Headers**: 
  ```
  Content-Type: application/json
  ```
- **Request Body** (JSON):
  ```json
  {
    "project_name": "Updated Project Name",
    "budget_limit": 60000,
    "description": "Updated description",
    "status": "active"
  }
  ```

---

### 11. **Delete Project**
- **Method**: `DELETE`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}`
- **Description**: Delete a project
- **Request Body**: None

---

### 12. **Set Current Project**
- **Method**: `POST`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}/set-current`
- **Description**: Set a project as the current active project
- **Request Body**: None

---

### 13. **Get Project Budget**
- **Method**: `GET`
- **URL**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/{project_id}/budget`
- **Description**: Get budget information for a specific project
- **Example**: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects/abc123/budget`

---

## 🔧 How to Test in Postman

### Step 1: Open Postman
1. Open Postman application
2. Create a new request or use an existing collection

### Step 2: Set Up Your Base URL
1. Create a new **Environment** in Postman:
   - Click **Environments** → **+** (Create Environment)
   - Name: `Budget Tracker API`
   - Add variable: `base_url` = `https://Budget-Tracker-Agent.i222728.repl.co`
   - Click **Save**

2. Use the environment:
   - Select your environment from the dropdown (top right)
   - In requests, use: `{{base_url}}/api/health`

### Step 3: Test Health Endpoint (Start Here!)

1. **Create New Request**:
   - Method: `GET`
   - URL: `https://Budget-Tracker-Agent.i222728.repl.co/api/health`
   - Click **Send**

2. **Expected Response** (200 OK):
   ```json
   {
     "status": "healthy",
     "mongodb_connected": true,
     "database": "budget_tracker"
   }
   ```

### Step 4: Test Natural Language Query

1. **Create New Request**:
   - Method: `POST`
   - URL: `https://Budget-Tracker-Agent.i222728.repl.co/api/query`

2. **Set Headers**:
   - Key: `Content-Type`
   - Value: `application/json`

3. **Set Body**:
   - Select **Body** tab
   - Choose **raw** and **JSON**
   - Paste:
     ```json
     {
       "query": "Check my budget: 50000 limit, 42000 spent"
     }
     ```

4. **Click Send**

### Step 5: Test Analyze Endpoint

1. **Create New Request**:
   - Method: `POST`
   - URL: `https://Budget-Tracker-Agent.i222728.repl.co/api/analyze`

2. **Set Headers**: `Content-Type: application/json`

3. **Set Body** (raw JSON):
   ```json
   {
     "parameters": {
       "budget_limit": 50000,
       "spent": 42000,
       "history": [5000, 6000, 7000, 5000, 25000, 6000]
     },
     "intent": "check"
   }
   ```

4. **Click Send**

### Step 6: Create a Project

1. **Create New Request**:
   - Method: `POST`
   - URL: `https://Budget-Tracker-Agent.i222728.repl.co/api/projects`

2. **Set Headers**: `Content-Type: application/json`

3. **Set Body** (raw JSON):
   ```json
   {
     "project_name": "My First Project",
     "budget_limit": 100000,
     "description": "Test project"
   }
   ```

4. **Click Send**
5. **Copy the `project_id` from response** - you'll need it for other requests!

---

## 📦 Import Postman Collection

I've created a Postman collection file (`Budget_Tracker_Agent_API.postman_collection.json`) that you can import:

1. Open Postman
2. Click **Import** (top left)
3. Select the file: `Budget_Tracker_Agent_API.postman_collection.json`
4. All endpoints will be imported with example requests!

---

## 🎯 Quick Test Sequence

Test in this order:

1. ✅ **GET** `/api/health` - Verify API is running
2. ✅ **POST** `/api/projects` - Create a project (save the project_id)
3. ✅ **POST** `/api/query` - Test natural language query
4. ✅ **POST** `/api/analyze` - Test structured analysis
5. ✅ **GET** `/api/projects` - List all projects
6. ✅ **GET** `/api/budget` - Get current budget

---

## ⚠️ Common Issues

### "Gemini API key not configured"
- Make sure `GEMINI_API_KEY` is set in Replit Secrets
- Only affects `/api/query` endpoint

### "MongoDB connection failed"
- Check `MONGODB_URI` is set correctly in Replit Secrets
- Verify MongoDB connection string is valid

### "No project specified"
- Create a project first using `POST /api/projects`
- Or include `project_id` in request body

### 404 Not Found
- Check your Replit URL is correct
- Make sure the app is running (green ▶️ button in Replit)

### Slow Response
- Free tier Repls may sleep after inactivity
- First request after sleep can take 30-60 seconds

---

## 💡 Pro Tips

1. **Use Postman Collections**: Import the collection file for easy testing
2. **Save Responses**: Save successful requests as examples
3. **Use Variables**: Store `project_id` in Postman variables for reuse
4. **Test in Sequence**: Create project → Query → Analyze → Update
5. **Check Interactive Docs**: Visit `/docs` in browser for Swagger UI

---

## 🔗 Interactive API Documentation

You can also test endpoints directly in your browser:

**Swagger UI**: `https://Budget-Tracker-Agent.i222728.repl.co/docs`

This provides an interactive interface to test all endpoints!

---

Happy Testing! 🚀


