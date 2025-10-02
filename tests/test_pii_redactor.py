import pytest
from backend.services.pii_redactor import PIIRedactor

class TestPIIRedactor:
    """Test PII redaction functionality"""
    
    def setup_method(self):
        self.redactor = PIIRedactor()
    
    def test_email_redaction(self):
        """Test email redaction"""
        text = "Contact: Jane Smith, jane@acme.co, (415) 555-0100"
        redacted = self.redactor.redact(text)
        
        assert "[EMAIL_REDACTED]" in redacted
        assert "jane@acme.co" not in redacted
        assert "(415) 555-0100" not in redacted  # Phone should also be redacted
    
    def test_phone_redaction(self):
        """Test phone number redaction"""
        text = "Call us at (415) 555-0100 or 415-555-0100"
        redacted = self.redactor.redact(text)
        
        assert "[PHONE_REDACTED]" in redacted
        assert "(415) 555-0100" not in redacted
        assert "415-555-0100" not in redacted
    
    def test_multiple_emails(self):
        """Test multiple email redaction"""
        text = "Emails: jane@acme.co, john@acme.co, support@acme.co"
        redacted = self.redactor.redact(text)
        
        assert redacted.count("[EMAIL_REDACTED]") == 3
        assert "jane@acme.co" not in redacted
        assert "john@acme.co" not in redacted
        assert "support@acme.co" not in redacted
    
    def test_multiple_phones(self):
        """Test multiple phone number redaction"""
        text = "Phones: (415) 555-0100, 415-555-0101, 415.555.0102"
        redacted = self.redactor.redact(text)
        
        assert redacted.count("[PHONE_REDACTED]") == 3
        assert "(415) 555-0100" not in redacted
        assert "415-555-0101" not in redacted
        assert "415.555.0102" not in redacted
    
    def test_email_extraction(self):
        """Test email extraction for parsing"""
        text = "Contact: Jane Smith, jane@acme.co, (415) 555-0100"
        emails = self.redactor.extract_emails(text)
        
        assert "jane@acme.co" in emails
        assert len(emails) == 1
    
    def test_phone_extraction(self):
        """Test phone extraction for parsing"""
        text = "Call us at (415) 555-0100 or 415-555-0101"
        phones = self.redactor.extract_phones(text)
        
        assert "(415) 555-0100" in phones
        assert "415-555-0101" in phones
        assert len(phones) == 2
    
    def test_no_pii_text(self):
        """Test text with no PII"""
        text = "This is a regular document with no personal information."
        redacted = self.redactor.redact(text)
        
        assert redacted == text
        assert "[EMAIL_REDACTED]" not in redacted
        assert "[PHONE_REDACTED]" not in redacted
    
    def test_mixed_content(self):
        """Test mixed content with PII and regular text"""
        text = """
        Company Profile:
        Name: Acme Robotics LLC
        Contact: Jane Smith, jane@acme.co, (415) 555-0100
        Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
        Website: www.acme.com
        """
        
        redacted = self.redactor.redact(text)
        
        # PII should be redacted
        assert "[EMAIL_REDACTED]" in redacted
        assert "[PHONE_REDACTED]" in redacted
        assert "jane@acme.co" not in redacted
        assert "(415) 555-0100" not in redacted
        
        # Regular text should remain
        assert "Acme Robotics LLC" in redacted
        assert "444 West Lake Street" in redacted
        assert "www.acme.com" in redacted
    
    def test_various_phone_formats(self):
        """Test various phone number formats"""
        phone_formats = [
            "(415) 555-0100",
            "415-555-0100", 
            "415.555.0100",
            "4155550100",
            "+1 415 555 0100"
        ]
        
        for phone in phone_formats:
            text = f"Contact: {phone}"
            redacted = self.redactor.redact(text)
            
            assert "[PHONE_REDACTED]" in redacted
            assert phone not in redacted
    
    def test_various_email_formats(self):
        """Test various email formats"""
        email_formats = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.co.uk",
            "user123@example-domain.com"
        ]
        
        for email in email_formats:
            text = f"Contact: {email}"
            redacted = self.redactor.redact(text)
            
            assert "[EMAIL_REDACTED]" in redacted
            assert email not in redacted
