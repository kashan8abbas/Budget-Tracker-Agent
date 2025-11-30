# ⚡ Quick Start - Natural Language Budget Tracker

## 🎯 What You Can Do Now

You can now ask the Budget Tracker Agent questions in **natural language**!

## 🚀 Setup (One Time)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Your OpenAI API Key

**Option 1: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-key-here

# Linux/Mac
export OPENAI_API_KEY="sk-your-key-here"
```

**Option 2: Command Line**
```bash
python main.py --query "your query" --api-key "sk-your-key-here"
```

**Option 3: .env File**
Create `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```

## 💬 Usage Examples

### Example 1: Simple Budget Check
```bash
python main.py --query "Check my budget: I have 50000 limit and spent 42000"
```

### Example 2: With History
```bash
python main.py --query "Analyze my budget: limit 100000, spent 30000, my spending history is 5000, 6000, 7000, 5000, 25000, 6000"
```

### Example 3: Natural Language
```bash
python main.py --query "I have a budget of fifty thousand dollars and I've spent forty-two thousand"
```

### Example 4: Different Phrasings
```bash
python main.py --query "My budget limit is 50k, I spent 42k so far"
```

## 📊 What Happens

1. **You type a query** in natural language
2. **OpenAI extracts** the parameters (budget_limit, spent, history)
3. **Agent checks LTM** for cached results
4. **If cached**: Returns instantly ⚡
5. **If not cached**: Calculates → Stores → Returns
6. **You get** a complete budget analysis!

## 🔄 LTM Caching

The agent **remembers** previous analyses:
- First time: Calculates and stores
- Second time (same numbers): Returns cached result instantly!

## 📝 Still Works with JSON

You can still use JSON files (no OpenAI needed):
```bash
python main.py --input sample_input.json
```

## ❓ Need Help?

See `SETUP_GUIDE.md` for detailed troubleshooting.

