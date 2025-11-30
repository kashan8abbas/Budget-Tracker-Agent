# 🔧 Gemini Model Fix

## Issue
The error `404 models/gemini-pro is not found` occurred because the model name format was incorrect. The API requires the full model path with `models/` prefix.

## Solution
Changed the model to use the correct format: `models/gemini-2.5-flash`, which:
- ✅ Is available in your API version
- ✅ Supports `generateContent` method
- ✅ Fast and cost-effective
- ✅ Latest stable flash model

## Changes Made

### 1. query_parser.py
- Changed: `genai.GenerativeModel('gemini-pro')` 
- To: `genai.GenerativeModel('models/gemini-2.5-flash')`

### 2. agents/workers/budget_tracker_agent.py
- Changed: `genai.GenerativeModel('gemini-pro')`
- To: `genai.GenerativeModel('models/gemini-2.5-flash')`

## Available Models (From Your API)

Based on your API, these models support `generateContent`:

1. **models/gemini-2.5-flash** (Current - Recommended)
   - Latest flash model
   - Fast and efficient
   - Supports all features we need

2. **models/gemini-2.0-flash**
   - Stable flash model
   - Good alternative

3. **models/gemini-pro-latest**
   - Pro model (more capable)
   - Slower but better quality

4. **models/gemini-flash-latest**
   - Latest flash (auto-updates)
   - Good for staying current

## Testing

After the fix, test with:
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check my budget: 50000 limit, 42000 spent"}'
```

## Notes

- `gemini-pro` is the most reliable choice for production
- JSON mode (`response_mime_type="application/json"`) may not be supported by `gemini-pro` - the code will automatically fallback
- If you need JSON mode, consider using `gemini-1.5-pro` or `gemini-1.5-flash` (if available)

