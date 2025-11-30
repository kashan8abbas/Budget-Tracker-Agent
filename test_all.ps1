# Budget Tracker API - Comprehensive Test Script
# Run this script to test all functionality

$baseUrl = "http://localhost:8000"
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "=== Budget Tracker API Test Suite ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Create Project
Write-Host "Test 1: Creating Website Redesign project..." -ForegroundColor Yellow
$project1 = @{
    project_name = "Website Redesign"
    budget_limit = 50000
    description = "Complete website overhaul"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/projects" -Method POST -Body $project1 -Headers $headers
    $project1Id = $response.project_id
    Write-Host "✅ Project created: $project1Id" -ForegroundColor Green
    Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Create Another Project
Write-Host "Test 2: Creating Mobile App project..." -ForegroundColor Yellow
$project2 = @{
    project_name = "Mobile App Development"
    budget_limit = 100000
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/projects" -Method POST -Body $project2 -Headers $headers
    $project2Id = $response.project_id
    Write-Host "✅ Project created: $project2Id" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: List Projects
Write-Host "Test 3: Listing all projects..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/projects" -Method GET
    Write-Host "✅ Found $($response.projects.Count) projects" -ForegroundColor Green
    $response.projects | ForEach-Object {
        Write-Host "   - $($_.project_name): $($_.project_id)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: Initial Budget Check
Write-Host "Test 4: Checking initial budget..." -ForegroundColor Yellow
$query1 = @{
    query = "Check my budget for Website Redesign: 50000 limit, 10000 spent"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query1 -Headers $headers
    Write-Host "✅ Budget checked" -ForegroundColor Green
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
    Write-Host "   History: $($response.history -join ', ')" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: Add Spending
Write-Host "Test 5: Adding spending..." -ForegroundColor Yellow
$query2 = @{
    query = "I spent 5000 today on Website Redesign project"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query2 -Headers $headers
    Write-Host "✅ Spending added" -ForegroundColor Green
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: Add More Spending
Write-Host "Test 6: Adding more spending..." -ForegroundColor Yellow
$query3 = @{
    query = "Add 3000 more to Website Redesign expenses"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query3 -Headers $headers
    Write-Host "✅ More spending added" -ForegroundColor Green
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: Check Remaining
Write-Host "Test 7: Checking remaining budget..." -ForegroundColor Yellow
$query4 = @{
    query = "How much budget remaining for Website Redesign?"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query4 -Headers $headers
    Write-Host "✅ Remaining budget checked" -ForegroundColor Green
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
    Write-Host "   Spent: $($response.spent)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 8: Analyze with History
Write-Host "Test 8: Analyzing budget with history..." -ForegroundColor Yellow
$query5 = @{
    query = "Analyze my Website Redesign budget: limit 50000, spent 30000, history is 5000, 6000, 7000, 5000, 25000, 6000"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query5 -Headers $headers
    Write-Host "✅ Budget analyzed" -ForegroundColor Green
    Write-Host "   Spending Rate: $($response.spending_rate)" -ForegroundColor Gray
    Write-Host "   Overshoot Risk: $($response.overshoot_risk)" -ForegroundColor Gray
    Write-Host "   Anomalies: $($response.anomalies.Count)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 9: Switch Projects
Write-Host "Test 9: Switching to Mobile App project..." -ForegroundColor Yellow
$query6 = @{
    query = "Check budget for Mobile App Development: 100000 limit, 40000 spent"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query6 -Headers $headers
    Write-Host "✅ Switched to Mobile App project" -ForegroundColor Green
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 10: Natural Language Variations
Write-Host "Test 10: Testing natural language (casual)..." -ForegroundColor Yellow
$query7 = @{
    query = "yo check my budget 50k limit spent 42k"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/query" -Method POST -Body $query7 -Headers $headers
    Write-Host "✅ Natural language query processed" -ForegroundColor Green
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 11: Get Current Budget
Write-Host "Test 11: Getting current budget..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/budget" -Method GET
    Write-Host "✅ Current budget retrieved" -ForegroundColor Green
    Write-Host "   Project: $($response.project_name)" -ForegroundColor Gray
    Write-Host "   Remaining: $($response.remaining)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "=== Test Suite Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check the responses above for any errors." -ForegroundColor Yellow
Write-Host "For more comprehensive tests, see TEST_QUERIES.md" -ForegroundColor Yellow

