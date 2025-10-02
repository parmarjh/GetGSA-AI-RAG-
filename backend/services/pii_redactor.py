import re
from typing import Dict, Any

class PIIRedactor:
    """PII redaction service for emails and phone numbers"""
    
    def __init__(self):
        # Email regex pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # Phone number regex patterns (various formats)
        self.phone_patterns = [
            re.compile(r'\(\d{3}\)\s*\d{3}-\d{4}'),  # (415) 555-0100
            re.compile(r'\d{3}-\d{3}-\d{4}'),        # 415-555-0100
            re.compile(r'\d{3}\.\d{3}\.\d{4}'),      # 415.555.0100
            re.compile(r'\d{10}'),                    # 4155550100
            re.compile(r'\+1\s*\d{3}\s*\d{3}\s*\d{4}'), # +1 415 555 0100
        ]
    
    def redact(self, text: str) -> str:
        """Redact PII from text"""
        redacted_text = text
        
        # Redact emails
        redacted_text = self.email_pattern.sub('[EMAIL_REDACTED]', redacted_text)
        
        # Redact phone numbers
        for pattern in self.phone_patterns:
            redacted_text = pattern.sub('[PHONE_REDACTED]', redacted_text)
        
        return redacted_text
    
    def extract_emails(self, text: str) -> list:
        """Extract emails from text for parsing"""
        return self.email_pattern.findall(text)
    
    def extract_phones(self, text: str) -> list:
        """Extract phone numbers from text for parsing"""
        phones = []
        for pattern in self.phone_patterns:
            phones.extend(pattern.findall(text))
        return phones
