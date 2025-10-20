# Fix em-dash characters for latin-1 encoding
import sys
from pathlib import Path

def fix_emdash(filepath):
    """Replace em-dash (U+2014) with hyphen-minus (U+002D)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace em-dash with normal hyphen
    fixed_content = content.replace('\u2014', '-')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed {filepath}")

if __name__ == '__main__':
    fix_emdash(Path('pages') / '07_pdf-ausgabe.py')
    print("Done!")
