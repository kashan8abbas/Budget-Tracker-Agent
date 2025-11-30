# ✅ Replit Deployment Checklist

Use this checklist to ensure everything is ready for Replit deployment.

## Pre-Deployment Checklist

- [ ] **Code is ready**
  - [ ] `app.py` exists and is configured
  - [ ] `requirements.txt` is up to date
  - [ ] `.replit` file is present (already created ✅)
  - [ ] All necessary files are in the repository

- [ ] **API Keys ready**
  - [ ] Google Gemini API key obtained
  - [ ] MongoDB connection string ready
  - [ ] Keys are NOT committed to repository (using .gitignore ✅)

- [ ] **Repository is pushed to GitHub**
  - [ ] Code is committed
  - [ ] Pushed to GitHub
  - [ ] Repository is public or you have access

## Deployment Steps

- [ ] **Create Repl**
  - [ ] Signed up at replit.com
  - [ ] Created new Repl from GitHub
  - [ ] Repl is created successfully

- [ ] **Set Environment Variables (Secrets)**
  - [ ] `GEMINI_API_KEY` added
  - [ ] `MONGODB_URI` added
  - [ ] `MONGO_DB_NAME` added (optional, defaults to `budget_tracker`)

- [ ] **Install Dependencies**
  - [ ] Dependencies installed (auto or manual)
  - [ ] No import errors in Shell

- [ ] **Run Application**
  - [ ] Clicked Run button
  - [ ] App starts without errors
  - [ ] Public URL is available

## Testing Checklist

- [ ] **Test Endpoints**
  - [ ] Root endpoint (`/`) works
  - [ ] Health endpoint (`/api/health`) works
  - [ ] API docs (`/docs`) accessible
  - [ ] Query endpoint (`/api/query`) works with test query

- [ ] **Verify Functionality**
  - [ ] Can connect to MongoDB
  - [ ] Gemini API calls work
  - [ ] Responses are correct

## Post-Deployment

- [ ] **Keep Repl Awake (Free Tier)**
  - [ ] Set up UptimeRobot monitor
  - [ ] Configure 5-minute ping interval
  - [ ] Monitor is active

- [ ] **Documentation**
  - [ ] Save your Repl URL
  - [ ] Note any custom configurations
  - [ ] Share URL with team/users

## Troubleshooting

If something doesn't work:

1. **Check Shell tab** for error messages
2. **Verify secrets** are set correctly
3. **Check requirements.txt** - all dependencies listed?
4. **Review logs** in Replit console
5. **See REPLIT_DEPLOYMENT.md** for detailed troubleshooting

---

**Quick Start**: Follow `REPLIT_QUICK_START.md` for fastest deployment! 🚀

