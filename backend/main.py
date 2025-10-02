from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import re
import json
from datetime import datetime
import asyncio

from services.document_processor import DocumentProcessor
from services.rag_service import RAGService
from services.ai_service import AIService
from services.pii_redactor import PIIRedactor
from models.document_models import Document, IngestRequest, IngestResponse, AnalyzeResponse

app = FastAPI(title="GetGSA API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
rag_service = RAGService()
ai_service = AIService()
pii_redactor = PIIRedactor()

# In-memory storage (in production, use Redis or database)
document_store = {}
analysis_store = {}

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {"ok": True}

@app.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """Ingest and store documents with PII redaction"""
    try:
        request_id = str(uuid.uuid4())
        doc_summaries = []
        
        for doc_data in request.documents:
            # Redact PII before storage
            redacted_text = pii_redactor.redact(doc_data.text)
            
            # Create document object
            document = Document(
                name=doc_data.name,
                type_hint=doc_data.type_hint,
                text=doc_data.text,
                redacted_text=redacted_text,
                created_at=datetime.now()
            )
            
            # Store both original and redacted versions
            document_store[request_id] = document_store.get(request_id, [])
            document_store[request_id].append(document)
            
            # Create summary
            summary = {
                "name": doc_data.name,
                "type_hint": doc_data.type_hint,
                "text_length": len(doc_data.text),
                "redacted": redacted_text != doc_data.text
            }
            doc_summaries.append(summary)
        
        return IngestResponse(
            doc_summaries=doc_summaries,
            request_id=request_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting documents: {str(e)}")

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_documents(request_id: Optional[str] = None):
    """Analyze documents and generate checklist, brief, and client email"""
    try:
        # Get documents to analyze
        if request_id and request_id in document_store:
            documents = document_store[request_id]
        elif document_store:
            # Use most recent request
            latest_request_id = max(document_store.keys())
            documents = document_store[latest_request_id]
            request_id = latest_request_id
        else:
            raise HTTPException(status_code=400, detail="No documents found to analyze")
        
        # Process documents
        parsed_data = await document_processor.process_documents(documents)
        
        # Get relevant rules using RAG
        relevant_rules = await rag_service.get_relevant_rules(parsed_data)
        
        # Generate checklist using AI
        checklist = await ai_service.generate_checklist(parsed_data, relevant_rules)
        
        # Generate brief and client email
        brief = await ai_service.generate_negotiation_brief(parsed_data, checklist, relevant_rules)
        client_email = await ai_service.generate_client_email(parsed_data, checklist)
        
        # Store analysis results
        analysis_result = {
            "parsed": parsed_data,
            "checklist": checklist,
            "brief": brief,
            "client_email": client_email,
            "citations": relevant_rules,
            "request_id": request_id,
            "created_at": datetime.now()
        }
        analysis_store[request_id] = analysis_result
        
        return AnalyzeResponse(**analysis_result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing documents: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
