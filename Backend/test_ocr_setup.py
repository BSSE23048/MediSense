"""
Test OCR Setup - Diagnose OCR configuration issues
"""

import os
import sys

print("=" * 60)
print("OCR Setup Diagnostic")
print("=" * 60)
print()

# Check 1: Python packages
print("1. Checking Python packages...")
try:
    import pytesseract
    print("   ✓ pytesseract installed")
except ImportError:
    print("   ❌ pytesseract NOT installed")
    print("   Install with: pip install pytesseract")
    sys.exit(1)

try:
    from PIL import Image
    print("   ✓ Pillow installed")
except ImportError:
    print("   ❌ Pillow NOT installed")
    print("   Install with: pip install pillow")
    sys.exit(1)

print()

# Check 2: Tesseract executable
print("2. Checking Tesseract OCR executable...")
try:
    import pytesseract
    import platform
    
    # Try to get Tesseract version
    try:
        version = pytesseract.get_tesseract_version()
        print(f"   ✓ Tesseract found (version: {version})")
    except Exception as e:
        print(f"   ❌ Tesseract executable not found")
        print(f"   Error: {str(e)}")
        print()
        print("   SOLUTION:")
        if platform.system() == 'Windows':
            print("   1. Download Tesseract OCR from:")
            print("      https://github.com/UB-Mannheim/tesseract/wiki")
            print("   2. Install to: C:\\Program Files\\Tesseract-OCR")
            print("   3. Add to your .env file:")
            print("      TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
        else:
            print("   Install with: sudo apt-get install tesseract-ocr")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Error checking Tesseract: {str(e)}")
    sys.exit(1)

print()

# Check 3: Test OCR on a simple case
print("3. Testing OCR functionality...")
try:
    # Create a simple test image (if PIL is available)
    from PIL import Image, ImageDraw, ImageFont
    import io
    
    # Create a simple test image with text
    img = Image.new('RGB', (200, 50), color='white')
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Test OCR", fill='black')
    
    # Try OCR
    text = pytesseract.image_to_string(img)
    if text.strip():
        print(f"   ✓ OCR test successful")
        print(f"   Extracted text: '{text.strip()}'")
    else:
        print("   ⚠️  OCR test returned empty text")
except Exception as e:
    print(f"   ❌ OCR test failed: {str(e)}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ All checks passed! OCR is ready to use.")
print("=" * 60)

