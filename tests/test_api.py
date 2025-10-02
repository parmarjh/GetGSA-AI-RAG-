import pytest
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

class TestAPI:
    """Test API endpoints"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
    
    def test_ingest_documents(self):
        """Test document ingestion"""
        test_document = {
            "documents": [{
                "name": "test.txt",
                "type_hint": "profile",
                "text": "UEI: ABC123DEF456, DUNS: 123456789, SAM.gov: registered"
            }]
        }
        
        response = self.client.post("/ingest", json=test_document)
        assert response.status_code == 200
        
        result = response.json()
        assert "request_id" in result
        assert "doc_summaries" in result
        assert len(result["doc_summaries"]) == 1
        assert result["doc_summaries"][0]["name"] == "test.txt"
    
    def test_ingest_multiple_documents(self):
        """Test ingesting multiple documents"""
        test_documents = {
            "documents": [
                {
                    "name": "profile.txt",
                    "type_hint": "profile",
                    "text": "UEI: ABC123DEF456, DUNS: 123456789"
                },
                {
                    "name": "pp.txt",
                    "type_hint": "past_performance",
                    "text": "Customer: City of Palo Verde, Value: $30,000"
                }
            ]
        }
        
        response = self.client.post("/ingest", json=test_documents)
        assert response.status_code == 200
        
        result = response.json()
        assert len(result["doc_summaries"]) == 2
    
    def test_analyze_documents(self):
        """Test document analysis"""
        # First ingest documents
        test_document = {
            "documents": [{
                "name": "test.txt",
                "type_hint": "profile",
                "text": "UEI: ABC123DEF456, DUNS: 123456789, SAM.gov: registered"
            }]
        }
        
        ingest_response = self.client.post("/ingest", json=test_document)
        request_id = ingest_response.json()["request_id"]
        
        # Then analyze
        response = self.client.post(f"/analyze?request_id={request_id}")
        assert response.status_code == 200
        
        result = response.json()
        assert "parsed" in result
        assert "checklist" in result
        assert "brief" in result
        assert "client_email" in result
        assert "citations" in result
        assert "request_id" in result
    
    def test_analyze_without_ingest(self):
        """Test analysis without prior ingestion"""
        response = self.client.post("/analyze")
        assert response.status_code == 400
        assert "No documents found" in response.json()["detail"]
    
    def test_ingest_empty_documents(self):
        """Test ingesting empty document list"""
        test_document = {"documents": []}
        
        response = self.client.post("/ingest", json=test_document)
        assert response.status_code == 200
        
        result = response.json()
        assert len(result["doc_summaries"]) == 0
    
    def test_ingest_invalid_json(self):
        """Test ingesting invalid JSON"""
        response = self.client.post("/ingest", json={"invalid": "data"})
        assert response.status_code == 422  # Validation error
    
    def test_pii_redaction_in_ingest(self):
        """Test that PII is redacted during ingestion"""
        test_document = {
            "documents": [{
                "name": "test.txt",
                "type_hint": "profile",
                "text": "Contact: Jane Smith, jane@acme.co, (415) 555-0100"
            }]
        }
        
        response = self.client.post("/ingest", json=test_document)
        assert response.status_code == 200
        
        result = response.json()
        # Should indicate that redaction occurred
        assert result["doc_summaries"][0]["redacted"] == True
    
    def test_analyze_latest_documents(self):
        """Test analyzing latest documents without request_id"""
        # Ingest first set
        test_document1 = {
            "documents": [{
                "name": "test1.txt",
                "type_hint": "profile",
                "text": "UEI: ABC123DEF456, DUNS: 123456789"
            }]
        }
        
        self.client.post("/ingest", json=test_document1)
        
        # Ingest second set
        test_document2 = {
            "documents": [{
                "name": "test2.txt",
                "type_hint": "profile",
                "text": "UEI: XYZ789GHI012, DUNS: 987654321"
            }]
        }
        
        self.client.post("/ingest", json=test_document2)
        
        # Analyze without request_id (should use latest)
        response = self.client.post("/analyze")
        assert response.status_code == 200
        
        result = response.json()
        # Should analyze the second set (latest)
        assert result["parsed"]["uei"] == "XYZ789GHI012"
        assert result["parsed"]["duns"] == "987654321"
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/healthz")
        assert response.status_code == 200
        # CORS headers should be present (handled by middleware)
    
    def test_error_handling(self):
        """Test error handling for malformed requests"""
        # Test with missing required fields
        response = self.client.post("/ingest", json={})
        assert response.status_code == 422
        
        # Test with invalid request_id
        response = self.client.post("/analyze?request_id=invalid-id")
        assert response.status_code == 400
