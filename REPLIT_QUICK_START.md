# ⚡ Replit Quick Start Guide

Follow these steps to deploy your Budget Tracker Agent to Replit in under 5 minutes!

## Step 1: Create Repl from GitHub

1. Go to [replit.com](https://replit.com) and sign in
2. Click **"Create Repl"** → **"Import from GitHub"**
3. Paste your repository URL: `https://github.com/yourusername/Budget-Tracker-Agent`
4. Click **"Import"**

## Step 2: Set Secrets (Environment Variables)

1. Click the **🔒 Secrets** tab in the left sidebar
2. Add these secrets:

   ```
   GEMINI_API_KEY = your-gemini-api-key-here
   MONGODB_URI = your-mongodb-connection-string
   MONGO_DB_NAME = budget_tracker
   ```

3. Click **"Add secret"** for each one

## Step 3: Run Your App

1. Click the green **▶️ Run** button
2. Wait for dependencies to install (first time only)
3. Your app will start automatically!

## Step 4: Get Your Public URL

Once running, Replit will show:
- **Webview**: Click to open in a new tab
- **Public URL**: `https://your-repl-name.your-username.repl.co`

## Step 5: Test Your API

Open these URLs in your browser:

- **Root**: `https://your-repl-name.your-username.repl.co/`
- **Health Check**: `https://your-repl-name.your-username.repl.co/api/health`
- **API Docs**: `https://your-repl-name.your-username.repl.co/docs`

## ⚠️ Keep Your Repl Awake (Free Tier)

Free Repls sleep after ~5 minutes of inactivity. To keep it awake:

1. Sign up at [UptimeRobot.com](https://uptimerobot.com) (free)
2. Add a monitor:
   - **Type**: HTTP(s)
   - **URL**: `https://your-repl-name.your-username.repl.co/api/health`
   - **Interval**: 5 minutes
3. This will ping your app every 5 minutes

## ✅ That's It!

Your API is now live! For detailed troubleshooting, see `REPLIT_DEPLOYMENT.md`.

## Common Issues

**App won't start?**
- Check the Shell tab for errors
- Make sure all secrets are set
- Verify `requirements.txt` is correct

**Module not found?**
- Run `pip install -r requirements.txt` in Shell

**Slow first request?**
- Normal for free tier after sleep
- Use UptimeRobot to keep it awake

---

Need help? Check `REPLIT_DEPLOYMENT.md` for detailed instructions! 🚀

