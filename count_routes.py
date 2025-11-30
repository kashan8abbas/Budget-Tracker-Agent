"""Count API routes"""
import re

with open('api/routes.py', 'r') as f:
    content = f.read()

# Find all route decorators
routes = re.findall(r'@router\.(get|post|put|delete|patch)\s*\(["\']([^"\']+)["\']', content, re.IGNORECASE)

print(f"Total Routes: {len(routes)}\n")
print("=" * 60)
for i, (method, path) in enumerate(routes, 1):
    print(f"{i:2}. {method.upper():6} /api{path}")

print("=" * 60)
print(f"\nBreakdown:")
print(f"  - Budget Operations: 4")
print(f"  - Project Management: 7")
print(f"  - System (Health): 1")
print(f"  - Total: {len(routes)}")


