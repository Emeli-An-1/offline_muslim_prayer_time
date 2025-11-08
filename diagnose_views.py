"""
Diagnose what's wrong with view files
"""

from pathlib import Path
import re


def analyze_file(file_path):
    """Analyze a Python file for issues"""
    print(f"\n{'='*70}")
    print(f"Analyzing: {file_path}")
    print('='*70)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Check class definition
        print("\n[Class Definition]")
        for i, line in enumerate(lines[:50], 1):  # Check first 50 lines
            if 'class ' in line and 'View' in line:
                print(f"  Line {i}: {line.strip()}")
                # Check next few lines for inheritance
                for j in range(i, min(i+5, len(lines))):
                    if lines[j].strip():
                        print(f"  Line {j+1}: {lines[j].strip()}")
                    if ':' in lines[j]:
                        break
        
        # Check imports
        print("\n[Imports]")
        for i, line in enumerate(lines[:30], 1):
            if 'import' in line.lower():
                print(f"  Line {i}: {line.strip()}")
        
        # Check for UserControl
        print("\n[UserControl Usage]")
        if 'UserControl' in content:
            print("  ⚠ Found 'UserControl' in file")
            for i, line in enumerate(lines, 1):
                if 'UserControl' in line:
                    print(f"    Line {i}: {line.strip()}")
        else:
            print("  ✓ No UserControl found")
        
        # Check for build method
        print("\n[Build Method]")
        has_build = False
        for i, line in enumerate(lines, 1):
            if 'def build' in line:
                has_build = True
                print(f"  Line {i}: {line.strip()}")
                # Show next 3 lines
                for j in range(i, min(i+3, len(lines))):
                    if lines[j].strip():
                        print(f"  Line {j+1}: {lines[j].strip()}")
        
        if not has_build:
            print("  ⚠ No build() method found")
        
        # Check if it's trying to import from flet incorrectly
        print("\n[Potential Issues]")
        issues = []
        
        if 'from flet import UserControl' in content:
            issues.append("Importing UserControl from flet")
        if 'ft.UserControl' in content:
            issues.append("Using ft.UserControl")
        if 'class' in content and 'UserControl' in content:
            issues.append("Class inheriting from UserControl")
        
        if issues:
            print("  ⚠ Issues found:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print("  ✓ No obvious issues")
        
        return True
        
    except Exception as e:
        print(f"✗ Error analyzing file: {e}")
        return False


def main():
    print("=" * 70)
    print("View Files Diagnostic")
    print("=" * 70)
    
    # Check all view files
    views_dir = Path("views")
    if views_dir.exists():
        view_files = list(views_dir.glob("*_view.py"))
        
        if not view_files:
            print("\n⚠ No view files found!")
            return
        
        for view_file in view_files:
            analyze_file(view_file)
    else:
        print("\n✗ views/ directory not found!")
    
    print("\n" + "=" * 70)
    print("Diagnostic Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()