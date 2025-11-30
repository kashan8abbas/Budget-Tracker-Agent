# 📝 History Enhancement - Structured Spending Records

## Overview

The history system has been enhanced to store structured objects instead of just numbers. Each history entry now contains detailed information about each spending transaction.

## New History Structure

### Old Format (Backward Compatible)
```json
{
  "history": [5000, 6000, 7000]
}
```

### New Format
```json
{
  "history": [
    {
      "amount": 5000,
      "description": "buying services",
      "date": "2024-01-15T10:30:00Z",
      "category": null
    },
    {
      "amount": 6000,
      "description": "software licenses",
      "date": "2024-01-16T14:20:00Z",
      "category": null
    },
    {
      "amount": 7000,
      "description": null,
      "date": "2024-01-17T09:15:00Z",
      "category": null
    }
  ]
}
```

## History Object Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | float | ✅ Yes | The amount spent |
| `description` | string/null | ❌ No | What the money was spent on (extracted from query) |
| `date` | string (ISO) | ✅ Yes | When the spending occurred (auto-generated) |
| `category` | string/null | ❌ No | Category for future use (currently null) |

## How It Works

### 1. Query Parsing
The QueryParser (Gemini) extracts spending descriptions from natural language queries:

**Examples:**
- `"spent 50 on buying services"` → `spending_description: "buying services"`
- `"spent 5000 on software licenses for Mobile App"` → `spending_description: "software licenses"`
- `"I spent 3000 today on marketing"` → `spending_description: "marketing"`
- `"Add 2000 for office supplies"` → `spending_description: "office supplies"`
- `"Spent 1000"` → `spending_description: null` (no description mentioned)

### 2. History Storage
When spending is added:
- Amount is extracted from the query
- Description is extracted (if mentioned)
- Date is automatically set to current timestamp
- Category is set to null (for future use)

### 3. Backward Compatibility
The system automatically converts old format (array of numbers) to new format (array of objects):
- Old entries: `5000` → `{"amount": 5000, "description": null, "date": "...", "category": null}`
- New entries: Already in object format

## Usage Examples

### Example 1: With Description
```bash
POST /api/query
{
  "query": "I spent 5000 on buying services for Mobile App project"
}
```

**Result:**
```json
{
  "history": [
    {
      "amount": 5000,
      "description": "buying services",
      "date": "2024-01-15T10:30:00Z",
      "category": null
    }
  ]
}
```

### Example 2: Without Description
```bash
POST /api/query
{
  "query": "I spent 3000 today"
}
```

**Result:**
```json
{
  "history": [
    {
      "amount": 3000,
      "description": null,
      "date": "2024-01-15T10:30:00Z",
      "category": null
    }
  ]
}
```

### Example 3: Multiple Entries
```bash
POST /api/query
{
  "query": "I spent 5000 on services"
}
POST /api/query
{
  "query": "Add 3000 for marketing"
}
```

**Result:**
```json
{
  "history": [
    {
      "amount": 5000,
      "description": "services",
      "date": "2024-01-15T10:30:00Z",
      "category": null
    },
    {
      "amount": 3000,
      "description": "marketing",
      "date": "2024-01-15T11:00:00Z",
      "category": null
    }
  ]
}
```

## Query Patterns Supported

The system recognizes these patterns for extracting descriptions:

1. **"spent X on [description]"**
   - `"spent 50 on buying services"` → description: "buying services"

2. **"spent X for [description]"**
   - `"spent 5000 for software licenses"` → description: "software licenses"

3. **"spent X on buying [description]"**
   - `"spent 1000 on buying equipment"` → description: "equipment"

4. **"Add X for [description]"**
   - `"Add 2000 for office supplies"` → description: "office supplies"

5. **"Spent X today on [description]"**
   - `"I spent 3000 today on marketing"` → description: "marketing"

6. **No description**
   - `"Spent 1000"` → description: null

## Benefits

1. **Better Tracking**: Know what each spending was for
2. **Analysis**: Can analyze spending by description/category
3. **Reporting**: Generate reports with spending details
4. **Audit Trail**: Complete record of all transactions
5. **Future Features**: Can add filtering, categorization, etc.

## Implementation Details

### Helper Functions

1. **`_normalize_history(history)`**: Converts old format to new format
2. **`_extract_amounts_from_history(history)`**: Extracts amounts for calculations

### Automatic Conversion

- When reading from database/file: Old format automatically converted
- When writing: Always stored in new format
- Calculations: Extract amounts from objects automatically

## API Response

History is returned in the new format:

```json
{
  "success": true,
  "project_id": "...",
  "project_name": "Mobile App",
  "remaining": 42000,
  "history": [
    {
      "amount": 5000,
      "description": "buying services",
      "date": "2024-01-15T10:30:00Z",
      "category": null
    }
  ]
}
```

## Migration

- **Automatic**: Old data is automatically converted when read
- **No Data Loss**: All existing history entries preserved
- **Seamless**: Works with both old and new formats

## Future Enhancements

Possible additions:
- `category`: Spending category (e.g., "marketing", "development", "operations")
- `tags`: Multiple tags for better organization
- `receipt_url`: Link to receipt/document
- `approved_by`: Who approved the spending
- `notes`: Additional notes

