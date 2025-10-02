#!/usr/bin/env python3
"""
Test script to verify the GetGSA app components work
"""
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test backend imports
        from backend.services.document_processor import DocumentProcessor
        from backend.services.rag_service import RAGService
        from backend.services.ai_service import AIService
        from backend.services.pii_redactor import PIIRedactor
        from backend.models.document_models import Document
        
        print("[OK] Backend imports successful")
        
        # Test Streamlit
        import streamlit as st
        print("[OK] Streamlit import successful")
        
        # Test other dependencies
        import numpy as np
        import pandas as pd
        from sklearn.feature_extraction.text import TfidfVectorizer
        print("[OK] All dependencies imported successfully")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_services():
    """Test that services can be initialized"""
    try:
        print("\nTesting service initialization...")
        
        from backend.services.document_processor import DocumentProcessor
        from backend.services.rag_service import RAGService
        from backend.services.ai_service import AIService
        from backend.services.pii_redactor import PIIRedactor
        
        # Initialize services
        processor = DocumentProcessor()
        rag = RAGService()
        ai = AIService()
        redactor = PIIRedactor()
        
        print("[OK] All services initialized successfully")
        
        # Test PII redaction
        test_text = "Contact: jane@example.com, (555) 123-4567"
        redacted = redactor.redact(test_text)
        print(f"[OK] PII redaction working: {redacted}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Service initialization error: {e}")
        return False

def main():
    """Run all tests"""
    print("GetGSA App Component Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test services
    services_ok = test_services()
    
    print("\n" + "=" * 40)
    if imports_ok and services_ok:
        print("[SUCCESS] All tests passed! The app should work correctly.")
        print("\nTo run the app, try:")
        print("1. python run_app.py")
        print("2. python -m streamlit run app.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print("[FAILED] Some tests failed. Check the errors above.")
    
    return imports_ok and services_ok

if __name__ == "__main__":
    main()
