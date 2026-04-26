# Tesseract OCR Setup Guide for Windows

## Quick Installation Steps

### Method 1: Automatic Download (Recommended)

1. **Download Tesseract OCR:**

   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Or direct download: https://digi.bib.uni-mannheim.de/tesseract/
   - Download the latest `tesseract-ocr-w64-setup-*.exe` file

2. **Install Tesseract:**

   - Run the downloaded installer
   - **Important:** Install to default location: `C:\Program Files\Tesseract-OCR`
   - During installation, make sure to select **English** language data
   - Complete the installation

3. **Verify Installation:**

   - Open Command Prompt or PowerShell
   - Run: `tesseract --version`
   - You should see version information

4. **Configure Backend (if needed):**
   - If Tesseract is installed in default location, the backend will auto-detect it
   - If installed elsewhere, add to your `.env` file:
     ```
     TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
     ```

### Method 2: Using PowerShell Script

Run the installation helper script:

```powershell
cd Backend
powershell -ExecutionPolicy Bypass -File install_tesseract_windows.ps1
```

## Troubleshooting

### Tesseract Not Found Error

**Solution 1:** Add to PATH

1. Open "Environment Variables" (search in Start menu)
2. Edit "Path" variable
3. Add: `C:\Program Files\Tesseract-OCR`
4. Restart terminal/IDE

**Solution 2:** Set in .env file
Add this line to your `Backend/.env` file:

```
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Testing Tesseract Installation

Test if Tesseract works:

```bash
# In Command Prompt or PowerShell
tesseract --version
```

Expected output:

```
tesseract 5.x.x
 leptonica-1.x.x
  libgif x.x.x
  ...
```

## Alternative: Use EasyOCR (No Installation Required)

If you don't want to install Tesseract, you can use EasyOCR instead:

1. In your `.env` file, set:

   ```
   USE_EASYOCR=true
   ```

2. EasyOCR will be automatically downloaded on first use (requires internet)

**Note:** EasyOCR is slower but doesn't require system installation.

## Verification

After installation, test the OCR service:

```python
# Test script (test_ocr.py)
from services.ocr_service import OCRService

ocr = OCRService()
print("OCR Service initialized successfully!")
```

Run: `python test_ocr.py`

If you see "OCR Service initialized successfully!", you're all set!
