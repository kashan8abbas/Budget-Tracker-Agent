# 🔗 Accessing Your API in Replit

Since your Budget Tracker Agent is a **FastAPI backend API** (not a website), the Preview tab will show "no webpage to preview" - **this is completely normal!**

## ✅ Your API is Running!

Even though there's no visual preview, your API is live and accessible. Here's how to use it:

## Step 1: Get Your Public URL

1. Look at the top of your Replit window
2. You'll see a **public URL** like: `https://your-repl-name.your-username.repl.co`
3. Or click the **"Open in new tab"** icon next to the webview

## Step 2: Access API Endpoints

Open these URLs in a **new browser tab** (not the Preview tab):

### 📋 Main Endpoints:

1. **Root/Info**: 
   ```
   https://your-repl-name.your-username.repl.co/
   ```
   Shows API information

2. **Health Check**: 
   ```
   https://your-repl-name.your-username.repl.co/api/health
   ```
   Verify your API is working

3. **Interactive API Docs** (Swagger UI): 
   ```
   https://your-repl-name.your-username.repl.co/docs
   ```
   **⭐ This is the best way to test your API!**

4. **Alternative API Docs** (ReDoc): 
   ```
   https://your-repl-name.your-username.repl.co/redoc
   ```

## Step 3: Test Your API

### Option A: Use the Interactive Docs (Easiest)

1. Open: `https://your-repl-name.your-username.repl.co/docs`
2. You'll see all available endpoints
3. Click on any endpoint to expand it
4. Click **"Try it out"**
5. Fill in the request body
6. Click **"Execute"**
7. See the response!

### Option B: Use curl or Postman

**Test Health Endpoint:**
```bash
curl https://your-repl-name.your-username.repl.co/api/health
```

**Test Query Endpoint:**
```bash
curl -X POST https://your-repl-name.your-username.repl.co/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check my budget: 50000 limit, 42000 spent"}'
```

## Available API Endpoints

Your API has these endpoints:

### Main Endpoints:
- `GET /` - API information
- `GET /api/health` - Health check
- `POST /api/query` - Natural language budget query
- `POST /api/analyze` - Analyze budget from JSON
- `POST /api/update` - Update budget information

### Project Management:
- `POST /api/projects` - Create a project
- `GET /api/projects` - List all projects
- `GET /api/projects/{project_id}` - Get project details
- `PUT /api/projects/{project_id}` - Update project
- `DELETE /api/projects/{project_id}` - Delete project
- `POST /api/projects/{project_id}/set-current` - Set current project
- `GET /api/projects/{project_id}/budget` - Get project budget

### Budget Info:
- `GET /api/budget` - Get current budget status

## ⚠️ Important: Set Your Secrets!

Before testing endpoints that need API keys, make sure you've set:

1. Click the **🔒 Secrets** tab in Replit
2. Add these secrets:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `MONGODB_URI` - Your MongoDB connection string
   - `MONGO_DB_NAME` - Database name (optional, defaults to `budget_tracker`)

**Without these secrets, some endpoints won't work!**

## Quick Test

1. **First, test the health endpoint** (doesn't need secrets):
   ```
   https://your-repl-name.your-username.repl.co/api/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Then, open the interactive docs**:
   ```
   https://your-repl-name.your-username.repl.co/docs
   ```
   This is the best way to explore and test all endpoints!

## Troubleshooting

### "No webpage to preview"
✅ **This is normal!** Your API is running, just open the URLs above in a new tab.

### Endpoints return errors
- Check that secrets are set (🔒 Secrets tab)
- Check the Console tab for error messages
- Verify your MongoDB connection string is correct

### Can't access the URL
- Make sure the app is running (green ▶️ button)
- Check the Console tab for startup errors
- Wait a few seconds after clicking Run

### Slow response
- Free tier Repls may sleep after inactivity
- First request after sleep can be slow (30-60 seconds)
- Use UptimeRobot to keep it awake (see REPLIT_QUICK_START.md)

---

**Remember**: The Preview tab is for websites with HTML. Your API is working perfectly - just access it via the URLs above! 🚀


