from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentData(BaseModel):
    name: str
    type_hint: Optional[str] = None
    text: str

class IngestRequest(BaseModel):
    documents: List[DocumentData]

class IngestResponse(BaseModel):
    doc_summaries: List[Dict[str, Any]]
    request_id: str

class Document(BaseModel):
    name: str
    type_hint: Optional[str] = None
    text: str
    redacted_text: str
    created_at: datetime

class ParsedData(BaseModel):
    uei: Optional[str] = None
    duns: Optional[str] = None
    naics_codes: List[str] = []
    sam_status: Optional[str] = None
    primary_contact: Optional[Dict[str, str]] = None
    past_performance: List[Dict[str, Any]] = []
    pricing_data: List[Dict[str, str]] = []
    document_types: List[str] = []

class ChecklistItem(BaseModel):
    required: bool
    ok: bool
    problem: Optional[str] = None
    evidence: Optional[str] = None
    rule_ids: List[str] = []

class Checklist(BaseModel):
    items: List[ChecklistItem]
    overall_status: str

class Citation(BaseModel):
    rule_id: str
    chunk: str
    relevance_score: float

class AnalyzeResponse(BaseModel):
    parsed: ParsedData
    checklist: Checklist
    brief: str
    client_email: str
    citations: List[Citation]
    request_id: str
