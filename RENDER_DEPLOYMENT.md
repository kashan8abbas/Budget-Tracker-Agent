# 🚀 Render Deployment Guide

This guide will help you deploy the Budget Tracker Agent API to Render's free tier.

## Prerequisites

1. A [Render account](https://render.com) (free tier available)
2. A GitHub repository with your code (or use Render's Git integration)
3. Google Gemini API key
4. MongoDB connection string (MongoDB Atlas free tier recommended)

## Step 1: Prepare Your Repository

Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository containing this project

## Step 3: Configure the Service

### Basic Settings

- **Name**: `budget-tracker-agent` (or your preferred name)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or specify if your app is in a subdirectory)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### Environment Variables

Add the following environment variables in the Render dashboard:

#### Required Variables:

1. **GEMINI_API_KEY**
   - Your Google Gemini API key
   - Get it from: https://makersuite.google.com/app/apikey

2. **MONGODB_URI** (or **MONGO_URI**)
   - Your MongoDB connection string
   - Example: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
   - For MongoDB Atlas: Create a free cluster at https://www.mongodb.com/cloud/atlas

#### Optional Variables:

3. **MONGO_DB_NAME**
   - Database name (defaults to `budget_tracker` if not set)
   - Example: `Budget_Tracker_Agent`

4. **PYTHON_VERSION** (optional)
   - Set to `3.11.0` or your preferred Python version

### How to Add Environment Variables:

1. In your Render service dashboard, go to **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Enter the key and value
4. Click **"Save Changes"**

## Step 4: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start your application
3. Wait for the build to complete (usually 2-5 minutes)

## Step 5: Verify Deployment

Once deployed, you'll get a URL like: `https://budget-tracker-agent.onrender.com`

Test your deployment:

1. **Health Check**: 
   ```
   https://your-app-name.onrender.com/api/health
   ```

2. **API Docs**: 
   ```
   https://your-app-name.onrender.com/docs
   ```

3. **Root Endpoint**: 
   ```
   https://your-app-name.onrender.com/
   ```

## Alternative: Using render.yaml

If you prefer configuration as code:

1. The `render.yaml` file is already in your repository
2. In Render dashboard, select **"Apply Render Blueprint"**
3. Connect your repository
4. Render will read `render.yaml` and create the service automatically
5. You'll still need to add environment variables manually in the dashboard

## Free Tier Limitations

⚠️ **Important Notes about Render Free Tier:**

1. **Spinning Down**: Free tier services spin down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - Consider upgrading to paid tier for production use

2. **Build Time**: Free tier has limited build minutes per month

3. **Bandwidth**: Limited bandwidth on free tier

4. **Sleep Time**: Services may sleep after periods of inactivity

## Troubleshooting

### Build Fails

- Check that `requirements.txt` is correct
- Verify Python version compatibility
- Check build logs in Render dashboard

### Application Crashes

- Check application logs in Render dashboard
- Verify all environment variables are set correctly
- Ensure MongoDB connection string is valid

### Slow Response Times

- First request after spin-down will be slow (free tier limitation)
- Consider using a health check service to keep it awake (e.g., UptimeRobot)

### Environment Variables Not Working

- Make sure variable names match exactly (case-sensitive)
- Restart the service after adding new variables
- Check that variables are marked as "Secret" if needed

## Keeping Your Service Awake (Free Tier)

To prevent your service from spinning down:

1. Use a service like [UptimeRobot](https://uptimerobot.com) (free)
2. Set up a monitor to ping your health endpoint every 5 minutes:
   ```
   https://your-app-name.onrender.com/api/health
   ```

## Next Steps

- Set up custom domain (paid tier)
- Configure auto-deploy from specific branches
- Set up monitoring and alerts
- Consider upgrading to paid tier for production use

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

---

**Note**: Remember to never commit sensitive information like API keys or MongoDB connection strings to your repository. Always use environment variables!

