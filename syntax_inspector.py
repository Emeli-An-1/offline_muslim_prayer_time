#!/usr/bin/env python3
"""
PrayerOffline - Syntax Error Inspector
Shows the exact syntax error and provides fix suggestions
"""

import ast
import sys
from pathlib import Path


def inspect_syntax_error(file_path: str):
    """Inspect and show detailed syntax error information"""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"\n🔍 Inspecting: {file_path}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Try to parse
        ast.parse(content)
        print("✅ No syntax errors found!")
        return True
    
    except SyntaxError as e:
        print("❌ SYNTAX ERROR FOUND!\n")
        print("=" * 70)
        print(f"Error Message: {e.msg}")
        print(f"Line Number:   {e.lineno}")
        print(f"Column:        {e.offset}")
        print("=" * 70)
        
        # Show context
        if e.lineno:
            start = max(0, e.lineno - 6)
            end = min(len(lines), e.lineno + 5)
            
            print("\n📋 CODE CONTEXT:\n")
            print("-" * 70)
            
            for i in range(start, end):
                line_num = i + 1
                line_content = lines[i] if i < len(lines) else ""
                
                # Highlight the error line
                if line_num == e.lineno:
                    print(f">>> {line_num:4d} | {line_content}")
                    if e.offset:
                        print(f"       | {' ' * (e.offset - 1)}^ ERROR HERE")
                else:
                    print(f"    {line_num:4d} | {line_content}")
            
            print("-" * 70)
            
            # Provide fix suggestions
            print("\n💡 FIX SUGGESTIONS:\n")
            
            error_line = lines[e.lineno - 1] if e.lineno <= len(lines) else ""
            
            # Common syntax error patterns
            if "invalid syntax" in e.msg.lower():
                if error_line.strip().startswith(('if', 'elif', 'else', 'for', 'while', 'def', 'class', 'try', 'except', 'finally', 'with')):
                    if not error_line.rstrip().endswith(':'):
                        print("   • Missing colon ':' at end of statement")
                        print(f"   • Try: {error_line.rstrip()}:")
                
                if error_line.count('(') != error_line.count(')'):
                    print("   • Unmatched parentheses")
                    print("   • Check if you're missing a closing ')'")
                
                if error_line.count('[') != error_line.count(']'):
                    print("   • Unmatched square brackets")
                    print("   • Check if you're missing a closing ']'")
                
                if error_line.count('{') != error_line.count('}'):
                    print("   • Unmatched curly braces")
                    print("   • Check if you're missing a closing '}'")
                
                if error_line.count("'") % 2 != 0 or error_line.count('"') % 2 != 0:
                    print("   • Unclosed string literal")
                    print("   • Check if you're missing a closing quote")
            
            elif "unexpected indent" in e.msg.lower():
                print("   • Unexpected indentation")
                print("   • Make sure indentation is consistent (use 4 spaces)")
                print("   • Check if previous line needs a colon ':'")
            
            elif "expected an indented block" in e.msg.lower():
                print("   • Missing indented block after colon")
                print("   • Add at least one indented line or use 'pass'")
            
            # Generic suggestions
            print("\n   Common fixes:")
            print("   1. Check for missing colons ':' at end of if/for/while/def/class")
            print("   2. Check for unmatched parentheses (), brackets [], or braces {}")
            print("   3. Check for unclosed strings \" or '")
            print("   4. Verify indentation (use 4 spaces consistently)")
            print("   5. Look at the line BEFORE the error - the issue might be there")
            
            return False
    
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def auto_fix_common_errors(file_path: str, backup: bool = True):
    """Attempt to auto-fix common syntax errors"""
    
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"\n🔧 Attempting auto-fix for: {file_path}\n")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Create backup
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✓ Backup created: {backup_path}")
        
        modified = False
        fixes = []
        
        for i, line in enumerate(lines):
            original_line = line
            
            # Fix 1: Add missing colon for control structures
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if any(stripped.startswith(kw + ' ') or stripped.startswith(kw + '(') 
                       for kw in ['if', 'elif', 'for', 'while', 'def', 'class', 'with']):
                    if not line.rstrip().endswith(':') and not line.rstrip().endswith('\\'):
                        lines[i] = line.rstrip() + ':\n'
                        fixes.append(f"Line {i+1}: Added missing colon")
                        modified = True
                
                elif stripped == 'else' or stripped.startswith('else:') or stripped == 'try' or stripped == 'finally':
                    if not line.rstrip().endswith(':'):
                        lines[i] = line.rstrip() + ':\n'
                        fixes.append(f"Line {i+1}: Added missing colon")
                        modified = True
                
                elif stripped.startswith('except'):
                    if not line.rstrip().endswith(':') and not stripped.endswith('\\'):
                        lines[i] = line.rstrip() + ':\n'
                        fixes.append(f"Line {i+1}: Added missing colon to except")
                        modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("✅ Auto-fixes applied:")
            for fix in fixes:
                print(f"   • {fix}")
            
            # Verify the fix worked
            print("\n🔍 Verifying fix...")
            return inspect_syntax_error(file_path)
        else:
            print("⚠️  No automatic fixes could be applied.")
            print("   Manual inspection required.")
            return False
    
    except Exception as e:
        print(f"❌ Error during auto-fix: {e}")
        return False


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║       PrayerOffline - Syntax Error Inspector & Fixer         ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Default to tasbih_view.py (the file with the error)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "views/tasbih_view.py"
    
    print(f"Target file: {file_path}\n")
    
    # First, inspect the error
    is_valid = inspect_syntax_error(file_path)
    
    if not is_valid:
        print("\n" + "=" * 70)
        response = input("\n🔧 Would you like to attempt auto-fix? (y/n): ").strip().lower()
        
        if response == 'y':
            auto_fix_common_errors(file_path, backup=True)
        else:
            print("\n📝 Please fix the error manually using the suggestions above.")
            print("   After fixing, run this script again to verify.")
    
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()