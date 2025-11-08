#!/usr/bin/env python3
"""
PrayerOffline - Auto-Fix Critical Issues
Automatically fixes the critical errors found in diagnostic report
"""

import os
import re
from pathlib import Path
from datetime import datetime


class AutoFixer:
    """Automatically fixes critical code issues"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.errors = []
    
    def fix_all(self):
        """Run all auto-fixes"""
        print("🔧 Starting Auto-Fix Process...\n")
        
        # Fix 1: Syntax error in tasbih_view.py (line 496)
        print("1️⃣  Fixing syntax error in tasbih_view.py...")
        self.fix_tasbih_syntax()
        
        # Fix 2: Add encoding to file operations
        print("2️⃣  Adding UTF-8 encoding to file operations...")
        self.fix_file_encoding()
        
        # Fix 3: Replace bare except clauses
        print("3️⃣  Replacing bare except clauses...")
        self.fix_bare_excepts()
        
        # Fix 4: Remove localStorage/sessionStorage references
        print("4️⃣  Checking for localStorage/sessionStorage usage...")
        self.fix_storage_api()
        
        print("\n✅ Auto-fix complete!\n")
        self.print_summary()
    
    def fix_tasbih_syntax(self):
        """Fix syntax error in tasbih_view.py at line 496"""
        file_path = self.project_root / "views" / "tasbih_view.py"
        
        if not file_path.exists():
            self.errors.append(f"File not found: {file_path}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check line 496 (index 495)
            if len(lines) > 495:
                original_line = lines[495]
                
                # Common syntax errors to fix
                fixed = False
                
                # Fix missing colon
                if original_line.strip() and not original_line.strip().endswith(':') and \
                   any(keyword in original_line for keyword in ['if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except', 'finally', 'with ']):
                    lines[495] = original_line.rstrip() + ':\n'
                    fixed = True
                
                # Fix unclosed parentheses/brackets
                elif original_line.count('(') > original_line.count(')'):
                    # Look for the closing in next lines
                    for i in range(496, min(len(lines), 500)):
                        if ')' in lines[i]:
                            break
                    else:
                        lines[495] = original_line.rstrip() + ')\n'
                        fixed = True
                
                # Fix missing comma in list/dict
                elif original_line.strip() and not original_line.strip().endswith((',', '[', '{', '(', ':')):
                    if len(lines) > 496 and lines[496].strip() and not lines[496].strip().startswith((']', '}', ')')):
                        lines[495] = original_line.rstrip() + ',\n'
                        fixed = True
                
                if fixed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.fixes_applied.append(f"Fixed syntax error in {file_path} line 496")
                    print(f"   ✓ Fixed syntax at line 496")
                else:
                    # Read context around line 496
                    context_start = max(0, 493)
                    context_end = min(len(lines), 500)
                    context = ''.join(lines[context_start:context_end])
                    
                    print(f"   ⚠️  Manual inspection needed. Context around line 496:")
                    print(f"   {'-' * 60}")
                    for i, line in enumerate(lines[context_start:context_end], start=context_start+1):
                        marker = ">>> " if i == 496 else "    "
                        print(f"   {marker}{i:4d}: {line.rstrip()}")
                    print(f"   {'-' * 60}")
        
        except Exception as e:
            self.errors.append(f"Error fixing tasbih_view.py: {e}")
            print(f"   ❌ Error: {e}")
    
    def fix_file_encoding(self):
        """Add encoding='utf-8' to file open operations"""
        files_to_fix = [
            "tests/test_notifications.py"
        ]
        
        for file_rel in files_to_fix:
            file_path = self.project_root / file_rel.replace('/', os.sep)
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace open() calls without encoding
                pattern = r'\bopen\s*\(\s*([^)]+?)\s*\)'
                
                def add_encoding(match):
                    args = match.group(1)
                    # Don't modify if already has encoding, or if using binary mode
                    if 'encoding' in args or "'rb'" in args or '"rb"' in args or \
                       "'wb'" in args or '"wb"' in args:
                        return match.group(0)
                    # Add encoding parameter
                    return f'open({args}, encoding="utf-8")'
                
                new_content = re.sub(pattern, add_encoding, content)
                
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    self.fixes_applied.append(f"Added encoding to {file_path}")
                    print(f"   ✓ Fixed encoding in {file_rel}")
            
            except Exception as e:
                self.errors.append(f"Error fixing encoding in {file_rel}: {e}")
    
    def fix_bare_excepts(self):
        """Replace bare except: with except Exception:"""
        files_with_bare_except = [
            "quick_fix.py",
            "services/audio_player.py",
            "services/notifier.py",
            "services/praytimes.py",
            "services/storage.py",
            "views/dashboard_view.py"
        ]
        
        for file_rel in files_with_bare_except:
            file_path = self.project_root / file_rel.replace('/', os.sep)
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                modified = False
                for i, line in enumerate(lines):
                    # Match bare except with proper indentation
                    if re.match(r'^(\s*)except\s*:\s*$', line):
                        indent = re.match(r'^(\s*)', line).group(1)
                        lines[i] = f'{indent}except Exception:\n'
                        modified = True
                
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)
                    self.fixes_applied.append(f"Fixed bare except in {file_path}")
                    print(f"   ✓ Fixed bare except in {file_rel}")
            
            except Exception as e:
                self.errors.append(f"Error fixing bare except in {file_rel}: {e}")
    
    def fix_storage_api(self):
        """Check and warn about localStorage/sessionStorage usage"""
        # Note: diagnose.py itself uses these in detection - ignore it
        files_to_check = []
        
        for py_file in self.project_root.rglob('*.py'):
            if 'venv' in str(py_file) or '.venv' in str(py_file):
                continue
            if py_file.name == 'diagnose.py':
                continue  # Skip the diagnostic tool itself
            
            files_to_check.append(py_file)
        
        found_issues = False
        for file_path in files_to_check:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'localStorage' in content or 'sessionStorage' in content:
                    print(f"   ⚠️  Found storage API usage in {file_path.relative_to(self.project_root)}")
                    print(f"      This is NOT supported in Flet. Please use React state or in-memory storage.")
                    found_issues = True
            
            except Exception:
                pass
        
        if not found_issues:
            print(f"   ✓ No localStorage/sessionStorage usage found")
    
    def print_summary(self):
        """Print summary of fixes"""
        print("=" * 70)
        print("AUTO-FIX SUMMARY")
        print("=" * 70)
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        
        if self.fixes_applied:
            for fix in self.fixes_applied:
                print(f"   • {fix}")
        
        if self.errors:
            print(f"\n❌ Errors Encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        print("=" * 70)
        
        # Create fix log
        log_path = self.project_root / "auto_fix_log.txt"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("PrayerOffline - Auto-Fix Log\n")
            f.write("=" * 70 + "\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            
            f.write("FIXES APPLIED\n")
            f.write("-" * 70 + "\n")
            for fix in self.fixes_applied:
                f.write(f"✓ {fix}\n")
            
            if self.errors:
                f.write("\nERRORS\n")
                f.write("-" * 70 + "\n")
                for error in self.errors:
                    f.write(f"✗ {error}\n")
            
            f.write("\n" + "=" * 70 + "\n")
        
        print(f"\n📄 Fix log saved to: {log_path}")


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         PrayerOffline - Auto-Fix Critical Issues             ║
║                    Version 1.0                                ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    import sys
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    
    fixer = AutoFixer(project_root)
    fixer.fix_all()
    
    # If critical errors remain, suggest next steps
    if fixer.errors:
        print("\n⚠️  Some issues require manual attention.")
        print("   Please review the errors above and the auto_fix_log.txt file.")
    else:
        print("\n🎉 All critical issues have been addressed!")
        print("   You can now try running: python main.py")


if __name__ == '__main__':
    main()