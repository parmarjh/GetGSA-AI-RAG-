import pytest
import asyncio
from backend.services.rag_service import RAGService

class TestRAGSanity:
    """RAG sanity test - test that RAG works correctly when rules are removed"""
    
    def setup_method(self):
        self.rag_service = RAGService()
    
    @pytest.mark.asyncio
    async def test_rag_without_r1_rule(self):
        """Test RAG behavior when R1 rule is removed from index"""
        # Create a modified RAG service without R1
        modified_rag = RAGService()
        
        # Remove R1 from the rules
        if 'R1' in modified_rag.rules:
            del modified_rag.rules['R1']
        
        # Rebuild index without R1
        modified_rag.rule_texts = []
        modified_rag.rule_ids = []
        
        for rule_id, rule_data in modified_rag.rules.items():
            searchable_text = f"{rule_data['title']}: {rule_data['content']}"
            modified_rag.rule_texts.append(searchable_text)
            modified_rag.rule_ids.append(rule_id)
        
        # Generate embeddings
        modified_rag.embeddings = modified_rag.model.encode(modified_rag.rule_texts)
        
        # Test with data that should trigger R1
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'sam_status': 'registered'
        }
        
        relevant_rules = await modified_rag.get_relevant_rules(parsed_data)
        
        # Should not find R1
        rule_ids = [rule['rule_id'] for rule in relevant_rules]
        assert 'R1' not in rule_ids
        
        # Should still find other relevant rules
        assert len(relevant_rules) > 0
    
    @pytest.mark.asyncio
    async def test_rag_without_r3_rule(self):
        """Test RAG behavior when R3 rule is removed from index"""
        # Create a modified RAG service without R3
        modified_rag = RAGService()
        
        # Remove R3 from the rules
        if 'R3' in modified_rag.rules:
            del modified_rag.rules['R3']
        
        # Rebuild index without R3
        modified_rag.rule_texts = []
        modified_rag.rule_ids = []
        
        for rule_id, rule_data in modified_rag.rules.items():
            searchable_text = f"{rule_data['title']}: {rule_data['content']}"
            modified_rag.rule_texts.append(searchable_text)
            modified_rag.rule_ids.append(rule_id)
        
        # Generate embeddings
        modified_rag.embeddings = modified_rag.model.encode(modified_rag.rule_texts)
        
        # Test with past performance data
        parsed_data = {
            'past_performance': [{'value': '$18,000'}]
        }
        
        relevant_rules = await modified_rag.get_relevant_rules(parsed_data)
        
        # Should not find R3
        rule_ids = [rule['rule_id'] for rule in relevant_rules]
        assert 'R3' not in rule_ids
        
        # Should still find other relevant rules
        assert len(relevant_rules) > 0
    
    @pytest.mark.asyncio
    async def test_rag_with_empty_index(self):
        """Test RAG behavior with completely empty index"""
        # Create a modified RAG service with empty rules
        modified_rag = RAGService()
        modified_rag.rules = {}
        modified_rag.rule_texts = []
        modified_rag.rule_ids = []
        modified_rag.embeddings = modified_rag.model.encode([])
        
        # Test with any data
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789'
        }
        
        relevant_rules = await modified_rag.get_relevant_rules(parsed_data)
        
        # Should return empty list
        assert relevant_rules == []
    
    @pytest.mark.asyncio
    async def test_rag_abstention_behavior(self):
        """Test that RAG properly abstains when no relevant rules found"""
        # Create a modified RAG service with only irrelevant rules
        modified_rag = RAGService()
        
        # Keep only R4 (pricing) rule
        modified_rag.rules = {'R4': modified_rag.rules['R4']}
        
        # Rebuild index with only R4
        modified_rag.rule_texts = []
        modified_rag.rule_ids = []
        
        for rule_id, rule_data in modified_rag.rules.items():
            searchable_text = f"{rule_data['title']}: {rule_data['content']}"
            modified_rag.rule_texts.append(searchable_text)
            modified_rag.rule_ids.append(rule_id)
        
        # Generate embeddings
        modified_rag.embeddings = modified_rag.model.encode(modified_rag.rule_texts)
        
        # Test with data that should not match R4
        parsed_data = {
            'uei': 'ABC123DEF456',
            'duns': '123456789',
            'sam_status': 'registered'
        }
        
        relevant_rules = await modified_rag.get_relevant_rules(parsed_data)
        
        # Should either return empty list or low relevance rules
        if relevant_rules:
            # If rules are returned, they should have low relevance
            for rule in relevant_rules:
                assert rule['relevance_score'] < 0.5  # Low relevance threshold
    
    @pytest.mark.asyncio
    async def test_rag_consistency_after_modification(self):
        """Test that RAG maintains consistency after rule modifications"""
        # Test original RAG service
        original_rules = await self.rag_service.get_relevant_rules({
            'uei': 'ABC123DEF456',
            'duns': '123456789'
        })
        
        # Create modified version
        modified_rag = RAGService()
        
        # Remove one rule
        if 'R2' in modified_rag.rules:
            del modified_rag.rules['R2']
        
        # Rebuild index
        modified_rag.rule_texts = []
        modified_rag.rule_ids = []
        
        for rule_id, rule_data in modified_rag.rules.items():
            searchable_text = f"{rule_data['title']}: {rule_data['content']}"
            modified_rag.rule_texts.append(searchable_text)
            modified_rag.rule_ids.append(rule_id)
        
        modified_rag.embeddings = modified_rag.model.encode(modified_rag.rule_texts)
        
        # Test modified RAG service
        modified_rules = await modified_rag.get_relevant_rules({
            'uei': 'ABC123DEF456',
            'duns': '123456789'
        })
        
        # Should have fewer rules
        assert len(modified_rules) < len(original_rules)
        
        # Should not contain R2
        modified_rule_ids = [rule['rule_id'] for rule in modified_rules]
        assert 'R2' not in modified_rule_ids
