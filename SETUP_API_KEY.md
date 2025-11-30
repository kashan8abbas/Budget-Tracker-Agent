# Setting Up OpenAI API Key

The `/api/query` endpoint requires an OpenAI API key for natural language processing. Here are three ways to set it up:

## Option 1: Using .env File (Recommended)

1. Create a `.env` file in the project root:
   ```bash
   # Copy the example file
   copy .env.example .env
   ```

2. Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. The `.env` file is automatically loaded by `python-dotenv` (already in requirements.txt)

4. Restart your API server:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## Option 2: Using Environment Variable (Windows PowerShell)

```powershell
# Set for current session
$env:OPENAI_API_KEY = "sk-your-actual-api-key-here"

# Or set permanently (requires restart)
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-actual-api-key-here', 'User')
```

Then restart your API server.

## Option 3: Using Environment Variable (Windows CMD)

```cmd
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

Then restart your API server.

## Option 4: Using Environment Variable (Linux/Mac)

```bash
export OPENAI_API_KEY="sk-your-actual-api-key-here"
```

Or add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export OPENAI_API_KEY="sk-your-actual-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Getting Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)
5. **Important:** Save it immediately - you won't be able to see it again!

## Testing the Setup

After setting up the API key, test it:

```powershell
# Test health endpoint (doesn't need API key)
Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing

# Test query endpoint (needs API key)
$body = @{query="Check my budget: 50000 limit, 42000 spent"} | ConvertTo-Json
Invoke-WebRequest -Uri http://localhost:8000/api/query -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
```

## Note

- The `/api/analyze` endpoint does **NOT** require an OpenAI API key - it works with structured JSON
- Only `/api/query` (natural language) requires the OpenAI API key
- Make sure to restart the server after setting the environment variable

## Security Note

- Never commit your `.env` file to git (it should be in `.gitignore`)
- Don't share your API key publicly
- The `.env.example` file is safe to commit (it doesn't contain real keys)

