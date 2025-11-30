# 🐍 PythonAnywhere Deployment Guide (No Credit Card Required)

This guide will help you deploy your Budget Tracker Agent API to PythonAnywhere's free tier.

## Prerequisites

1. A [PythonAnywhere account](https://www.pythonanywhere.com) (free tier available, no card required)
2. Google Gemini API key
3. MongoDB connection string

## Step 1: Sign Up for PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Create a Beginner account" (free)
3. Verify your email

## Step 2: Upload Your Code

### Option A: Using Git (Recommended)

1. In PythonAnywhere dashboard, open **"Consoles"** → **"Bash"**
2. Clone your repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

### Option B: Manual Upload

1. Go to **"Files"** tab
2. Navigate to `/home/yourusername/`
3. Click **"Upload a file"** and upload your project files
4. Or create a new directory and upload files there

## Step 3: Install Dependencies

1. Open **"Consoles"** → **"Bash"**
2. Navigate to your project directory:
   ```bash
   cd ~/your-project-name
   ```
3. Install dependencies:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```
   
   **Note**: PythonAnywhere uses `pip3.10` for Python 3.10. Adjust if using different version.

## Step 4: Create Web App

1. Go to **"Web"** tab in dashboard
2. Click **"Add a new web app"**
3. Choose domain: Select your free subdomain (e.g., `yourusername.pythonanywhere.com`)
4. Select **"Manual configuration"**
5. Choose **"Python 3.10"** (or latest available)
6. Click **"Next"** → **"Finish"**

## Step 5: Configure WSGI File

1. In **"Web"** tab, click on the WSGI configuration file link
2. Replace the content with:

```python
import sys
import os

# Add your project directory to the path
path = '/home/yourusername/your-project-name'
if path not in sys.path:
    sys.path.insert(0, path)

# Change to your project directory
os.chdir(path)

# Import your FastAPI app
from app import app

# WSGI expects 'application' variable
application = app
```

**Important**: Replace `yourusername` and `your-project-name` with your actual values!

## Step 6: Set Source Code and Working Directory

1. In **"Web"** tab, scroll to **"Code"** section
2. Set **"Source code"**: `/home/yourusername/your-project-name`
3. Set **"Working directory"**: `/home/yourusername/your-project-name`

## Step 7: Configure Environment Variables

1. In **"Web"** tab, scroll to **"Environment variables"** section
2. Add the following variables:

   - **GEMINI_API_KEY**: Your Google Gemini API key
   - **MONGODB_URI**: Your MongoDB connection string
   - **MONGO_DB_NAME**: `budget_tracker` (or your preferred name)

3. Click **"Save"**

## Step 8: Configure Static Files (Optional)

If you have static files, add them in the **"Static files"** section:
- URL: `/static`
- Directory: `/home/yourusername/your-project-name/static`

## Step 9: Reload Web App

1. Click the green **"Reload"** button in the **"Web"** tab
2. Wait for the reload to complete

## Step 10: Test Your Deployment

Your app should be available at: `https://yourusername.pythonanywhere.com`

Test endpoints:

1. **Root**: `https://yourusername.pythonanywhere.com/`
2. **Health**: `https://yourusername.pythonanywhere.com/api/health`
3. **Docs**: `https://yourusername.pythonanywhere.com/docs`

## Troubleshooting

### Error: Module not found

- Make sure you installed dependencies with `pip3.10 install --user`
- Check that the path in WSGI file is correct
- Verify you're using the correct Python version

### Error: Application failed to start

- Check the **"Error log"** in the **"Web"** tab
- Verify environment variables are set correctly
- Make sure `app.py` is in the correct location

### 502 Bad Gateway

- Check the **"Server log"** in the **"Web"** tab
- Verify your WSGI file syntax is correct
- Make sure the `application` variable is defined

### Port Issues

- PythonAnywhere handles ports automatically
- You don't need to specify `--port` in the WSGI file
- The app runs behind a proxy

### Environment Variables Not Working

- Make sure variables are set in **"Web"** → **"Environment variables"**
- Restart the web app after adding variables
- Check variable names match exactly (case-sensitive)

## Free Tier Limitations

⚠️ **PythonAnywhere Free Tier:**

- ✅ 1 web app
- ✅ 512 MB disk space
- ✅ Limited CPU time (100 seconds per day for web apps)
- ✅ Custom domain requires paid plan
- ✅ URL: `yourusername.pythonanywhere.com`
- ⚠️ Web app may be suspended if CPU limit exceeded

## Updating Your App

1. **If using Git**:
   ```bash
   cd ~/your-project-name
   git pull
   ```

2. **If manual upload**:
   - Upload new files via **"Files"** tab
   - Or use SFTP

3. **Reload web app**:
   - Go to **"Web"** tab
   - Click **"Reload"**

## Tips

1. **Use Git**: Makes updates much easier
2. **Monitor CPU usage**: Check **"Tasks"** tab to see CPU time used
3. **Check logs regularly**: **"Web"** → **"Error log"** and **"Server log"**
4. **Test locally first**: Make sure everything works before deploying

## Upgrading (Optional)

If you need more resources:
- **Hacker plan**: $5/month - More CPU time, custom domains
- **Web Developer**: $12/month - Even more resources

## Support

- PythonAnywhere Help: https://help.pythonanywhere.com
- Community Forum: https://www.pythonanywhere.com/forums

---

**Note**: PythonAnywhere is a great free option that doesn't require a credit card! 🎉

