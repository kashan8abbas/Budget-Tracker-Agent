# 🧪 Comprehensive Test Queries for Budget Tracker API

This document provides test queries to verify all functionality of the Budget Tracker system.

## 📋 Table of Contents
1. [Project Management Tests](#project-management-tests)
2. [Basic Budget Operations](#basic-budget-operations)
3. [Spending Updates](#spending-updates)
4. [History Tracking](#history-tracking)
5. [Project-Specific Queries](#project-specific-queries)
6. [Natural Language Variations](#natural-language-variations)
7. [Edge Cases](#edge-cases)
8. [Analysis & Predictions](#analysis--predictions)

---

## 1. Project Management Tests

### Create Projects
```bash
# Test 1.1: Create a new project
POST /api/projects
{
  "project_name": "Website Redesign",
  "budget_limit": 50000,
  "description": "Complete website overhaul project"
}

# Test 1.2: Create another project
POST /api/projects
{
  "project_name": "Mobile App Development",
  "budget_limit": 100000,
  "description": "iOS and Android app development"
}

# Test 1.3: Create project with minimal data
POST /api/projects
{
  "project_name": "Marketing Campaign"
}
```

### List Projects
```bash
# Test 1.4: Get all projects
GET /api/projects

# Test 1.5: Get specific project
GET /api/projects/{project_id}
```

### Update Projects
```bash
# Test 1.6: Update project budget
PUT /api/projects/{project_id}
{
  "budget_limit": 75000,
  "description": "Updated description"
}
```

### Set Current Project
```bash
# Test 1.7: Set active project
POST /api/projects/{project_id}/set-current
```

### Delete Projects
```bash
# Test 1.8: Delete a project
DELETE /api/projects/{project_id}
```

---

## 2. Basic Budget Operations

### Check Budget Status
```bash
# Test 2.1: Simple budget check
POST /api/query
{
  "query": "Check my budget: 50000 limit, 42000 spent"
}

# Test 2.2: Budget check with project name
POST /api/query
{
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent"
}

# Test 2.3: Natural language budget check
POST /api/query
{
  "query": "I have a budget of fifty thousand dollars and I've spent forty-two thousand"
}

# Test 2.4: Budget check with project ID
POST /api/query
{
  "query": "Check my budget",
  "project_id": "{project_id}"
}
```

### Get Current Budget
```bash
# Test 2.5: Get current budget (uses active project)
GET /api/budget

# Test 2.6: Get budget for specific project
GET /api/projects/{project_id}/budget
```

---

## 3. Spending Updates

### Add New Spending
```bash
# Test 3.1: Add spending (update type)
POST /api/query
{
  "query": "I spent 5000 today on Website Redesign project"
}

# Test 3.2: Add spending with natural language
POST /api/query
{
  "query": "Add 3000 to my expenses for Mobile App"
}

# Test 3.3: Add spending via update endpoint
POST /api/update
{
  "update_type": "add",
  "update_field": "spent",
  "update_value": 5000,
  "project_id": "{project_id}"
}
```

### Set Spending Directly
```bash
# Test 3.4: Set total spent amount
POST /api/query
{
  "query": "My total spending is now 45000 for Website Redesign"
}

# Test 3.5: Set spending via update
POST /api/update
{
  "update_type": "set",
  "update_field": "spent",
  "update_value": 45000,
  "project_id": "{project_id}"
}
```

### Update Budget Limit
```bash
# Test 3.6: Update budget limit
POST /api/query
{
  "query": "Update my budget limit to 75000 for Website Redesign"
}

# Test 3.7: Update budget limit via API
POST /api/update
{
  "update_type": "replace",
  "update_field": "budget_limit",
  "update_value": 75000,
  "project_id": "{project_id}"
}
```

---

## 4. History Tracking

### Initial Spending in History
```bash
# Test 4.1: Set budget with initial spent (should add to history)
POST /api/query
{
  "query": "Check my budget: 50000 limit, 7000 spent"
}
# Expected: 7000 should appear in history

# Test 4.2: Set budget with higher spent (should track difference)
POST /api/query
{
  "query": "My budget is 50000 and I've spent 15000"
}
# Expected: 8000 (15000 - 7000) should be added to history
```

### Add to History
```bash
# Test 4.3: Add spending (should add to history)
POST /api/query
{
  "query": "I spent 2000 today"
}
# Expected: 2000 should be added to history

# Test 4.4: Multiple spending additions
POST /api/query
{
  "query": "Add 3000 to expenses"
}
POST /api/query
{
  "query": "Add 1500 more"
}
# Expected: History should contain [7000, 8000, 2000, 3000, 1500]
```

### Check History
```bash
# Test 4.5: Analyze with history
POST /api/query
{
  "query": "Analyze my budget: limit 100000, spent 30000, history is 5000, 6000, 7000, 5000, 25000, 6000"
}
```

---

## 5. Project-Specific Queries

### Project Name Detection
```bash
# Test 5.1: Query with project name mentioned
POST /api/query
{
  "query": "Check budget for Website Redesign project: 50000 limit, 42000 spent"
}
# Expected: Should use/create "Website Redesign" project

# Test 5.2: Query with different project name format
POST /api/query
{
  "query": "How much remaining in Mobile App Development?"
}
# Expected: Should detect "Mobile App Development" project

# Test 5.3: Query with project ID
POST /api/query
{
  "query": "Check my budget",
  "project_id": "{project_id}"
}
# Expected: Should use specified project
```

### Switch Between Projects
```bash
# Test 5.4: Query project A
POST /api/query
{
  "query": "Check budget for Website Redesign: 50000 limit, 30000 spent"
}

# Test 5.5: Query project B (should switch context)
POST /api/query
{
  "query": "Check budget for Mobile App: 100000 limit, 50000 spent"
}

# Test 5.6: Query without project (should use last active)
POST /api/query
{
  "query": "How much remaining?"
}
# Expected: Should use Mobile App project
```

---

## 6. Natural Language Variations

### Different Phrasings
```bash
# Test 6.1: Formal query
POST /api/query
{
  "query": "Please analyze my budget. The limit is 50000 and I have spent 42000."
}

# Test 6.2: Casual query
POST /api/query
{
  "query": "yo check my budget 50k limit spent 42k"
}

# Test 6.3: Question format
POST /api/query
{
  "query": "How much budget do I have left if my limit is 50000 and I spent 42000?"
}

# Test 6.4: Statement format
POST /api/query
{
  "query": "My budget limit is fifty thousand dollars, I've spent forty-two thousand"
}
```

### Intent Variations
```bash
# Test 6.5: Check intent
POST /api/query
{
  "query": "Check my budget status"
}

# Test 6.6: Predict intent
POST /api/query
{
  "query": "Will I exceed my budget?"
}

# Test 6.7: Recommend intent
POST /api/query
{
  "query": "Suggest ways to reduce spending"
}

# Test 6.8: Analyze intent
POST /api/query
{
  "query": "Analyze my spending patterns"
}

# Test 6.9: Report intent
POST /api/query
{
  "query": "Generate a budget report"
}
```

---

## 7. Edge Cases

### Zero and Negative Values
```bash
# Test 7.1: Zero spent
POST /api/query
{
  "query": "Check budget: 50000 limit, 0 spent"
}

# Test 7.2: Zero budget (should error)
POST /api/query
{
  "query": "Check budget: 0 limit, 5000 spent"
}
# Expected: Should return error

# Test 7.3: Negative spent (should error)
POST /api/query
{
  "query": "Check budget: 50000 limit, -1000 spent"
}
# Expected: Should return error
```

### Large Numbers
```bash
# Test 7.4: Large budget
POST /api/query
{
  "query": "Check budget: 1000000 limit, 750000 spent"
}

# Test 7.5: Large spending history
POST /api/query
{
  "query": "Analyze budget: limit 500000, spent 200000, history is 10000, 15000, 20000, 18000, 25000, 30000, 22000"
}
```

### Missing Information
```bash
# Test 7.6: Missing budget limit
POST /api/query
{
  "query": "I've spent 42000"
}
# Expected: Should use existing budget limit or error

# Test 7.7: Missing spent
POST /api/query
{
  "query": "My budget limit is 50000"
}
# Expected: Should use existing spent or default to 0
```

### Special Characters
```bash
# Test 7.8: Query with special characters
POST /api/query
{
  "query": "Check budget: $50,000 limit, $42,000 spent"
}

# Test 7.9: Query with abbreviations
POST /api/query
{
  "query": "Budget: 50k limit, 42k spent"
}
```

---

## 8. Analysis & Predictions

### Spending Rate Analysis
```bash
# Test 8.1: Analyze with history
POST /api/query
{
  "query": "Analyze my budget: limit 100000, spent 30000, history is 5000, 6000, 7000, 5000, 25000, 6000"
}
# Expected: Should calculate spending rate, detect anomalies

# Test 8.2: Predict overspending
POST /api/query
{
  "query": "Will I exceed my budget? Limit 50000, spent 42000, history is 5000, 6000, 7000, 8000"
}
# Expected: Should predict overshoot risk
```

### Anomaly Detection
```bash
# Test 8.3: Detect spending anomalies
POST /api/query
{
  "query": "Analyze spending: limit 100000, spent 50000, history is 5000, 6000, 7000, 5000, 25000, 6000"
}
# Expected: Should detect 25000 as anomaly

# Test 8.4: No anomalies
POST /api/query
{
  "query": "Analyze budget: limit 100000, spent 30000, history is 5000, 6000, 7000, 5000, 6000"
}
# Expected: No anomalies detected
```

### Recommendations
```bash
# Test 8.5: Get recommendations
POST /api/query
{
  "query": "Suggest ways to manage my budget. Limit 50000, spent 45000"
}
# Expected: Should provide recommendations

# Test 8.6: Low risk scenario
POST /api/query
{
  "query": "Check budget: 100000 limit, 20000 spent"
}
# Expected: Should show low risk, positive recommendations
```

---

## 9. Complete Workflow Tests

### Full Project Lifecycle
```bash
# Step 1: Create project
POST /api/projects
{
  "project_name": "Test Project",
  "budget_limit": 50000
}

# Step 2: Set initial budget
POST /api/query
{
  "query": "Check budget for Test Project: 50000 limit, 10000 spent"
}

# Step 3: Add spending multiple times
POST /api/query
{
  "query": "I spent 5000 today on Test Project"
}
POST /api/query
{
  "query": "Add 3000 more to Test Project expenses"
}

# Step 4: Check status
POST /api/query
{
  "query": "How much remaining in Test Project?"
}

# Step 5: Analyze
POST /api/query
{
  "query": "Analyze Test Project budget"
}

# Step 6: Update budget limit
POST /api/query
{
  "query": "Update Test Project budget to 75000"
}

# Step 7: Final check
GET /api/projects/{project_id}/budget
```

---

## 10. Error Handling Tests

### Invalid Inputs
```bash
# Test 10.1: Invalid project ID
GET /api/projects/invalid-id
# Expected: 404 Not Found

# Test 10.2: Missing required fields
POST /api/projects
{
  "project_name": ""
}
# Expected: Validation error

# Test 10.3: Invalid update
POST /api/update
{
  "update_type": "invalid",
  "update_field": "spent",
  "update_value": 5000
}
# Expected: Validation error
```

### API Key Tests
```bash
# Test 10.4: Missing API key (if not set)
POST /api/query
{
  "query": "Check my budget"
}
# Expected: Error about missing Gemini API key
```

---

## 📊 Testing Checklist

Use this checklist to ensure all features are tested:

- [ ] Project creation
- [ ] Project listing
- [ ] Project retrieval
- [ ] Project update
- [ ] Project deletion
- [ ] Set current project
- [ ] Basic budget check
- [ ] Budget with project name
- [ ] Budget with project ID
- [ ] Add spending (update)
- [ ] Set spending directly
- [ ] Update budget limit
- [ ] Initial spent in history
- [ ] Multiple spending additions
- [ ] History tracking
- [ ] Project name detection
- [ ] Project switching
- [ ] Natural language variations
- [ ] Different intents (check, predict, recommend, analyze)
- [ ] Edge cases (zero, negative, large numbers)
- [ ] Missing information handling
- [ ] Spending rate calculation
- [ ] Overshoot prediction
- [ ] Anomaly detection
- [ ] Recommendations generation
- [ ] Error handling
- [ ] Complete workflow

---

## 🚀 Quick Test Script

Save this as `test_all.sh` (or `test_all.ps1` for PowerShell):

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "=== Testing Project Management ==="
# Create project
curl -X POST "$BASE_URL/api/projects" \
  -H "Content-Type: application/json" \
  -d '{"project_name": "Test Project", "budget_limit": 50000}'

echo -e "\n=== Testing Budget Query ==="
# Query budget
curl -X POST "$BASE_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Check budget for Test Project: 50000 limit, 10000 spent"}'

echo -e "\n=== Testing Spending Update ==="
# Add spending
curl -X POST "$BASE_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "I spent 5000 today on Test Project"}'

echo -e "\n=== Testing Analysis ==="
# Analyze
curl -X POST "$BASE_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze Test Project budget"}'
```

---

## 💡 Tips for Testing

1. **Start Fresh**: Clear your database or LTM files before comprehensive testing
2. **Test Incrementally**: Test one feature at a time
3. **Check Responses**: Verify JSON structure and values
4. **Test Edge Cases**: Don't just test happy paths
5. **Verify History**: Check that history is correctly tracked
6. **Project Isolation**: Ensure projects don't interfere with each other
7. **Natural Language**: Test various phrasings to ensure robustness

---

## 📝 Notes

- Replace `{project_id}` with actual project IDs from your database
- Adjust URLs if your API runs on a different port
- Some tests may require previous setup (e.g., project must exist before querying)
- History tracking tests require sequential queries to verify accumulation

