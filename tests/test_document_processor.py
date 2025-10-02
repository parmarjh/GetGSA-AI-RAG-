import pytest
import asyncio
from backend.services.document_processor import DocumentProcessor
from backend.models.document_models import Document
from datetime import datetime

class TestDocumentProcessor:
    """Test document processing functionality"""
    
    def setup_method(self):
        self.processor = DocumentProcessor()
    
    @pytest.mark.asyncio
    async def test_missing_uei_extraction(self):
        """Test that missing UEI is properly flagged (R1)"""
        # Document without UEI
        doc_text = """
        Company Profile:
        Acme Robotics LLC
        DUNS: 123456789
        NAICS: 541511
        POC: Jane Smith, jane@acme.co, (415) 555-0100
        SAM.gov: registered
        """
        
        document = Document(
            name="test.txt",
            type_hint="profile",
            text=doc_text,
            redacted_text=doc_text,
            created_at=datetime.now()
        )
        
        result = await self.processor.process_documents([document])
        
        # Should not find UEI
        assert result['uei'] is None
        assert result['duns'] == '123456789'
        assert result['sam_status'] == 'registered'
    
    @pytest.mark.asyncio
    async def test_past_performance_threshold(self):
        """Test past performance threshold detection (R3)"""
        # Document with past performance below $25,000 threshold
        doc_text = """
        Past Performance (PP-1):
        Customer: City of Palo Verde
        Contract: Website modernization
        Value: $18,000
        Period: 07/2023 - 03/2024
        Contact: John Roe, cio@pverde.gov
        """
        
        document = Document(
            name="pp.txt",
            type_hint="past_performance",
            text=doc_text,
            redacted_text=doc_text,
            created_at=datetime.now()
        )
        
        result = await self.processor.process_documents([document])
        
        # Should extract past performance
        assert len(result['past_performance']) == 1
        assert result['past_performance'][0]['value'] == '$18,000'
        assert result['past_performance'][0]['customer'] == 'City of Palo Verde'
    
    @pytest.mark.asyncio
    async def test_naics_sin_mapping(self):
        """Test NAICS to SIN mapping with deduplication (R2)"""
        # Document with multiple NAICS codes
        doc_text = """
        Company Profile:
        UEI: ABC123DEF456
        DUNS: 123456789
        NAICS: 541511, 541512, 541611
        POC: Jane Smith, jane@acme.co, (415) 555-0100
        SAM.gov: registered
        """
        
        document = Document(
            name="test.txt",
            type_hint="profile",
            text=doc_text,
            redacted_text=doc_text,
            created_at=datetime.now()
        )
        
        result = await self.processor.process_documents([document])
        
        # Should extract all NAICS codes
        assert '541511' in result['naics_codes']
        assert '541512' in result['naics_codes']
        assert '541611' in result['naics_codes']
        assert len(result['naics_codes']) == 3
    
    @pytest.mark.asyncio
    async def test_pii_redaction(self):
        """Test PII redaction for emails and phones (R5)"""
        # Document with PII
        doc_text = """
        Company Profile:
        UEI: ABC123DEF456
        DUNS: 123456789
        POC: Jane Smith, jane@acme.co, (415) 555-0100
        Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
        """
        
        document = Document(
            name="test.txt",
            type_hint="profile",
            text=doc_text,
            redacted_text=doc_text,  # This would be redacted in real usage
            created_at=datetime.now()
        )
        
        result = await self.processor.process_documents([document])
        
        # Should extract contact info
        assert result['primary_contact']['email'] == 'jane@acme.co'
        assert result['primary_contact']['phone'] == '(415) 555-0100'
    
    def test_uei_validation(self):
        """Test UEI validation"""
        assert self.processor.validate_uei('ABC123DEF456') == True
        assert self.processor.validate_uei('ABC123DEF45') == False  # Too short
        assert self.processor.validate_uei('ABC123DEF4567') == False  # Too long
        assert self.processor.validate_uei('ABC123DEF45!') == False  # Invalid char
    
    def test_duns_validation(self):
        """Test DUNS validation"""
        assert self.processor.validate_duns('123456789') == True
        assert self.processor.validate_duns('12345678') == False  # Too short
        assert self.processor.validate_duns('1234567890') == False  # Too long
        assert self.processor.validate_duns('12345678a') == False  # Invalid char
    
    def test_naics_validation(self):
        """Test NAICS validation"""
        assert self.processor.validate_naics('541511') == True
        assert self.processor.validate_naics('54151') == False  # Too short
        assert self.processor.validate_naics('5415111') == False  # Too long
        assert self.processor.validate_naics('54151a') == False  # Invalid char
