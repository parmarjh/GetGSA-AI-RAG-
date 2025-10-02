import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models.document_models import Document, ParsedData

class DocumentProcessor:
    """Document processing service for field extraction"""
    
    def __init__(self):
        # Regex patterns for field extraction
        self.patterns = {
            'uei': re.compile(r'UEI:\s*([A-Z0-9]{12})', re.IGNORECASE),
            'duns': re.compile(r'DUNS:\s*(\d{9})', re.IGNORECASE),
            'naics': re.compile(r'NAICS:\s*([0-9,\s]+)', re.IGNORECASE),
            'sam_status': re.compile(r'SAM\.gov:\s*([a-zA-Z\s]+)', re.IGNORECASE),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
            'past_performance_customer': re.compile(r'Customer:\s*([^\n]+)', re.IGNORECASE),
            'past_performance_contract': re.compile(r'Contract:\s*([^\n]+)', re.IGNORECASE),
            'past_performance_value': re.compile(r'Value:\s*([^\n]+)', re.IGNORECASE),
            'past_performance_period': re.compile(r'Period:\s*([^\n]+)', re.IGNORECASE),
            'past_performance_contact': re.compile(r'Contact:\s*([^\n]+)', re.IGNORECASE),
        }
    
    async def process_documents(self, documents: List[Document]) -> Dict[str, Any]:
        """Process documents and extract key fields"""
        parsed_data = {
            'uei': None,
            'duns': None,
            'naics_codes': [],
            'sam_status': None,
            'primary_contact': None,
            'past_performance': [],
            'pricing_data': [],
            'document_types': []
        }
        
        for document in documents:
            # Classify document type
            doc_type = await self._classify_document(document.text, document.type_hint)
            parsed_data['document_types'].append(doc_type)
            
            # Extract fields based on document type
            if doc_type == 'profile':
                self._extract_profile_fields(document.text, parsed_data)
            elif doc_type == 'past_performance':
                self._extract_past_performance_fields(document.text, parsed_data)
            elif doc_type == 'pricing':
                self._extract_pricing_fields(document.text, parsed_data)
        
        return parsed_data
    
    async def _classify_document(self, text: str, type_hint: Optional[str] = None) -> str:
        """Classify document type"""
        if type_hint:
            return type_hint
        
        text_lower = text.lower()
        
        # Check for profile indicators
        if any(keyword in text_lower for keyword in ['uei:', 'duns:', 'sam.gov', 'primary contact', 'poc:']):
            return 'profile'
        
        # Check for past performance indicators
        if any(keyword in text_lower for keyword in ['past performance', 'customer:', 'contract:', 'value:', 'period:']):
            return 'past_performance'
        
        # Check for pricing indicators
        if any(keyword in text_lower for keyword in ['labor category', 'rate', 'pricing', 'hour', 'day']):
            return 'pricing'
        
        return 'unknown'
    
    def _extract_profile_fields(self, text: str, parsed_data: Dict[str, Any]):
        """Extract profile fields from text"""
        # Extract UEI
        uei_match = self.patterns['uei'].search(text)
        if uei_match:
            parsed_data['uei'] = uei_match.group(1)
        
        # Extract DUNS
        duns_match = self.patterns['duns'].search(text)
        if duns_match:
            parsed_data['duns'] = duns_match.group(1)
        
        # Extract NAICS codes
        naics_match = self.patterns['naics'].search(text)
        if naics_match:
            naics_text = naics_match.group(1)
            # Split by comma and clean up
            naics_codes = [code.strip() for code in naics_text.split(',')]
            parsed_data['naics_codes'].extend(naics_codes)
        
        # Extract SAM status
        sam_match = self.patterns['sam_status'].search(text)
        if sam_match:
            parsed_data['sam_status'] = sam_match.group(1).strip()
        
        # Extract primary contact
        emails = self.patterns['email'].findall(text)
        phones = self.patterns['phone'].findall(text)
        
        if emails and phones:
            parsed_data['primary_contact'] = {
                'email': emails[0],
                'phone': phones[0]
            }
    
    def _extract_past_performance_fields(self, text: str, parsed_data: Dict[str, Any]):
        """Extract past performance fields from text"""
        # Split text into sections (assuming each PP is separated)
        sections = text.split('\n\n')
        
        for section in sections:
            if 'customer:' in section.lower() or 'contract:' in section.lower():
                pp_data = {}
                
                # Extract customer
                customer_match = self.patterns['past_performance_customer'].search(section)
                if customer_match:
                    pp_data['customer'] = customer_match.group(1).strip()
                
                # Extract contract
                contract_match = self.patterns['past_performance_contract'].search(section)
                if contract_match:
                    pp_data['contract'] = contract_match.group(1).strip()
                
                # Extract value
                value_match = self.patterns['past_performance_value'].search(section)
                if value_match:
                    pp_data['value'] = value_match.group(1).strip()
                
                # Extract period
                period_match = self.patterns['past_performance_period'].search(section)
                if period_match:
                    pp_data['period'] = period_match.group(1).strip()
                
                # Extract contact
                contact_match = self.patterns['past_performance_contact'].search(section)
                if contact_match:
                    pp_data['contact'] = contact_match.group(1).strip()
                
                if pp_data:
                    parsed_data['past_performance'].append(pp_data)
    
    def _extract_pricing_fields(self, text: str, parsed_data: Dict[str, Any]):
        """Extract pricing fields from text"""
        lines = text.split('\n')
        
        for line in lines:
            # Look for CSV-like format: Labor Category, Rate, Unit
            if ',' in line and any(keyword in line.lower() for keyword in ['labor', 'rate', 'hour', 'day']):
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 3:
                    pricing_item = {
                        'labor_category': parts[0],
                        'rate': parts[1],
                        'unit': parts[2]
                    }
                    parsed_data['pricing_data'].append(pricing_item)
    
    def validate_uei(self, uei: str) -> bool:
        """Validate UEI format (12 characters)"""
        return len(uei) == 12 and uei.isalnum()
    
    def validate_duns(self, duns: str) -> bool:
        """Validate DUNS format (9 digits)"""
        return len(duns) == 9 and duns.isdigit()
    
    def validate_naics(self, naics: str) -> bool:
        """Validate NAICS code format (6 digits)"""
        return len(naics) == 6 and naics.isdigit()
