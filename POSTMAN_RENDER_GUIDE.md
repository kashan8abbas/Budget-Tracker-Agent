# 🚀 Postman Testing Guide for Render Deployment

## Base URL Format

Your Render API URL will be:
```
https://your-service-name.onrender.com
```

**Find your exact URL in the Render dashboard!**

---

## 📋 How to Find Your Render URL

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click on your service**: "Budget-Tracker-Agent" (or your service name)
3. **Look at the top of the page** - you'll see your public URL
4. **Or check the "Settings" tab** - URL is listed there

**Example Render URLs:**
- `https://budget-tracker-agent.onrender.com`
- `https://budget-tracker-agent-abc123.onrender.com`
- `https://your-service-name.onrender.com`

---

## 🎯 Quick Start in Postman

### Step 1: Get Your Render URL

1. Open Render Dashboard
2. Click on your service
3. Copy the URL from the top (e.g., `https://budget-tracker-agent.onrender.com`)

### Step 2: Test Health Endpoint

**In Postman:**
```
GET https://your-service-name.onrender.com/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "mongodb_connected": true,
  "database": "budget_tracker"
}
```

---

## 📝 All Endpoints for Render

### 1. Health Check
```
GET https://your-service-name.onrender.com/api/health
```

### 2. Root/Info
```
GET https://your-service-name.onrender.com/
```

### 3. Natural Language Query
```
POST https://your-service-name.onrender.com/api/query
Content-Type: application/json

{
  "query": "Check my budget: 50000 limit, 42000 spent"
}
```

### 4. Analyze Budget
```
POST https://your-service-name.onrender.com/api/analyze
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

### 5. Create Project
```
POST https://your-service-name.onrender.com/api/projects
Content-Type: application/json

{
  "project_name": "My Project",
  "budget_limit": 100000,
  "description": "Test project"
}
```

### 6. List Projects
```
GET https://your-service-name.onrender.com/api/projects
```

### 7. Get Current Budget
```
GET https://your-service-name.onrender.com/api/budget
```

### 8. Update Budget
```
POST https://your-service-name.onrender.com/api/update
Content-Type: application/json

{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000
}
```

---

## ⚠️ Important: Render Free Tier Spin-Down

**Render free tier services spin down after 15 minutes of inactivity!**

### First Request After Spin-Down:
- ⏱️ Can take **30-60 seconds** to respond
- This is normal - wait for it!
- Subsequent requests will be fast

### Keep Your Service Awake:

**Option 1: UptimeRobot (Free)**
1. Sign up at https://uptimerobot.com
2. Add a monitor:
   - Type: HTTP(s)
   - URL: `https://your-service-name.onrender.com/api/health`
   - Interval: 5 minutes
3. This will ping your service every 5 minutes

**Option 2: Use a Cron Job**
- Set up a simple cron job to ping your health endpoint

---

## 🔧 Troubleshooting

### Error: "getaddrinfo ENOTFOUND"

**Possible Causes:**
1. **Wrong URL** - Check Render dashboard for exact URL
2. **Service not deployed** - Check Render dashboard status
3. **Service spun down** - Wait 30-60 seconds for first request

**Fix:**
1. Go to Render Dashboard
2. Verify service status is "Live" (green)
3. Copy the exact URL from Render
4. Make sure URL includes `https://`

### Service Status: "Building"

- Wait for build to complete
- Check build logs in Render dashboard
- Build usually takes 2-5 minutes

### Service Status: "Failed"

- Check build logs for errors
- Verify environment variables are set
- Check `requirements.txt` is correct

### Slow Response

- **First request**: Normal (30-60 seconds) - service is spinning up
- **Subsequent requests**: Should be fast
- **After 15 min inactivity**: Will spin down again

---

## ✅ Deployment Checklist

Before testing in Postman:

- [ ] Service is deployed and shows "Live" status in Render
- [ ] Environment variables are set:
  - [ ] `GEMINI_API_KEY`
  - [ ] `MONGODB_URI`
  - [ ] `MONGO_DB_NAME` (optional)
- [ ] Build completed successfully (check logs)
- [ ] You have the correct URL from Render dashboard

---

## 🎯 Test Sequence

1. **Check Service Status**:
   - Go to Render Dashboard
   - Verify service shows "Live" (green)

2. **Test Health Endpoint**:
   ```
   GET https://your-service-name.onrender.com/api/health
   ```
   - First request may take 30-60 seconds (spin-up)
   - Should return: `{"status": "healthy", ...}`

3. **Test Root Endpoint**:
   ```
   GET https://your-service-name.onrender.com/
   ```

4. **Test Interactive Docs**:
   ```
   Open: https://your-service-name.onrender.com/docs
   ```

5. **Test API Endpoints**:
   - Create a project
   - Test natural language query
   - Test analyze endpoint

---

## 💡 Pro Tips

1. **Use Environment Variables in Postman**:
   - Create environment: `base_url` = `https://your-service-name.onrender.com`
   - Use `{{base_url}}/api/health` in requests

2. **Keep Service Awake**:
   - Set up UptimeRobot to ping every 5 minutes
   - Or upgrade to paid tier for always-on

3. **Monitor Logs**:
   - Check Render logs for debugging
   - Logs tab shows real-time output

4. **Test in Browser First**:
   - Open `/docs` endpoint in browser
   - Use Swagger UI to test endpoints
   - Then use Postman for advanced testing

---

## 🔗 Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Your Service**: Check your dashboard for exact URL
- **Interactive Docs**: `https://your-service-name.onrender.com/docs`
- **Health Check**: `https://your-service-name.onrender.com/api/health`

---

## 📦 Import Postman Collection

1. Open Postman
2. Click **Import**
3. Select: `Budget_Tracker_Agent_API.postman_collection.json`
4. Update `base_url` variable to your Render URL
5. Start testing!

---

**Remember**: Render free tier spins down after 15 minutes. First request after spin-down will be slow - this is normal! 🚀


