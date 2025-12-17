"""
Test script for nested JSON functionality in the DeployFolder tool.

Copyright (c) 2025 Janosch Meyer (janosch.code@proton.me)
This project is licensed under the MIT License - see the LICENSE file for details.
This project was created with the assistance of artificial intelligence.
"""

import sys
import os
import json

from deployfolder import replace_placeholders

def test_nested_json():
    """Test the nested JSON functionality in replace_placeholders."""
    # Test values with nested JSON
    values = {
        "project_name": "MyProject",
        "environment": "production",
        "date": "2025-11-08",
        "user": {
            "name": "JohnDoe",
            "role": "admin"
        },
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "credentials": {
                "username": "dbuser",
                "password": "secret"
            }
        }
    }
    
    # Test cases
    test_cases = [
        # Simple top-level placeholder
        {
            "input": "Project: {{ project_name }}",
            "expected": "Project: MyProject"
        },
        # First-level nested placeholder
        {
            "input": "User: {{ user.name }}",
            "expected": "User: JohnDoe"
        },
        # Another first-level nested placeholder
        {
            "input": "Role: {{ user.role }}",
            "expected": "Role: admin"
        },
        # Second-level nested placeholder
        {
            "input": "DB Host: {{ database.host }}",
            "expected": "DB Host: db.example.com"
        },
        # Numeric value
        {
            "input": "DB Port: {{ database.port }}",
            "expected": "DB Port: 5432"
        },
        # Deeply nested placeholder
        {
            "input": "DB User: {{ database.credentials.username }}",
            "expected": "DB User: dbuser"
        },
        # Multiple placeholders in one string
        {
            "input": "{{ user.name }} is an {{ user.role }} on {{ database.host }}",
            "expected": "JohnDoe is an admin on db.example.com"
        },
        # Non-existent placeholder (should remain unchanged)
        {
            "input": "Missing: {{ nonexistent.key }}",
            "expected": "Missing: {{ nonexistent.key }}"
        },
        # Mixed existing and non-existent placeholders
        {
            "input": "{{ user.name }} has {{ nonexistent.key }}",
            "expected": "JohnDoe has {{ nonexistent.key }}"
        }
    ]
    
    # Run tests
    passed = 0
    failed = 0
    
    print("Testing nested JSON functionality in replace_placeholders:")
    print("-" * 60)
    
    for i, test in enumerate(test_cases, 1):
        result = replace_placeholders(test["input"], values)
        if result == test["expected"]:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1
        
        print(f"Test {i}: {status}")
        print(f"  Input:    {test['input']}")
        print(f"  Expected: {test['expected']}")
        print(f"  Result:   {result}")
        if status == "FAIL":
            print(f"  ERROR: Expected '{test['expected']}', got '{result}'")
        print()
    
    print("-" * 60)
    print(f"Summary: {passed} passed, {failed} failed")
    
    return failed == 0

if __name__ == "__main__":
    success = test_nested_json()
    sys.exit(0 if success else 1)