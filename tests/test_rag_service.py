import pytest
import asyncio
from backend.services.rag_service import RAGService

class TestRAGService:
    """Test RAG service functionality"""
    
    def setup_method(self):
        self.rag_service = RAGService()
    
    @pytest.mark.asyncio
    async def test_rag_sanity_check(self):
        """Test that RAG service can retrieve relevant rules"""
        # Test data with UEI, DUNS, and past performance
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'naics_codes': ['541511', '541512'],
            'past_performance': [{'value': '$30,000'}],
            'pricing_data': [{'labor_category': 'Developer', 'rate': '150', 'unit': 'Hour'}]
        }
        
        relevant_rules = await self.rag_service.get_relevant_rules(parsed_data)
        
        # Should find relevant rules
        assert len(relevant_rules) > 0
        
        # Should include R1 (Identity & Registry) for UEI/DUNS
        rule_ids = [rule['rule_id'] for rule in relevant_rules]
        assert 'R1' in rule_ids
        
        # Should include R3 (Past Performance) for past performance data
        assert 'R3' in rule_ids
        
        # Should include R4 (Pricing) for pricing data
        assert 'R4' in rule_ids
    
    @pytest.mark.asyncio
    async def test_naics_mapping(self):
        """Test NAICS to SIN mapping"""
        # Test specific mappings from R2
        assert self.rag_service.get_naics_mapping('541511') == '54151S'
        assert self.rag_service.get_naics_mapping('541512') == '54151S'
        assert self.rag_service.get_naics_mapping('541611') == '541611'
        assert self.rag_service.get_naics_mapping('518210') == '518210C'
        
        # Test unmapped NAICS code
        assert self.rag_service.get_naics_mapping('999999') == '999999'
    
    @pytest.mark.asyncio
    async def test_rule_retrieval_by_id(self):
        """Test getting specific rules by ID"""
        # Test R1 rule
        r1_rule = self.rag_service.get_rule_by_id('R1')
        assert r1_rule['title'] == 'Identity & Registry'
        assert 'UEI' in r1_rule['content']
        assert 'DUNS' in r1_rule['content']
        
        # Test R3 rule
        r3_rule = self.rag_service.get_rule_by_id('R3')
        assert r3_rule['title'] == 'Past Performance'
        assert '$25,000' in r3_rule['content']
        
        # Test non-existent rule
        non_existent = self.rag_service.get_rule_by_id('R99')
        assert non_existent == {}
    
    @pytest.mark.asyncio
    async def test_relevance_scoring(self):
        """Test that relevance scoring works correctly"""
        # Test with minimal data
        minimal_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789'
        }
        
        relevant_rules = await self.rag_service.get_relevant_rules(minimal_data)
        
        # Should find R1 as most relevant
        assert len(relevant_rules) > 0
        assert relevant_rules[0]['rule_id'] == 'R1'
        assert relevant_rules[0]['relevance_score'] > 0.3
    
    @pytest.mark.asyncio
    async def test_empty_data_handling(self):
        """Test handling of empty parsed data"""
        empty_data = {}
        
        relevant_rules = await self.rag_service.get_relevant_rules(empty_data)
        
        # Should return empty list or low relevance rules
        assert isinstance(relevant_rules, list)
    
    @pytest.mark.asyncio
    async def test_vector_index_consistency(self):
        """Test that vector index is consistent"""
        # Check that all rules are indexed
        assert len(self.rag_service.rule_texts) == 5  # R1-R5
        assert len(self.rag_service.rule_ids) == 5
        assert len(self.rag_service.embeddings) == 5
        
        # Check that embeddings have correct dimensions
        assert self.rag_service.embeddings.shape[1] == 384  # all-MiniLM-L6-v2 embedding size
