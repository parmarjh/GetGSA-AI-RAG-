import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any
import asyncio

class RAGService:
    """RAG service for GSA Rules Pack retrieval"""
    
    def __init__(self):
        # Initialize simple text embedding model (CPU-based)
        self.model = None  # Will use simple TF-IDF approach
        
        # GSA Rules Pack (R1-R5)
        self.rules = {
            "R1": {
                "title": "Identity & Registry",
                "content": "Required: UEI (12 chars), DUNS (9 digits), and active SAM.gov registration. Primary contact must have valid email and phone.",
                "requirements": ["UEI", "DUNS", "SAM.gov registration", "primary contact email", "primary contact phone"]
            },
            "R2": {
                "title": "NAICS & SIN Mapping",
                "content": "541511 → 54151S, 541512 → 54151S, 541611 → 541611, 518210 → 518210C",
                "mappings": {
                    "541511": "54151S",
                    "541512": "54151S", 
                    "541611": "541611",
                    "518210": "518210C"
                }
            },
            "R3": {
                "title": "Past Performance",
                "content": "At least 1 past performance ≥ $25,000 within last 36 months. Must include customer name, value, period, and contact email.",
                "requirements": ["past performance ≥ $25,000", "within last 36 months", "customer name", "value", "period", "contact email"]
            },
            "R4": {
                "title": "Pricing & Catalog",
                "content": "Provide labor categories and rates in a structured sheet. If missing rate basis or units, flag 'pricing_incomplete'.",
                "requirements": ["labor categories", "rates", "structured sheet", "rate basis", "units"]
            },
            "R5": {
                "title": "Submission Hygiene",
                "content": "All personally identifiable info must be stored in redacted form; only derived fields and hashes are stored by default.",
                "requirements": ["PII redaction", "derived fields", "hashes"]
            }
        }
        
        # Build vector index
        self._build_index()
    
    def _build_index(self):
        """Build vector index from rules"""
        self.rule_texts = []
        self.rule_ids = []
        
        for rule_id, rule_data in self.rules.items():
            # Create searchable text
            searchable_text = f"{rule_data['title']}: {rule_data['content']}"
            self.rule_texts.append(searchable_text)
            self.rule_ids.append(rule_id)
        
        # Generate simple embeddings using TF-IDF
        self.embeddings = self._create_simple_embeddings(self.rule_texts)
    
    async def get_relevant_rules(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get relevant rules based on parsed data"""
        # Create query text from parsed data
        query_parts = []
        
        if parsed_data.get('uei'):
            query_parts.append("UEI DUNS SAM.gov registration")
        if parsed_data.get('naics_codes'):
            query_parts.append("NAICS SIN mapping")
        if parsed_data.get('past_performance'):
            query_parts.append("past performance requirements")
        if parsed_data.get('pricing_data'):
            query_parts.append("pricing labor categories rates")
        
        query_text = " ".join(query_parts)
        
        # Generate query embedding
        query_embedding = self._create_simple_embeddings([query_text])
        
        # Calculate similarities
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top relevant rules
        relevant_rules = []
        for i, similarity in enumerate(similarities):
            if similarity > 0.3:  # Threshold for relevance
                relevant_rules.append({
                    "rule_id": self.rule_ids[i],
                    "chunk": self.rule_texts[i],
                    "relevance_score": float(similarity)
                })
        
        # Sort by relevance score
        relevant_rules.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return relevant_rules
    
    def get_rule_by_id(self, rule_id: str) -> Dict[str, Any]:
        """Get specific rule by ID"""
        return self.rules.get(rule_id, {})
    
    def get_naics_mapping(self, naics_code: str) -> str:
        """Get SIN mapping for NAICS code"""
        rule_r2 = self.rules.get("R2", {})
        mappings = rule_r2.get("mappings", {})
        return mappings.get(naics_code, naics_code)
    
    def _create_simple_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create simple embeddings using TF-IDF approach"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Fit and transform texts
        embeddings = vectorizer.fit_transform(texts)
        
        # Convert to dense array
        return embeddings.toarray()
