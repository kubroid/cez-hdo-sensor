#!/usr/bin/env python3
"""Test HACS structure and requirements."""

import json
import os
import sys
from pathlib import Path

def test_hacs_structure():
    """Test if the repository structure is HACS compatible."""
    errors = []
    warnings = []
    
    # Check if hacs.json exists
    hacs_file = Path("hacs.json")
    if not hacs_file.exists():
        errors.append("hacs.json file missing")
    else:
        # Validate hacs.json content
        try:
            with open(hacs_file) as f:
                hacs_data = json.load(f)
            
            required_fields = ["name", "domains", "render_readme"]
            for field in required_fields:
                if field not in hacs_data:
                    errors.append(f"hacs.json missing required field: {field}")
            
            # Check version consistency
            if "version" in hacs_data:
                print(f"HACS version: {hacs_data['version']}")
        except json.JSONDecodeError as e:
            errors.append(f"hacs.json invalid JSON: {e}")
    
    # Check custom_components structure
    custom_components_dir = Path("custom_components")
    if not custom_components_dir.exists():
        errors.append("custom_components directory missing")
    else:
        integration_dirs = [d for d in custom_components_dir.iterdir() if d.is_dir()]
        if not integration_dirs:
            errors.append("No integration found in custom_components")
        
        for integration_dir in integration_dirs:
            print(f"Found integration: {integration_dir.name}")
            
            # Check required files
            required_files = ["__init__.py", "manifest.json"]
            for req_file in required_files:
                file_path = integration_dir / req_file
                if not file_path.exists():
                    errors.append(f"{integration_dir.name}/{req_file} missing")
            
            # Check manifest.json
            manifest_file = integration_dir / "manifest.json"
            if manifest_file.exists():
                try:
                    with open(manifest_file) as f:
                        manifest_data = json.load(f)
                    
                    required_manifest_fields = ["domain", "name", "version"]
                    for field in required_manifest_fields:
                        if field not in manifest_data:
                            errors.append(f"manifest.json missing required field: {field}")
                    
                    print(f"Integration version: {manifest_data.get('version', 'UNKNOWN')}")
                    print(f"Integration domain: {manifest_data.get('domain', 'UNKNOWN')}")
                    
                    # Check version consistency between hacs.json and manifest.json
                    if hacs_file.exists():
                        if manifest_data.get("version") != hacs_data.get("version"):
                            warnings.append(f"Version mismatch: manifest.json ({manifest_data.get('version')}) vs hacs.json ({hacs_data.get('version')})")
                    
                except json.JSONDecodeError as e:
                    errors.append(f"manifest.json invalid JSON: {e}")
    
    # Check README file
    readme_files = ["README.md", "README.rst", "readme.md"]
    if not any(Path(f).exists() for f in readme_files):
        warnings.append("No README file found")
    
    # Print results
    print("\n=== HACS STRUCTURE TEST RESULTS ===")
    
    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors and not warnings:
        print("\n✅ All checks passed! Repository is HACS compatible.")
    elif not errors:
        print("\n✅ Structure is valid with minor warnings.")
    else:
        print("\n❌ Repository has structural issues that need to be fixed.")
        return False
    
    return True

if __name__ == "__main__":
    success = test_hacs_structure()
    sys.exit(0 if success else 1)
