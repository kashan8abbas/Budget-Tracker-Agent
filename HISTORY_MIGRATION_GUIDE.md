# 🔄 History Format Migration Guide

## Issue
Your MongoDB database still has history in the old format (array of numbers):
```json
{
  "history": [50, 500]
}
```

But the system now expects the new format (array of objects):
```json
{
  "history": [
    {
      "amount": 50,
      "description": null,
      "date": "2024-01-15T10:30:00Z",
      "category": null
    },
    {
      "amount": 500,
      "description": null,
      "date": "2024-01-15T10:30:00Z",
      "category": null
    }
  ]
}
```

## Solution

### Option 1: Run Migration Script (Recommended)
Run the migration script to convert all existing data:

```bash
python migrate_history_format.py
```

**Requirements:**
- MongoDB URI must be set in `.env` file as `MONGO_URI` or `MONGODB_URI`
- Or in `config/agent_config.json` as `mongo_uri`

**What it does:**
- Reads all projects from MongoDB
- Converts history from `[50, 500]` to structured objects
- Saves back to MongoDB
- Preserves all data, just changes format

### Option 2: Automatic Migration (On Next Update)
The system will automatically convert old format to new format when:
- You make any update to a project (add spending, update budget, etc.)
- The system reads the old format, normalizes it, and saves it back in new format

**To trigger:**
```bash
# Just make any update to your project
POST /api/query
{
  "query": "I spent 100 on Website Redesign"
}
```

This will:
1. Read old format: `[50, 500]`
2. Normalize to new format: `[{amount: 50, ...}, {amount: 500, ...}]`
3. Add new entry: `[{amount: 50, ...}, {amount: 500, ...}, {amount: 100, description: null, ...}]`
4. Save back in new format

## Verification

After migration, check your MongoDB:

**Before:**
```json
{
  "history": [50, 500]
}
```

**After:**
```json
{
  "history": [
    {
      "amount": 50,
      "description": null,
      "date": "2024-01-15T10:30:00Z",
      "category": null
    },
    {
      "amount": 500,
      "description": null,
      "date": "2024-01-15T10:30:00Z",
      "category": null
    }
  ]
}
```

## What's Fixed

✅ **Reading**: All reads normalize old format to new format
✅ **Writing**: All writes save in new format
✅ **Backward Compatibility**: Old format automatically converted
✅ **New Entries**: Always saved with description support

## Next Steps

1. **Run migration script** (if you want to convert all data now)
2. **Or** just use the system - it will convert automatically on next update
3. **Test** with a query that includes description:
   ```bash
   POST /api/query
   {
     "query": "I spent 1000 on buying services for Website Redesign"
   }
   ```

The new entry will have:
```json
{
  "amount": 1000,
  "description": "buying services",
  "date": "2024-01-15T10:30:00Z",
  "category": null
}
```


