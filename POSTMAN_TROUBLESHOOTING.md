# 🔧 Postman Troubleshooting - DNS/Connection Errors

## Error: `getaddrinfo ENOTFOUND`

This error means Postman can't find your Replit server. Here's how to fix it:

---

## ✅ Step 1: Get Your Correct Replit URL

The URL in your Replit might be different! Here's how to find it:

### In Replit:

1. **Look at the top of your Replit window** - you'll see your public URL
2. **Or check the Console tab** - the URL is usually displayed there
3. **Or click the "Open in new tab" icon** next to the webview

### Common Replit URL Formats:

- `https://Budget-Tracker-Agent.i222728.repl.co`
- `https://budget-tracker-agent.i222728.repl.co` (lowercase)
- `https://Budget-Tracker-Agent--i222728.repl.co` (with double dash)
- `https://your-repl-name.your-username.repl.co`

**⚠️ Important**: Replit URLs are case-sensitive! Use the exact URL from your Replit dashboard.

---

## ✅ Step 2: Verify Your App is Running

1. **In Replit**, make sure:
   - The green **▶️ Run** button shows the app is running
   - You see output in the Console tab
   - No error messages

2. **Test in Browser First**:
   - Open your Replit URL in a browser: `https://your-actual-url.repl.co/api/health`
   - If it works in browser but not Postman, it's a URL issue
   - If it doesn't work in browser, the app isn't running

---

## ✅ Step 3: Check URL Format

### Common Issues:

1. **Case Sensitivity**:
   - ❌ Wrong: `budget-tracker-agent.i222728.repl.co` (all lowercase)
   - ✅ Correct: `Budget-Tracker-Agent.i222728.repl.co` (exact case from Replit)

2. **Missing Protocol**:
   - ❌ Wrong: `Budget-Tracker-Agent.i222728.repl.co/api/health`
   - ✅ Correct: `https://Budget-Tracker-Agent.i222728.repl.co/api/health`

3. **Extra Slashes**:
   - ❌ Wrong: `https://Budget-Tracker-Agent.i222728.repl.co//api/health`
   - ✅ Correct: `https://Budget-Tracker-Agent.i222728.repl.co/api/health`

---

## ✅ Step 4: Test in Browser First

Before testing in Postman, verify the URL works in your browser:

1. Open a new browser tab
2. Go to: `https://your-replit-url.repl.co/api/health`
3. You should see JSON response like:
   ```json
   {
     "status": "healthy",
     "mongodb_connected": true,
     "database": "budget_tracker"
   }
   ```

**If this works in browser but not Postman**, it's a Postman configuration issue.

**If this doesn't work in browser**, your Replit app might be:
- Not running (click Run button)
- Spun down (free tier - wait 30-60 seconds for first request)
- URL is incorrect

---

## ✅ Step 5: Fix Postman Request

1. **Copy the exact URL from Replit** (including https://)
2. **Paste into Postman URL field**
3. **Make sure there are no extra spaces**
4. **Try the request again**

---

## ✅ Step 6: Free Tier Spin-Down Issue

If your Replit is on free tier:

1. **First request after inactivity** can take 30-60 seconds
2. **Wait for the request to complete** - don't cancel it
3. **Use UptimeRobot** to keep it awake (see REPLIT_QUICK_START.md)

---

## 🔍 Quick Diagnostic Steps

### Test 1: Browser Test
```
Open: https://your-replit-url.repl.co/api/health
```
- ✅ Works = URL is correct, app is running
- ❌ Doesn't work = Check Replit app status

### Test 2: Root Endpoint
```
Open: https://your-replit-url.repl.co/
```
- Should show: `{"message": "Budget Tracker Agent API", ...}`

### Test 3: Interactive Docs
```
Open: https://your-replit-url.repl.co/docs
```
- Should show Swagger UI with all endpoints

---

## 🎯 Correct URL Format Examples

Based on your Replit username (`i222728`), your URL should be one of these:

```
https://Budget-Tracker-Agent.i222728.repl.co
https://budget-tracker-agent.i222728.repl.co
https://Budget-Tracker-Agent--i222728.repl.co
```

**Use the exact URL shown in your Replit dashboard!**

---

## 💡 Pro Tip: Use Replit's Webview

1. In Replit, click the **"Open in new tab"** icon (next to Preview/Console tabs)
2. This opens your app in a new browser tab
3. **Copy the URL from the browser address bar**
4. Use that exact URL in Postman

---

## 🚨 Still Not Working?

1. **Check Replit Console** for error messages
2. **Verify secrets are set** (GEMINI_API_KEY, MONGODB_URI)
3. **Restart the Repl** (Stop → Run)
4. **Check Replit status** - is the service running?
5. **Try a different endpoint** - maybe start with just `/` (root)

---

## ✅ Success Checklist

- [ ] App is running in Replit (green ▶️ button)
- [ ] URL works in browser
- [ ] Using exact URL from Replit (case-sensitive)
- [ ] URL includes `https://`
- [ ] No extra spaces or characters
- [ ] Waiting for response (free tier can be slow)

---

Once you get the correct URL working in your browser, use that exact same URL in Postman!


