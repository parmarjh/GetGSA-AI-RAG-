import pytest
import asyncio
from backend.services.ai_service import AIService

class TestAIService:
    """Test AI service functionality"""
    
    def setup_method(self):
        self.ai_service = AIService()
    
    @pytest.mark.asyncio
    async def test_document_classification(self):
        """Test document classification"""
        # Test profile document
        profile_text = "UEI: ABC123DEF456, DUNS: 123456789, SAM.gov: registered"
        classification = await self.ai_service.classify_document(profile_text, None)
        assert classification == "profile"
        
        # Test past performance document
        pp_text = "Past Performance: Customer: City of Palo Verde, Value: $30,000"
        classification = await self.ai_service.classify_document(pp_text, None)
        assert classification == "past_performance"
        
        # Test pricing document
        pricing_text = "Labor Category: Developer, Rate: 150, Unit: Hour"
        classification = await self.ai_service.classify_document(pricing_text, None)
        assert classification == "pricing"
        
        # Test unknown document
        unknown_text = "This is just some random text"
        classification = await self.ai_service.classify_document(unknown_text, None)
        assert classification == "unknown"
    
    @pytest.mark.asyncio
    async def test_checklist_generation_missing_uei(self):
        """Test checklist generation for missing UEI (R1)"""
        parsed_data = {
            'uei': None,
            'duns': '123456789',
            'sam_status': 'registered',
            'past_performance': [{'value': '$30,000'}],
            'pricing_data': [{'labor_category': 'Developer', 'rate': '150', 'unit': 'Hour'}]
        }
        
        relevant_rules = [{'rule_id': 'R1', 'chunk': 'Identity & Registry requirements', 'relevance_score': 0.8}]
        
        checklist = await self.ai_service.generate_checklist(parsed_data, relevant_rules)
        
        # Should flag missing UEI
        uei_item = next((item for item in checklist['items'] if item['problem'] == 'missing_uei'), None)
        assert uei_item is not None
        assert uei_item['required'] == True
        assert uei_item['ok'] == False
        assert 'R1' in uei_item['rule_ids']
    
    @pytest.mark.asyncio
    async def test_checklist_generation_past_performance_threshold(self):
        """Test checklist generation for past performance threshold (R3)"""
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'sam_status': 'registered',
            'past_performance': [{'value': '$18,000'}],  # Below $25,000 threshold
            'pricing_data': [{'labor_category': 'Developer', 'rate': '150', 'unit': 'Hour'}]
        }
        
        relevant_rules = [{'rule_id': 'R3', 'chunk': 'Past Performance requirements', 'relevance_score': 0.8}]
        
        checklist = await self.ai_service.generate_checklist(parsed_data, relevant_rules)
        
        # Should flag past performance threshold
        pp_item = next((item for item in checklist['items'] if item['problem'] == 'past_performance_min_value_not_met'), None)
        assert pp_item is not None
        assert pp_item['required'] == True
        assert pp_item['ok'] == False
        assert 'R3' in pp_item['rule_ids']
    
    @pytest.mark.asyncio
    async def test_checklist_generation_complete_submission(self):
        """Test checklist generation for complete submission"""
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'sam_status': 'registered',
            'past_performance': [{'value': '$30,000'}],  # Above $25,000 threshold
            'pricing_data': [{'labor_category': 'Developer', 'rate': '150', 'unit': 'Hour'}]
        }
        
        relevant_rules = [
            {'rule_id': 'R1', 'chunk': 'Identity & Registry requirements', 'relevance_score': 0.8},
            {'rule_id': 'R3', 'chunk': 'Past Performance requirements', 'relevance_score': 0.7},
            {'rule_id': 'R4', 'chunk': 'Pricing requirements', 'relevance_score': 0.6}
        ]
        
        checklist = await self.ai_service.generate_checklist(parsed_data, relevant_rules)
        
        # Should pass all requirements
        assert checklist['overall_status'] == 'pass'
        
        # All items should be ok
        for item in checklist['items']:
            assert item['ok'] == True
            assert item['problem'] is None
    
    @pytest.mark.asyncio
    async def test_negotiation_brief_generation(self):
        """Test negotiation brief generation"""
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'sam_status': 'registered',
            'past_performance': [{'value': '$18,000'}],
            'pricing_data': [{'labor_category': 'Developer', 'rate': '150', 'unit': 'Hour'}]
        }
        
        checklist = {
            'items': [
                {'problem': 'past_performance_min_value_not_met', 'rule_ids': ['R3']}
            ],
            'overall_status': 'fail'
        }
        
        relevant_rules = [{'rule_id': 'R3', 'chunk': 'Past Performance requirements', 'relevance_score': 0.8}]
        
        brief = await self.ai_service.generate_negotiation_brief(parsed_data, checklist, relevant_rules)
        
        # Should mention the issue
        assert 'past performance' in brief.lower()
        assert 'R3' in brief
        assert 'negotiation' in brief.lower()
    
    @pytest.mark.asyncio
    async def test_client_email_generation(self):
        """Test client email generation"""
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'sam_status': 'registered',
            'past_performance': [{'value': '$18,000'}],
            'pricing_data': [{'labor_category': 'Developer', 'rate': '150', 'unit': 'Hour'}]
        }
        
        checklist = {
            'items': [
                {'problem': 'past_performance_min_value_not_met', 'rule_ids': ['R3']}
            ],
            'overall_status': 'fail'
        }
        
        email = await self.ai_service.generate_client_email(parsed_data, checklist)
        
        # Should be a proper email format
        assert 'Subject:' in email
        assert 'Dear Client,' in email
        assert 'Thank you' in email
        assert 'Best regards,' in email
        
        # Should mention the issue
        assert 'past performance' in email.lower() or '$25,000' in email
    
    @pytest.mark.asyncio
    async def test_abstention_handling(self):
        """Test abstention when confidence is low"""
        # Test with ambiguous text
        ambiguous_text = "Some random text that doesn't clearly indicate document type"
        classification = await self.ai_service.classify_document(ambiguous_text, None)
        
        # Should return 'unknown' for ambiguous content
        assert classification == "unknown"
    
    @pytest.mark.asyncio
    async def test_type_hint_override(self):
        """Test that type hint overrides classification"""
        text = "Some random text"
        classification = await self.ai_service.classify_document(text, "profile")
        
        # Should use type hint
        assert classification == "profile"
