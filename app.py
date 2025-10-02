import streamlit as st
import json
import uuid
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.services.document_processor import DocumentProcessor
from backend.services.rag_service import RAGService
from backend.services.ai_service import AIService
from backend.services.pii_redactor import PIIRedactor
from backend.models.document_models import Document, ParsedData

# Page configuration
st.set_page_config(
    page_title="GetGSA - AI + RAG Document Analysis",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
@st.cache_resource
def get_services():
    """Initialize and cache services"""
    return {
        'document_processor': DocumentProcessor(),
        'rag_service': RAGService(),
        'ai_service': AIService(),
        'pii_redactor': PIIRedactor()
    }

# File uploader widget
def file_uploader_widget():
    """Create a file uploader widget"""
    uploaded_files = st.file_uploader(
        "Upload Document(s)",
        type=["txt", "pdf", "doc", "docx"],
        accept_multiple_files=True,
        help="Upload your documents here. Supported formats: TXT, PDF, DOC, DOCX"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_details = {
                "FileName": uploaded_file.name,
                "FileType": uploaded_file.type,
                "FileSize": f"{uploaded_file.size / 1024:.2f} KB"
            }
            st.write("File Details:", file_details)
            
            # Read and process the file content
            if uploaded_file.type == "text/plain":
                raw_text = uploaded_file.read().decode("utf-8")
            else:
                # For other file types, you might need additional processing
                raw_text = "File content processing not implemented for this type yet"
            
            with st.expander("View Document Content"):
                st.text(raw_text)
            
            return raw_text
    
    return None

# Sample documents
SAMPLE_DOCUMENTS = {
    "Complete Submission": """Company Profile (A):
Acme Robotics LLC
UEI: ABC123DEF456
DUNS: 123456789
NAICS: 541511, 541512
POC: Jane Smith, jane@acme.co, (415) 555-0100
Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
SAM.gov: registered

Past Performance (PP-1):
Customer: City of Palo Verde
Contract: Website modernization
Value: $18,000
Period: 07/2023 - 03/2024
Contact: John Roe, cio@pverde.gov

Past Performance (PP-2):
Customer: State of Fremont
Contract: Data migration & support
Value: $82,500
Period: 10/2022 - 02/2024
Contact: sarah.lee@fremont.gov

Pricing Sheet (text; simplified):
Labor Category, Rate, Unit
Senior Developer, 185, Hour
Project Manager, 165, Hour""",

    "Incomplete Submission": """Company Profile (A):
Acme Robotics LLC
UEI: ABC123DEF456
DUNS: 123456789
NAICS: 541511, 541512
POC: Jane Smith, jane@acme.co, (415) 555-0100
Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
SAM.gov: pending

Past Performance (PP-1):
Customer: City of Palo Verde
Contract: Website modernization
Value: $18,000
Period: 07/2023 - 03/2024
Contact: John Roe, cio@pverde.gov

Pricing Sheet (text; simplified):
Labor Category, Rate, Unit
Senior Developer, 185, Hour
Project Manager, 165, Hour""",

    "Minimal Submission": """Company Profile (A):
Acme Robotics LLC
UEI: ABC123DEF456
DUNS: 123456789
NAICS: 541511
POC: Jane Smith, jane@acme.co, (415) 555-0100
Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
SAM.gov: registered

Past Performance (PP-1):
Customer: City of Palo Verde
Contract: Website modernization
Value: $15,000
Period: 07/2023 - 03/2024
Contact: John Roe, cio@pverde.gov"""
}

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("📋 GetGSA - AI + RAG Document Analysis")
    st.markdown("Upload and analyze GSA onboarding documents with AI-powered compliance checking")
    
    # Add the file uploader section
    st.header("📤 Document Upload")
    uploaded_content = file_uploader_widget()
    
    # Initialize services
    services = get_services()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Sample Documents")
        selected_sample = st.selectbox(
            "Choose a sample document:",
            ["None"] + list(SAMPLE_DOCUMENTS.keys())
        )
        
        if selected_sample != "None":
            st.text_area(
                "Sample Document Preview:",
                SAMPLE_DOCUMENTS[selected_sample],
                height=200,
                disabled=True
            )
        
        st.header("⚙️ Settings")
        show_raw_data = st.checkbox("Show Raw Parsed Data", value=False)
        show_citations = st.checkbox("Show Rule Citations", value=True)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Document Input")
        
        # Document input
        document_text = st.text_area(
            "Paste your document text here:",
            height=400,
            placeholder="Paste your GSA document text here or select a sample document from the sidebar..."
        )
        
        # Load sample document
        if selected_sample != "None" and st.button("Load Sample Document"):
            document_text = SAMPLE_DOCUMENTS[selected_sample]
            st.rerun()
        
        # Process buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🔍 Analyze Document", type="primary", disabled=not document_text.strip()):
                with st.spinner("Processing document..."):
                    result = process_document(document_text, services)
                    st.session_state['analysis_result'] = result
        
        with col_btn2:
            if st.button("🧹 Clear"):
                st.session_state.pop('analysis_result', None)
                st.rerun()
    
    with col2:
        st.header("📊 Analysis Results")
        
        if 'analysis_result' in st.session_state:
            display_results(st.session_state['analysis_result'], show_raw_data, show_citations)
        else:
            st.info("👈 Enter document text and click 'Analyze Document' to see results")

def process_document(text: str, services: Dict[str, Any]) -> Dict[str, Any]:
    """Process document and return analysis results"""
    try:
        # Create document object
        document = Document(
            name="document.txt",
            type_hint=None,
            text=text,
            redacted_text=services['pii_redactor'].redact(text),
            created_at=datetime.now()
        )
        
        # Process documents
        parsed_data = asyncio.run(services['document_processor'].process_documents([document]))
        
        # Get relevant rules using RAG
        relevant_rules = asyncio.run(services['rag_service'].get_relevant_rules(parsed_data))
        
        # Generate checklist using AI
        checklist = asyncio.run(services['ai_service'].generate_checklist(parsed_data, relevant_rules))
        
        # Generate brief and client email
        brief = asyncio.run(services['ai_service'].generate_negotiation_brief(parsed_data, checklist, relevant_rules))
        client_email = asyncio.run(services['ai_service'].generate_client_email(parsed_data, checklist))
        
        return {
            'parsed': parsed_data,
            'checklist': checklist,
            'brief': brief,
            'client_email': client_email,
            'citations': relevant_rules,
            'request_id': str(uuid.uuid4())
        }
    
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")
        return None

def display_results(result: Dict[str, Any], show_raw_data: bool, show_citations: bool):
    """Display analysis results"""
    if not result:
        return
    
    # Overall status
    status = result['checklist']['overall_status']
    if status == 'pass':
        st.success("✅ All Requirements Met")
    else:
        st.error("❌ Issues Found")
    
    # Checklist
    st.subheader("📋 Compliance Checklist")
    
    for item in result['checklist']['items']:
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if item['ok']:
                st.success("✅")
            else:
                st.error("❌")
        
        with col2:
            st.write(f"**{get_checklist_title(item)}**")
            if item['evidence']:
                st.caption(item['evidence'])
            if item['rule_ids'] and show_citations:
                rule_citations = " ".join([f"`{rule_id}`" for rule_id in item['rule_ids']])
                st.caption(f"Rules: {rule_citations}")
    
    # Extracted data
    st.subheader("📊 Extracted Data")
    
    parsed = result['parsed']
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        if parsed.get('uei'):
            st.write(f"**UEI:** {parsed['uei']}")
        if parsed.get('duns'):
            st.write(f"**DUNS:** {parsed['duns']}")
        if parsed.get('naics_codes'):
            st.write(f"**NAICS:** {', '.join(parsed['naics_codes'])}")
        if parsed.get('sam_status'):
            st.write(f"**SAM Status:** {parsed['sam_status']}")
    
    with col2:
        if parsed.get('primary_contact'):
            st.write(f"**Primary Contact:** {parsed['primary_contact']['email']}")
            st.write(f"**Phone:** {parsed['primary_contact']['phone']}")
    
    # Past performance
    if parsed.get('past_performance'):
        st.write("**Past Performance:**")
        for pp in parsed['past_performance']:
            st.write(f"- {pp.get('customer', 'Unknown')}: ${pp.get('value', 'N/A')} ({pp.get('period', 'N/A')})")
    
    # Pricing data
    if parsed.get('pricing_data'):
        st.write("**Pricing:**")
        for pricing in parsed['pricing_data']:
            st.write(f"- {pricing.get('labor_category', 'Unknown')}: ${pricing.get('rate', 'N/A')}/{pricing.get('unit', 'N/A')}")
    
    # Raw data (if requested)
    if show_raw_data:
        st.subheader("🔍 Raw Parsed Data")
        st.json(parsed)
    
    # Negotiation brief
    st.subheader("📝 Negotiation Prep Brief")
    st.markdown(result['brief'])
    
    # Client email
    st.subheader("📧 Client Email Draft")
    st.text(result['client_email'])
    
    # Rule citations
    if show_citations and result['citations']:
        st.subheader("📚 Rule Citations")
        for citation in result['citations']:
            with st.expander(f"Rule {citation['rule_id']} (Score: {citation['relevance_score']:.2f})"):
                st.write(citation['chunk'])

def get_checklist_title(item: Dict[str, Any]) -> str:
    """Get human-readable title for checklist item"""
    titles = {
        'missing_uei': 'UEI Required',
        'missing_duns': 'DUNS Required',
        'sam_not_active': 'SAM.gov Registration',
        'missing_past_performance': 'Past Performance Required',
        'past_performance_min_value_not_met': 'Past Performance Value',
        'pricing_incomplete': 'Pricing Information'
    }
    return titles.get(item.get('problem'), 'Requirement Check')

if __name__ == "__main__":
    main()
