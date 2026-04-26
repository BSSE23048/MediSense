"""
Test script for OCR + Summarization workflow
Tests OCR extraction from medical report image and then summarizes it
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_ocr_and_summarize():
    """Test OCR extraction and medical report summarization"""
    print("=" * 70)
    print("Testing MediSense AI - OCR + Summarization Workflow")
    print("=" * 70)
    print()
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("   Please add your Gemini API key to Backend/.env")
        return False
    
    print("✓ GEMINI_API_KEY found")
    print()
    
    # Check if image exists
    image_path = os.path.join(os.path.dirname(__file__), 'uploads', 'Medical-Reports-of-Patients.png')
    
    if not os.path.exists(image_path):
        print(f"❌ ERROR: Image not found at: {image_path}")
        print("   Please ensure the image file exists in the uploads folder")
        return False
    
    print(f"✓ Found test image: {os.path.basename(image_path)}")
    print()
    
    try:
        # Step 1: Test OCR Service
        print("=" * 70)
        print("STEP 1: Testing OCR Text Extraction")
        print("=" * 70)
        print()
        
        from services.ocr_service import OCRService
        
        print("1. Initializing OCR Service...")
        ocr_service = OCRService()
        print(f"   ✓ OCR Service initialized (Method: {ocr_service.ocr_method})")
        print()
        
        print("2. Extracting text from image...")
        print(f"   Processing: {os.path.basename(image_path)}")
        print("   This may take a moment...")
        print()
        
        try:
            extracted_text, confidence = ocr_service.extract_text_from_image(image_path)
            
            print(f"   ✓ Text extraction completed!")
            print(f"   ✓ Confidence score: {confidence:.2%}")
            print()
            
            # Display extracted text preview
            text_preview = extracted_text[:200] if len(extracted_text) > 200 else extracted_text
            print("   Extracted Text Preview:")
            print("   " + "-" * 66)
            print(f"   {text_preview}...")
            if len(extracted_text) > 200:
                print(f"   ... ({len(extracted_text) - 200} more characters)")
            print()
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                print("   ⚠️  Warning: Very little text extracted. Image quality may be low.")
                print()
            
        except Exception as e:
            print(f"   ❌ OCR Extraction failed: {str(e)}")
            print("   Possible causes:")
            print("   - Tesseract OCR not installed or not in PATH")
            print("   - Image file is corrupted")
            print("   - Image quality is too low")
            return False
        
        # Step 2: Test Summarization
        print("=" * 70)
        print("STEP 2: Testing Medical Report Summarization")
        print("=" * 70)
        print()
        
        from services.llm_service import LLMService
        
        print("1. Initializing LLM Service...")
        llm_service = LLMService()
        print(f"   ✓ LLM Service initialized (Provider: {llm_service.provider})")
        if hasattr(llm_service, 'use_direct_api') and llm_service.use_direct_api:
            print("   ✓ Using direct Google Generative AI API")
        print()
        
        print("2. Summarizing extracted medical report...")
        print("   This may take 10-30 seconds...")
        print()
        
        try:
            result = llm_service.summarize_medical_report(extracted_text)
            
            print("   ✓ Summarization completed successfully!")
            print()
            
            # Display results
            print("=" * 70)
            print("SUMMARY RESULTS")
            print("=" * 70)
            print()
            
            print("📋 Patient-Friendly Summary:")
            print("-" * 70)
            patient_summary = result.get('patient_summary', 'N/A')
            # Wrap text for better display
            words = patient_summary.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) < 70:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            for line in lines:
                print(f"   {line}")
            print()
            
            print("👨‍⚕️ Doctor-Focused Summary:")
            print("-" * 70)
            doctor_summary = result.get('doctor_summary', 'N/A')
            words = doctor_summary.split()
            lines = []
            current_line = ""
            for word in words:
                if len(current_line + word) < 70:
                    current_line += word + " "
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            for line in lines:
                print(f"   {line}")
            print()
            
            print("🔍 Key Findings:")
            print("-" * 70)
            key_findings = result.get('key_findings', [])
            if key_findings:
                for i, finding in enumerate(key_findings, 1):
                    print(f"   {i}. {finding}")
            else:
                print("   No key findings extracted")
            print()
            
            print("💊 Medications:")
            print("-" * 70)
            medications = result.get('medications', [])
            if medications:
                for i, med in enumerate(medications, 1):
                    print(f"   {i}. {med}")
            else:
                print("   No medications found")
            print()
            
            print("⚠️  Critical Warnings:")
            print("-" * 70)
            warnings = result.get('critical_warnings', [])
            if warnings:
                for i, warning in enumerate(warnings, 1):
                    print(f"   {i}. {warning}")
            else:
                print("   No critical warnings")
            print()
            
            print("📅 Follow-up Recommendations:")
            print("-" * 70)
            follow_up = result.get('follow_up', 'N/A')
            print(f"   {follow_up}")
            print()
            
            print("=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            print()
            print("OCR + Summarization workflow is working correctly!")
            print("You can now use the /api/ocr and /api/summarize endpoints.")
            print()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Summarization failed: {str(e)}")
            print("   Possible causes:")
            print("   - API key is invalid or expired")
            print("   - Internet connection issues")
            print("   - Model name is incorrect")
            print("   - API quota exceeded")
            return False
        
    except ImportError as e:
        print(f"❌ Import Error: {str(e)}")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ocr_and_summarize()
    sys.exit(0 if success else 1)


