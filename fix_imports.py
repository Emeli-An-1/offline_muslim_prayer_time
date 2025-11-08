"""
Fix missing imports in view and component files
"""

from pathlib import Path
import re


def fix_snackbartype_imports(file_path):
    """Remove SnackBarType imports from view files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Remove SnackBarType from imports
        patterns = [
            r'from views\.base_view import.*?SnackBarType.*?\n',
            r'from \.base_view import.*?SnackBarType.*?\n',
            r',\s*SnackBarType',
            r'SnackBarType\s*,',
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, '', content)
                changes.append('removed SnackBarType import')
        
        # Clean up any double commas or spaces
        content = re.sub(r',\s*,', ',', content)
        content = re.sub(r'import\s+,', 'import ', content)
        content = re.sub(r'from .* import\s*\)', 'from views.base_view import BaseView', content)
        
        # Fix any usage of SnackBarType in the code
        if 'SnackBarType.' in content:
            # Replace with string literals
            content = content.replace('SnackBarType.ERROR', '"error"')
            content = content.replace('SnackBarType.SUCCESS', '"success"')
            content = content.replace('SnackBarType.INFO', '"info"')
            content = content.replace('SnackBarType.WARNING', '"warning"')
            changes.append('replaced SnackBarType usage')
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            if changes:
                print(f"  Changes: {', '.join(set(changes))}")
            return True
        else:
            print(f"○ No SnackBarType issues: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def fix_prayer_card_imports():
    """Fix imports in prayer_card.py"""
    file_path = Path("components/prayer_card.py")
    
    if not file_path.exists():
        print(f"○ {file_path} not found")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        changes = []
        
        # Remove bad imports
        bad_imports = [
            r'from components\.navigation_rail import get_navigation_component',
            r'from \.navigation_rail import get_navigation_component',
        ]
        
        for pattern in bad_imports:
            if re.search(pattern, content):
                content = re.sub(pattern + r'\n?', '', content)
                changes.append('removed get_navigation_component import')
        
        # Fix any usage of get_navigation_component
        if 'get_navigation_component' in content:
            content = content.replace(
                'get_navigation_component(',
                'create_navigation_rail('
            )
            # Add the correct import if not present
            if 'from components.navigation_rail import' not in content and 'from .navigation_rail import' not in content:
                # Add import at the top
                import_line = "from components.navigation_rail import create_navigation_rail, AppNavigationRail\n"
                # Find first non-comment, non-docstring line
                lines = content.split('\n')
                insert_idx = 0
                in_docstring = False
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if '"""' in line or "'''" in line:
                        in_docstring = not in_docstring
                    elif not in_docstring and stripped and not stripped.startswith('#'):
                        if stripped.startswith('import ') or stripped.startswith('from '):
                            insert_idx = i + 1
                        else:
                            break
                
                lines.insert(insert_idx, import_line)
                content = '\n'.join(lines)
                changes.append('added correct import')
        
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {file_path}")
            if changes:
                print(f"  Changes: {', '.join(set(changes))}")
            return True
        else:
            print(f"○ No import issues: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {e}")
        return False


def main():
    print("=" * 70)
    print("Fixing Missing Import Issues")
    print("=" * 70)
    
    total_fixed = 0
    
    # Fix SnackBarType in all view files
    print("\n[1] Fixing SnackBarType imports in views...")
    print("-" * 70)
    views_dir = Path("views")
    if views_dir.exists():
        for view_file in views_dir.glob("*_view.py"):
            if fix_snackbartype_imports(view_file):
                total_fixed += 1
    
    # Fix prayer_card imports
    print("\n[2] Fixing prayer_card.py imports...")
    print("-" * 70)
    if fix_prayer_card_imports():
        total_fixed += 1
    
    print("\n" + "=" * 70)
    print(f"✓ Fixed {total_fixed} file(s)")
    print("\nNext step: Run 'python check_imports.py'")
    print("=" * 70)


if __name__ == "__main__":
    main()