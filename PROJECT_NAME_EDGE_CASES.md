# 🔍 Project Name Detection - Edge Cases & Test Queries

This document covers all edge cases for project name detection and matching.

## 🎯 Problem Statement

The system must correctly identify which project a user is referring to, even when:
- Project names are mentioned in various formats
- Partial project names are used
- Project names have variations (e.g., "Mobile App" vs "Mobile App Development")
- Multiple projects exist with similar names

## 📋 Edge Case Categories

### 1. Query Phrasing Variations

#### Pattern: "for [Project Name]"
```json
POST /api/query
{"query": "Check budget for Mobile App"}
{"query": "Check budget for our Mobile App"}
{"query": "Check budget for the Mobile App"}
{"query": "How much remaining for Mobile App?"}
```

#### Pattern: "in [Project Name]"
```json
POST /api/query
{"query": "Check budget in Mobile App"}
{"query": "How is spending in Mobile App?"}
```

#### Pattern: "[Project Name] project"
```json
POST /api/query
{"query": "Mobile App project budget"}
{"query": "Check Mobile App project"}
```

#### Pattern: "project [Project Name]"
```json
POST /api/query
{"query": "Check project Mobile App"}
{"query": "Budget for project Mobile App"}
```

#### Pattern: "our project [Project Name]"
```json
POST /api/query
{"query": "Is our budget overrunning for our project Mobile App?"}
{"query": "Check our project Mobile App budget"}
```

#### Pattern: "the [Project Name]"
```json
POST /api/query
{"query": "Check the Mobile App budget"}
{"query": "How is the Mobile App doing?"}
```

### 2. Partial vs Full Names

#### Scenario: User says "Mobile App" but project is "Mobile App Development"
```json
# Project exists: "Mobile App Development"
POST /api/query
{"query": "Check budget for Mobile App"}
# Expected: Should match "Mobile App Development" (partial match)
```

#### Scenario: User says "Website" but project is "Website Redesign"
```json
# Project exists: "Website Redesign"
POST /api/query
{"query": "How much spent on Website?"}
# Expected: Should match "Website Redesign" (partial match)
```

#### Scenario: User says full name but project is shorter
```json
# Project exists: "Mobile App"
POST /api/query
{"query": "Check Mobile App Development budget"}
# Expected: Should match "Mobile App" (partial match)
```

### 3. Case Sensitivity

```json
POST /api/query
{"query": "Check budget for mobile app"}
{"query": "Check budget for MOBILE APP"}
{"query": "Check budget for Mobile App"}
{"query": "Check budget for mObIlE aPp"}
# All should match "Mobile App" project
```

### 4. Suffix Variations

#### "Project" suffix
```json
POST /api/query
{"query": "Check Mobile App Project"}
# Should match "Mobile App"
```

#### "Development" suffix
```json
POST /api/query
{"query": "Check Mobile App Development"}
# Should match "Mobile App" (if exists) or "Mobile App Development"
```

### 5. Multiple Projects with Similar Names

#### Scenario: Both "Mobile App" and "Mobile App Development" exist
```json
# Both projects exist
POST /api/query
{"query": "Check Mobile App"}
# Expected: Should match "Mobile App" (exact match preferred)

POST /api/query
{"query": "Check Mobile App Development"}
# Expected: Should match "Mobile App Development" (exact match)
```

### 6. No Project Mentioned

```json
POST /api/query
{"query": "Check my budget"}
{"query": "How much remaining?"}
# Expected: Should use current active project
```

### 7. Ambiguous Queries

```json
POST /api/query
{"query": "Check budget"}
# Expected: Use current project or ask for clarification

POST /api/query
{"query": "Mobile App"}
# Expected: Extract "Mobile App" as project name
```

### 8. Special Characters & Numbers

```json
POST /api/query
{"query": "Check Project-2024 budget"}
{"query": "Budget for Project #1"}
{"query": "Check Project_Alpha"}
```

### 9. Multilingual Mix

```json
POST /api/query
{"query": "Mobile App ka budget check karo"}
# Expected: Should extract "Mobile App"
```

### 10. Questions About Projects

```json
POST /api/query
{"query": "Is our budget overrunning for our project Mobile App?"}
{"query": "Will Mobile App exceed budget?"}
{"query": "How is Mobile App doing?"}
```

## 🧪 Comprehensive Test Suite

### Test 1: Basic Project Name Extraction
```bash
# Test various phrasings
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check budget for Mobile App"}'

curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Is our budget overrunning for our project Mobile App?"}'

curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check the Mobile App budget"}'
```

### Test 2: Partial Matching
```bash
# Create project: "Mobile App Development"
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Mobile App Development", "budget_limit": 100000}'

# Query with partial name
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check budget for Mobile App"}'
# Expected: Should match "Mobile App Development"
```

### Test 3: Case Insensitivity
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check budget for mobile app"}'

curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check budget for MOBILE APP"}'
```

### Test 4: Suffix Handling
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check Mobile App Project budget"}'

curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check Mobile App Development budget"}'
```

### Test 5: Multiple Similar Projects
```bash
# Create both projects
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Mobile App", "budget_limit": 50000}'

curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Mobile App Development", "budget_limit": 100000}'

# Test exact match preference
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Check Mobile App budget"}'
# Expected: Should match "Mobile App" (exact match)
```

## 🔧 Implementation Details

### Matching Priority Order:
1. **Exact match** (case-insensitive) - Highest priority
2. **Normalized exact match** (after removing suffixes) - High priority
3. **Partial match** (one name contains the other) - Medium priority
4. **Create new project** (if not found) - Low priority
5. **Use current project** (if no project mentioned) - Fallback

### Normalization Rules:
- Convert to lowercase
- Remove trailing: " project", "project", " proj", "proj", " development", "development"
- Trim whitespace

### Partial Matching Logic:
- If search name is contained in DB name → Match
- If DB name is contained in search name → Match
- Longer match length = better score

## ✅ Expected Behavior

### When Project Name is Mentioned:
1. Extract project name from query
2. Try to find exact match
3. Try flexible/partial match
4. If found → Use that project
5. If not found → Create new project with that name
6. **NEVER** fall back to current project if name was mentioned

### When No Project Name is Mentioned:
1. Use current active project
2. If no current project → Create "Default Project"
3. Use that project

## 🐛 Common Issues & Fixes

### Issue 1: Wrong Project Selected
**Symptom**: Query mentions "Mobile App" but uses "Pretty Salon"
**Cause**: Fallback to current project when project name extraction fails
**Fix**: Improved project name extraction in QueryParser + better fallback logic

### Issue 2: Partial Match Not Working
**Symptom**: "Mobile App" doesn't match "Mobile App Development"
**Cause**: Only exact matching was implemented
**Fix**: Added partial matching with scoring

### Issue 3: Case Sensitivity
**Symptom**: "mobile app" doesn't match "Mobile App"
**Cause**: Case-sensitive comparison
**Fix**: All comparisons are now case-insensitive

## 📝 Testing Checklist

- [ ] Basic project name extraction works
- [ ] Partial matching works (e.g., "Mobile App" → "Mobile App Development")
- [ ] Case-insensitive matching works
- [ ] Suffix removal works ("Mobile App Project" → "Mobile App")
- [ ] Exact match preferred over partial match
- [ ] No fallback to wrong project when name is mentioned
- [ ] New project created if name mentioned but not found
- [ ] Current project used when no name mentioned
- [ ] Multiple similar projects handled correctly

