# 🚀 Setup Guide - Budget Tracker Agent with OpenAI

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key

You have three options:

#### Option A: Environment Variable (Recommended)
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Windows CMD
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

#### Option B: .env File
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your-api-key-here
```

#### Option C: Command Line Argument
```bash
python main.py --query "your query" --api-key "your-api-key-here"
```

### 3. Run the Agent

#### Natural Language Query Mode
```bash
python main.py --query "Check my budget: 50000 limit, 42000 spent"
```

#### JSON File Input Mode (No OpenAI needed)
```bash
python main.py --input sample_input.json
```

---

## Usage Examples

### Example 1: Basic Budget Check
```bash
python main.py --query "I have a budget of 50000 and spent 42000"
```

### Example 2: With Spending History
```bash
python main.py --query "Analyze my budget: limit 100000, spent 30000, history is 5000, 6000, 7000, 5000, 25000, 6000"
```

### Example 3: Different Phrasings
```bash
python main.py --query "My budget limit is fifty thousand dollars, I've spent forty-two thousand"
```

### Example 4: Using JSON File (No OpenAI)
```bash
python main.py --input sample_input.json
```

---

## How It Works

1. **User enters natural language query**
2. **OpenAI extracts parameters** (budget_limit, spent, history)
3. **Agent checks LTM** for cached results
4. **If not cached**: Calculates analysis
5. **Stores result in LTM** for future use
6. **Returns formatted response**

---

## Troubleshooting

### Error: "OpenAI API key not found"
- Make sure you've set the API key using one of the methods above
- Check that the key is correct and has credits

### Error: "Failed to parse extracted parameters"
- The OpenAI response might not be valid JSON
- Try rephrasing your query more clearly
- Check your internet connection

### Error: "ModuleNotFoundError: No module named 'openai'"
- Run: `pip install -r requirements.txt`

---

## Notes

- The agent uses **gpt-4o-mini** model (cost-effective)
- Results are cached in LTM for faster repeated queries
- You can use either natural language or JSON file input
- LTM storage: `LTM/BudgetTrackerAgent/memory.json`

