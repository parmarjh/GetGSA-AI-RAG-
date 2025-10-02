# GetGSA Architecture

## System Overview

GetGSA is a microservice-based application that combines AI, RAG (Retrieval-Augmented Generation), and document processing to analyze GSA onboarding documents for compliance.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (HTML/JS)     │◄──►│   (FastAPI)     │◄──►│   (Mock LLM)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   RAG Service   │
                       │   (Vector DB)   │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Document      │
                       │   Processor     │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   PII Redactor  │
                       └─────────────────┘
```

## Data Flow

```
1. User Input → Frontend → Backend API
2. Document Ingestion → PII Redaction → Storage
3. Document Analysis → Field Extraction → RAG Retrieval
4. AI Processing → Checklist Generation → Brief/Email Creation
5. Results → Frontend Display
```

## Component Details

### Frontend (Single-Page Application)
- **Technology**: HTML5, CSS3, JavaScript (Vanilla)
- **Purpose**: User interface for document input and results display
- **Features**: Sample document selection, real-time analysis, responsive design
- **Communication**: REST API calls to backend

### Backend (FastAPI)
- **Technology**: Python 3.8+, FastAPI, Pydantic
- **Purpose**: API server and business logic orchestration
- **Endpoints**: `/ingest`, `/analyze`, `/healthz`
- **Storage**: In-memory (production: database)
- **Security**: CORS middleware, input validation

### RAG Service
- **Technology**: Sentence Transformers, scikit-learn
- **Purpose**: Vector-based retrieval of GSA rules
- **Model**: `all-MiniLM-L6-v2` (384-dimensional embeddings)
- **Index**: In-memory vector store of rules R1-R5
- **Retrieval**: Cosine similarity with relevance threshold

### Document Processor
- **Technology**: Python, Regular Expressions
- **Purpose**: Field extraction and document classification
- **Features**: UEI/DUNS validation, NAICS parsing, contact extraction
- **Output**: Structured data for analysis

### AI Service
- **Technology**: Mock LLM interface (extensible to real LLM)
- **Purpose**: Document classification and content generation
- **Features**: Abstention handling, rule-based fallbacks
- **Outputs**: Checklists, negotiation briefs, client emails

### PII Redactor
- **Technology**: Python, Regular Expressions
- **Purpose**: Redact sensitive information before storage
- **Targets**: Email addresses, phone numbers
- **Method**: Pattern matching with replacement tokens

## AI Integration Strategy

### Current Implementation (Mock LLM)
- **Classification**: Rule-based with keyword matching
- **Checklist Generation**: Rule-driven logic with GSA compliance
- **Content Generation**: Template-based with rule citations
- **Abstention**: Returns "unknown" for ambiguous content

### Production LLM Integration
- **Interface**: Well-defined abstraction layer
- **Fallback**: Classical methods when model abstains
- **Prompts**: Structured prompts with examples and guardrails
- **Confidence**: Threshold-based decision making

## Scalability Design

### Current Scale (10-100 customers)
- **Storage**: In-memory dictionaries
- **Processing**: Synchronous API calls
- **Caching**: None (stateless design)
- **Deployment**: Single instance

### Target Scale (1,000+ customers)
- **Database**: PostgreSQL for document storage
- **Queue System**: Redis/RabbitMQ for async processing
- **Caching**: Redis for RAG results and parsed data
- **Load Balancing**: nginx with multiple backend instances
- **Monitoring**: Structured logging, metrics, health checks

## Security Considerations

### Data Protection
- **PII Redaction**: Automatic masking of emails/phones
- **Input Validation**: Pydantic models with strict validation
- **Size Limits**: Configurable document size limits
- **Rate Limiting**: API endpoint protection (production)

### Access Control
- **Authentication**: None (assessment requirement)
- **Authorization**: None (assessment requirement)
- **CORS**: Configured for frontend access
- **HTTPS**: Required in production

## Rule Pack System

### Current Rules (R1-R5)
- **R1**: Identity & Registry requirements
- **R2**: NAICS & SIN mapping rules
- **R3**: Past performance thresholds
- **R4**: Pricing structure requirements
- **R5**: Submission hygiene standards

### Extensibility
- **Versioning**: Rule pack versioning system
- **Dynamic Loading**: Runtime rule pack updates
- **Vector Index**: Automatic reindexing on updates
- **Backward Compatibility**: Support for multiple rule versions

## Error Handling

### API Errors
- **Validation**: Pydantic model validation
- **Business Logic**: Custom exception handling
- **HTTP Status**: Appropriate status codes
- **Error Messages**: User-friendly error descriptions

### AI Abstention
- **Low Confidence**: Return "unknown" classification
- **Missing Data**: Flag as incomplete in checklist
- **Rule Conflicts**: Prioritize by relevance score
- **Fallback Logic**: Classical methods when AI fails

## Performance Characteristics

### Latency
- **Document Ingestion**: ~100ms (small documents)
- **RAG Retrieval**: ~50ms (vector similarity)
- **Field Extraction**: ~20ms (regex processing)
- **AI Processing**: ~200ms (mock LLM)

### Throughput
- **Concurrent Requests**: Limited by Python GIL
- **Memory Usage**: ~100MB base + document storage
- **CPU Usage**: Moderate (vector operations)
- **Storage**: In-memory (no persistence)

## Deployment Architecture

### Development
```
Frontend (localhost:8001) → Backend (localhost:8000)
```

### Production (Recommended)
```
Load Balancer (nginx) → Backend Instances (FastAPI) → Database (PostgreSQL)
                     → Cache (Redis) → Queue (RabbitMQ)
```

## Monitoring and Observability

### Logging
- **Structured Logs**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Sensitive Data**: Automatic PII masking
- **Performance**: Request timing and metrics

### Health Checks
- **Endpoint**: `/healthz` for basic health
- **Dependencies**: RAG service, AI service status
- **Database**: Connection health (production)
- **External Services**: LLM API status (production)

## Future Enhancements

### Short Term
- **Real LLM Integration**: OpenAI/Anthropic API
- **Database Persistence**: PostgreSQL integration
- **Authentication**: JWT-based auth system
- **API Documentation**: OpenAPI/Swagger UI

### Long Term
- **Multi-tenant Support**: Customer isolation
- **Advanced Analytics**: Compliance trend analysis
- **Integration APIs**: Third-party system connections
- **Mobile Support**: Responsive mobile interface

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.8+
- **Models**: Pydantic 2.5.0
- **AI/ML**: sentence-transformers 2.2.2, scikit-learn 1.3.0
- **Testing**: pytest 7.4.3, httpx 0.25.2

### Frontend
- **Technology**: Vanilla JavaScript, HTML5, CSS3
- **Styling**: CSS Grid, Flexbox, Custom CSS
- **Communication**: Fetch API
- **Responsive**: Mobile-first design

### Infrastructure
- **Containerization**: Docker (recommended)
- **Process Management**: uvicorn (development)
- **Reverse Proxy**: nginx (production)
- **Database**: PostgreSQL (production)
- **Cache**: Redis (production)
- **Queue**: RabbitMQ (production)

## Development Workflow

### Local Development
1. Install dependencies: `make install`
2. Run tests: `make test`
3. Start backend: `make run`
4. Serve frontend: `make serve-frontend`
5. Access application: `http://localhost:8001`

### Testing Strategy
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **RAG Tests**: Vector retrieval validation
- **PII Tests**: Redaction verification
- **AI Tests**: Classification and generation

### Code Quality
- **Linting**: flake8 with custom rules
- **Formatting**: black with 100-character lines
- **Type Hints**: Full type annotation
- **Documentation**: Inline docstrings and comments
