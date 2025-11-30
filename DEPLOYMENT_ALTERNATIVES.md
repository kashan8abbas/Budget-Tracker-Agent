# 🚀 Free Deployment Alternatives (No Credit Card Required)

Since Render requires a credit card even for free tier, here are alternative platforms that offer free hosting without requiring card details:

## Option 1: PythonAnywhere (Recommended - No Card Required) ⭐

**Best for**: Simple deployments, no credit card needed

### Setup Steps:

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com) (free account)
2. **Upload your code**:
   - Go to "Files" tab
   - Upload your project files (or use Git)
3. **Install dependencies**:
   - Open "Consoles" → "Bash"
   - Run: `pip3.10 install --user -r requirements.txt`
4. **Create Web App**:
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Manual configuration" → "Python 3.10"
   - Set source code path to your project directory
5. **Configure WSGI file**:
   - Edit the WSGI file to point to your app:
   ```python
   import sys
   path = '/home/yourusername/path/to/your/app'
   if path not in sys.path:
       sys.path.append(path)
   
   from app import app
   application = app
   ```
6. **Set Environment Variables**:
   - In "Web" tab → "Environment variables"
   - Add: `GEMINI_API_KEY`, `MONGODB_URI`, `MONGO_DB_NAME`
7. **Reload** your web app

**Limitations**: 
- Free tier: 1 web app, limited CPU time
- Custom domain requires paid plan
- URL: `yourusername.pythonanywhere.com`

---

## Option 2: Replit (No Card Required) ⭐

**Best for**: Quick deployment, built-in IDE

### Setup Steps:

1. **Sign up** at [replit.com](https://replit.com) (free)
2. **Create new Repl**:
   - Click "Create Repl"
   - Choose "Python" template
   - Name it "budget-tracker-agent"
3. **Import your code**:
   - Upload files or connect GitHub repository
4. **Install dependencies**:
   - Replit auto-detects `requirements.txt` and installs
   - Or run: `pip install -r requirements.txt` in Shell
5. **Configure Secrets** (Environment Variables):
   - Click "Secrets" tab (lock icon)
   - Add: `GEMINI_API_KEY`, `MONGODB_URI`, `MONGO_DB_NAME`
6. **Create `.replit` file** (if not auto-generated):
   ```toml
   run = "uvicorn app:app --host 0.0.0.0 --port 8000"
   ```
7. **Run**: Click "Run" button

**Limitations**:
- Free tier: Limited resources, may sleep after inactivity
- URL: `your-repl-name.your-username.repl.co`

---

## Option 3: Fly.io (Free Tier Available)

**Best for**: More control, Docker-based

### Setup Steps:

1. **Install Fly CLI**: 
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Sign up**: `fly auth signup` (free tier available)

3. **Create `Dockerfile`** (see below)

4. **Deploy**:
   ```bash
   fly launch
   fly secrets set GEMINI_API_KEY=your-key
   fly secrets set MONGODB_URI=your-uri
   fly deploy
   ```

**Note**: Fly.io may require card for verification, but free tier is generous.

---

## Option 4: Railway (Check Current Policy)

**Best for**: Similar to Render, easy deployment

1. Sign up at [railway.app](https://railway.app)
2. Connect GitHub repository
3. Railway auto-detects Python and deploys
4. Add environment variables in dashboard

**Note**: Railway's policy on credit cards may vary. Check their current terms.

---

## Option 5: Cyclic.sh (Serverless - No Card)

**Best for**: Serverless deployment

### Setup:

1. Sign up at [cyclic.sh](https://cyclic.sh)
2. Connect GitHub repository
3. Cyclic auto-deploys FastAPI apps
4. Add environment variables in dashboard

**Limitations**: Serverless functions, may have cold starts

---

## Quick Comparison

| Platform | Card Required? | Free Tier | Ease of Use | Best For |
|----------|---------------|-----------|-------------|----------|
| **PythonAnywhere** | ❌ No | ✅ Yes | ⭐⭐⭐⭐ | Simple apps |
| **Replit** | ❌ No | ✅ Yes | ⭐⭐⭐⭐⭐ | Quick setup |
| **Fly.io** | ⚠️ Maybe | ✅ Yes | ⭐⭐⭐ | Docker apps |
| **Railway** | ⚠️ Maybe | ✅ Yes | ⭐⭐⭐⭐ | Similar to Render |
| **Cyclic** | ❌ No | ✅ Yes | ⭐⭐⭐⭐ | Serverless |
| **Render** | ✅ Yes | ✅ Yes | ⭐⭐⭐⭐ | Production-ready |

---

## Recommended: PythonAnywhere Setup

I'll create a detailed guide for PythonAnywhere since it's the most reliable free option without card requirements.

See `PYTHONANYWHERE_DEPLOYMENT.md` for step-by-step instructions.

---

## About Render's Card Requirement

**Why Render asks for a card:**
- Prevents abuse of free tier
- Allows automatic upgrade if you exceed limits
- They **don't charge** for free tier services
- Card is only charged if you manually upgrade to paid plan

**If you're comfortable with this**, Render is still a great option. The card requirement is just for verification.

---

## Need Help?

- PythonAnywhere Docs: https://help.pythonanywhere.com
- Replit Docs: https://docs.replit.com
- Fly.io Docs: https://fly.io/docs

