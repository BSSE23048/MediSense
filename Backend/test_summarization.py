"""
Test script for summarization module
Run this to verify LangChain and Gemini integration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_llm_service():
    """Test LLM service initialization and summarization"""
    print("=" * 60)
    print("Testing MediSense AI Summarization Module")
    print("=" * 60)
    print()
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY not found in .env file")
        print("   Please add your Gemini API key to Backend/.env")
        return False
    
    print("✓ GEMINI_API_KEY found")
    print()
    
    # Test LLM Service
    try:
        print("1. Testing LLM Service initialization...")
        from services.llm_service import LLMService
        
        llm_service = LLMService()
        print("   ✓ LLM Service initialized successfully")
        print(f"   ✓ Provider: {llm_service.provider}")
        print()
        
        # Test summarization
        print("2. Testing medical report summarization...")
        sample_text = """
        PATIENT: John Doe
        DATE: 2024-01-15
        
        DIAGNOSIS: Type 2 Diabetes Mellitus
        
        LAB RESULTS:
        - Fasting Blood Glucose: 126 mg/dL (Elevated)
        - HbA1c: 7.2% (Above normal range)
        - Total Cholesterol: 210 mg/dL
        - LDL: 140 mg/dL (Elevated)
        
        MEDICATIONS PRESCRIBED:
        - Metformin 500mg, twice daily with meals
        - Lisinopril 10mg, once daily
        
        RECOMMENDATIONS:
        - Monitor blood glucose levels daily
        - Follow diabetic diet plan
        - Exercise 30 minutes daily
        - Follow-up appointment in 3 months
        - Annual eye examination recommended
        """
        
        print("   Processing sample medical report...")
        result = llm_service.summarize_medical_report(sample_text)
        
        print("   ✓ Summarization completed successfully!")
        print()
        print("   Results:")
        print("   " + "-" * 56)
        print(f"   Patient Summary: {result.get('patient_summary', 'N/A')[:100]}...")
        print(f"   Doctor Summary: {result.get('doctor_summary', 'N/A')[:100]}...")
        print(f"   Key Findings: {len(result.get('key_findings', []))} items")
        print(f"   Medications: {len(result.get('medications', []))} items")
        print(f"   Warnings: {len(result.get('critical_warnings', []))} items")
        print()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print()
        print("Summarization module is working correctly!")
        print("You can now use the /api/summarize endpoint.")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import Error: {str(e)}")
        print("   Please install dependencies: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print("   Check your API key and internet connection")
        return False

if __name__ == '__main__':
    success = test_llm_service()
    sys.exit(0 if success else 1)

