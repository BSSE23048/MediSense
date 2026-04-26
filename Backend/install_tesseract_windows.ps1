# Tesseract OCR Installation Script for Windows
# This script helps download and configure Tesseract OCR

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Tesseract OCR Installation for Windows" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Tesseract is already installed
$tesseractPath = "C:\Program Files\Tesseract-OCR\tesseract.exe"
if (Test-Path $tesseractPath) {
    Write-Host "Tesseract OCR is already installed at: $tesseractPath" -ForegroundColor Green
    Write-Host "Version: " -NoNewline
    & $tesseractPath --version
    exit 0
}

Write-Host "Tesseract OCR not found. Please follow these steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "STEP 1: Download Tesseract OCR" -ForegroundColor Cyan
Write-Host "--------------------------------" -ForegroundColor Cyan
Write-Host "1. Visit: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
Write-Host "2. Download the latest Windows installer (tesseract-ocr-w64-setup-*.exe)" -ForegroundColor White
Write-Host "   Direct link: https://digi.bib.uni-mannheim.de/tesseract/" -ForegroundColor White
Write-Host ""
Write-Host "STEP 2: Install Tesseract OCR" -ForegroundColor Cyan
Write-Host "----------------------------" -ForegroundColor Cyan
Write-Host "1. Run the downloaded installer" -ForegroundColor White
Write-Host "2. Install to default location: C:\Program Files\Tesseract-OCR" -ForegroundColor White
Write-Host "3. Make sure to select 'English' language data during installation" -ForegroundColor White
Write-Host ""
Write-Host "STEP 3: Verify Installation" -ForegroundColor Cyan
Write-Host "---------------------------" -ForegroundColor Cyan
Write-Host "After installation, run this script again to verify." -ForegroundColor White
Write-Host ""
Write-Host "STEP 4: Configure Environment (Optional)" -ForegroundColor Cyan
Write-Host "----------------------------------------" -ForegroundColor Cyan
Write-Host "If Tesseract is not in PATH, add to your .env file:" -ForegroundColor White
Write-Host "TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe" -ForegroundColor Yellow
Write-Host ""

# Try to open the download page
$response = Read-Host "Would you like to open the download page in your browser? (Y/N)"
if ($response -eq 'Y' -or $response -eq 'y') {
    Start-Process "https://github.com/UB-Mannheim/tesseract/wiki"
}

Write-Host ""
Write-Host "After installation, update your .env file with:" -ForegroundColor Green
Write-Host "TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe" -ForegroundColor Yellow

