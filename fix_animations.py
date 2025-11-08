import os
import re

def fix_animation_imports(directory):
    """Tüm .py dosyalardaki animation importlarını düzelt"""
    
    replacements = [
        (r'ft\.animation\.Animation', 'ft.Animation'),
        (r'ft\.animation\.AnimationCurve', 'ft.AnimationCurve'),
    ]
    
    for root, dirs, files in os.walk(directory):
        if 'components' not in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    original = content
                    
                    for pattern, replacement in replacements:
                        content = re.sub(pattern, replacement, content)
                    
                    if content != original:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✓ Fixed: {filepath}")
                    
                except Exception as e:
                    print(f"✗ Error: {e}")

if __name__ == '__main__':
    fix_animation_imports('.')
    print("\nDüzeltme tamamlandı!")