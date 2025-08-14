#!/usr/bin/env python3
"""Test CEZ HDO integration syntax and structure."""

import ast
import sys
from pathlib import Path

def test_python_syntax():
    """Test all Python files for syntax errors."""
    errors = []
    integration_dir = Path("custom_components/cez_hdo")
    
    if not integration_dir.exists():
        return ["Integration directory not found"]
    
    python_files = list(integration_dir.glob("*.py"))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check syntax
            ast.parse(content, filename=str(py_file))
            print(f"✅ {py_file.name}: Syntax OK")
            
        except SyntaxError as e:
            error_msg = f"❌ {py_file.name}: Syntax error at line {e.lineno}: {e.msg}"
            errors.append(error_msg)
            print(error_msg)
        except Exception as e:
            error_msg = f"❌ {py_file.name}: Error reading file: {e}"
            errors.append(error_msg)
            print(error_msg)
    
    return errors

def test_imports():
    """Test if imports are reasonable."""
    integration_dir = Path("custom_components/cez_hdo")
    issues = []
    
    for py_file in integration_dir.glob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(py_file))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ['homeassistant', 'aiohttp']:
                            print(f"✅ {py_file.name}: Found expected import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if node.module and 'homeassistant' in node.module:
                        print(f"✅ {py_file.name}: Found Home Assistant import from {node.module}")
        
        except Exception as e:
            issues.append(f"❌ {py_file.name}: Error analyzing imports: {e}")
    
    return issues

def test_manifest_structure():
    """Test manifest.json structure."""
    manifest_file = Path("custom_components/cez_hdo/manifest.json")
    
    if not manifest_file.exists():
        return ["manifest.json not found"]
    
    try:
        import json
        with open(manifest_file) as f:
            manifest = json.load(f)
        
        required_fields = [
            "domain", "name", "version", "requirements", 
            "config_flow", "codeowners", "iot_class"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in manifest:
                missing_fields.append(field)
            else:
                print(f"✅ manifest.json: Found {field} = {manifest[field]}")
        
        if missing_fields:
            return [f"manifest.json missing fields: {', '.join(missing_fields)}"]
        
        # Check specific values
        if manifest.get("config_flow") != True:
            return ["manifest.json: config_flow should be true"]
        
        if not isinstance(manifest.get("requirements"), list):
            return ["manifest.json: requirements should be a list"]
        
        return []
        
    except json.JSONDecodeError as e:
        return [f"manifest.json: Invalid JSON: {e}"]
    except Exception as e:
        return [f"manifest.json: Error reading: {e}"]

def main():
    """Run all tests."""
    print("=== CEZ HDO INTEGRATION STRUCTURE TEST ===\n")
    
    print("Testing Python syntax...")
    syntax_errors = test_python_syntax()
    
    print("\nTesting imports...")
    import_issues = test_imports()
    
    print("\nTesting manifest.json...")
    manifest_issues = test_manifest_structure()
    
    print("\n=== TEST RESULTS ===")
    
    all_issues = syntax_errors + import_issues + manifest_issues
    
    if all_issues:
        print(f"❌ Found {len(all_issues)} issues:")
        for issue in all_issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ All structure tests passed!")
        print("✅ Integration is ready for HACS installation")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
