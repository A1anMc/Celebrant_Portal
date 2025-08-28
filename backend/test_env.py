#!/usr/bin/env python3
"""
Simple environment variable test script
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Environment Variable Test")
print("=" * 50)

# Test critical variables
critical_vars = [
    'DATABASE_URL',
    'SECRET_KEY', 
    'ALLOWED_ORIGINS',
    'ENVIRONMENT',
    'DEBUG'
]

for var in critical_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {'*' * min(len(value), 10)}...")
    else:
        print(f"❌ {var}: NOT SET")

print("\n🔧 All Environment Variables:")
print("-" * 30)
for key, value in os.environ.items():
    if any(keyword in key.upper() for keyword in ['DATABASE', 'SECRET', 'ORIGIN', 'ENV', 'DEBUG']):
        print(f"{key}: {'*' * min(len(value), 10)}...")
