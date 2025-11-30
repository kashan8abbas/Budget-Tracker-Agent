# 🔷 Replit Deployment Guide (No Credit Card Required)

This guide will help you deploy your Budget Tracker Agent API to Replit's free tier.

## Prerequisites

1. A [Replit account](https://replit.com) (free, no card required)
2. Google Gemini API key
3. MongoDB connection string
4. Your code in a GitHub repository (optional but recommended)

## Step 1: Create a New Repl

1. Go to [replit.com](https://replit.com) and sign in
2. Click **"Create Repl"** (or the **"+"** button)
3. Choose **"Python"** template
4. Name it: `budget-tracker-agent`
5. Click **"Create Repl"**

## Step 2: Import Your Code

### Option A: Import from GitHub (Recommended)

1. In Replit, click **"Import from GitHub"**
2. Enter your repository URL: `https://github.com/yourusername/your-repo`
3. Click **"Import"**
4. Replit will clone your repository

### Option B: Manual Upload

1. In Replit, click **"Files"** in the sidebar
2. Upload your project files:
   - `app.py`
   - `requirements.txt`
   - `api/` directory
   - `agents/` directory
   - `communication/` directory
   - `config/` directory
   - All other necessary files

## Step 3: Install Dependencies

Replit usually auto-installs from `requirements.txt`, but if not:

1. Open the **"Shell"** tab (bottom panel)
2. Run:
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Configure Secrets (Environment Variables)

1. Click the **"Secrets"** tab (lock icon 🔒) in the left sidebar
2. Add the following secrets:

   - **Key**: `GEMINI_API_KEY`
     **Value**: Your Google Gemini API key
   
   - **Key**: `MONGODB_URI`
     **Value**: Your MongoDB connection string
   
   - **Key**: `MONGO_DB_NAME`
     **Value**: `budget_tracker` (or your preferred name)

3. Click **"Add secret"** for each one

## Step 5: Configure Run Command

### Option A: Using .replit file (Auto-generated)

Replit should auto-detect your FastAPI app, but verify:

1. Check if `.replit` file exists
2. If not, create it with:
   ```toml
   run = "uvicorn app:app --host 0.0.0.0 --port 8000"
   ```

### Option B: Using replit.nix (For custom packages)

If you need specific system packages, create `replit.nix`:
```nix
{ pkgs }: {
  deps = [
    pkgs.python310Full
  ];
}
```

## Step 6: Update app.py for Replit

Replit uses port 8000 by default, but you can make it dynamic:

The `app.py` already uses `PORT` environment variable, which is good. Replit will handle this automatically.

## Step 7: Run Your App

1. Click the green **"Run"** button at the top
2. Wait for the app to start
3. You'll see output in the console
4. Replit will show a webview with your app

## Step 8: Get Your Public URL

1. Once running, Replit provides a public URL
2. Look for: `https://your-repl-name.your-username.repl.co`
3. Or click the webview to open in a new tab

## Step 9: Test Your Deployment

Test these endpoints:

1. **Root**: `https://your-repl-name.your-username.repl.co/`
2. **Health**: `https://your-repl-name.your-username.repl.co/api/health`
3. **Docs**: `https://your-repl-name.your-username.repl.co/docs`

## Step 10: Keep Your Repl Running (Free Tier)

⚠️ **Important**: Free tier Repls sleep after inactivity.

### Option A: Use UptimeRobot (Recommended)

1. Sign up at [UptimeRobot](https://uptimerobot.com) (free)
2. Add a monitor:
   - Type: HTTP(s)
   - URL: `https://your-repl-name.your-username.repl.co/api/health`
   - Interval: 5 minutes
3. This will ping your app every 5 minutes to keep it awake

### Option B: Always On (Paid Feature)

- Replit Hacker plan ($7/month) includes "Always On"
- Prevents your Repl from sleeping

## Troubleshooting

### App Not Starting

- Check the **"Shell"** tab for error messages
- Verify all dependencies are installed
- Check that secrets are set correctly

### Module Not Found

- Run `pip install -r requirements.txt` in Shell
- Make sure `requirements.txt` is in the root directory

### Port Already in Use

- Replit handles ports automatically
- If issues, try changing port in `.replit` file:
  ```toml
  run = "uvicorn app:app --host 0.0.0.0 --port 8080"
  ```

### Environment Variables Not Working

- Make sure secrets are added in **"Secrets"** tab (not `.env` file)
- Restart the Repl after adding secrets
- Check variable names match exactly

### Repl Sleeping

- Free tier Repls sleep after ~5 minutes of inactivity
- Use UptimeRobot to keep it awake (see Step 10)

## Updating Your App

### If using GitHub:

1. Push changes to GitHub
2. In Replit, open **"Shell"**
3. Run:
   ```bash
   git pull
   ```
4. Click **"Run"** again

### If editing in Replit:

1. Make changes directly in Replit editor
2. Click **"Run"** to restart

## Free Tier Limitations

⚠️ **Replit Free Tier:**

- ✅ Unlimited public Repls
- ✅ 500 MB RAM
- ✅ 0.5 CPU cores
- ✅ Repls sleep after inactivity (~5 minutes)
- ✅ Public URL: `your-repl-name.your-username.repl.co`
- ⚠️ First request after sleep may be slow (cold start)

## Tips

1. **Use GitHub**: Makes version control and updates easier
2. **Monitor resources**: Check usage in Replit dashboard
3. **Use UptimeRobot**: Keep your app awake for free
4. **Check logs**: Use Shell tab to see application output
5. **Test locally**: Make sure everything works before deploying

## Upgrading (Optional)

- **Hacker Plan**: $7/month - Always On, more resources
- **Teams**: For collaboration features

## Support

- Replit Docs: https://docs.replit.com
- Replit Community: https://replit.com/talk

---

**Note**: Replit is great for quick deployments and doesn't require a credit card! 🎉

