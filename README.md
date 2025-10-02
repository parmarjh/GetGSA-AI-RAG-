# GetGSA - AI + RAG Document Analysis

A tiny, working slice of GetGSA that can ingest, classify, and analyze GSA onboarding documents using AI and RAG (Retrieval-Augmented Generation).

## Features

- **Document Ingestion**: Parse and store GSA onboarding documents with PII redaction
- **AI Classification**: Automatically classify documents (profile, past_performance, pricing)
- **Field Extraction**: Extract key fields (UEI, DUNS, NAICS, SAM status, etc.)
- **RAG-Powered Analysis**: Build policy-aware checklists using GSA Rules Pack
- **PII Redaction**: Automatically redact emails and phone numbers
- **Negotiation Prep**: Generate briefs and client emails
- **Single-Page UI**: Clean, responsive interface
- **Comprehensive Testing**: Full test suite with sample inputs

## Quick Start

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd getgsa
```

2. Install dependencies:
```bash
make install
# or
pip install -r requirements.txt
```

3. Run tests:
```bash
make test
# or
python run_tests.py
```

### Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your browser and navigate to:
```
http://localhost:8501
```

## Streamlit Interface

The application provides a user-friendly Streamlit interface with the following features:

### Document Input
- **Text Area**: Paste your GSA document text
- **Sample Documents**: Pre-loaded sample documents for testing
- **Real-time Processing**: Instant analysis of uploaded documents

### Analysis Results
- **Compliance Checklist**: Visual checklist with pass/fail indicators
- **Extracted Data**: Structured display of parsed information
- **Negotiation Brief**: AI-generated preparation brief
- **Client Email**: Draft email for client communication
- **Rule Citations**: References to relevant GSA rules

### Settings
- **Show Raw Data**: Toggle to display raw parsed data
- **Show Citations**: Toggle to display rule citations
- **Sample Documents**: Easy access to test cases

## GSA Rules Pack

The system uses a small knowledge base of GSA rules (R1-R5):

- **R1 - Identity & Registry**: UEI, DUNS, SAM.gov registration requirements
- **R2 - NAICS & SIN Mapping**: NAICS code to SIN mapping rules
- **R3 - Past Performance**: Minimum $25,000 threshold within 36 months
- **R4 - Pricing & Catalog**: Labor categories and rates structure
- **R5 - Submission Hygiene**: PII redaction requirements

## Sample Documents

The application includes three sample document sets:

1. **Complete Submission**: All required elements present
2. **Incomplete Submission**: Missing some required items
3. **Minimal Submission**: Edge cases and minimal data

## Testing

Run the comprehensive test suite:

```bash
make test
```

The test suite includes:
- Unit tests for document processing
- RAG service tests
- PII redaction tests
- AI service tests
- API endpoint tests
- RAG sanity tests

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system architecture and design decisions.

## Security

See [SECURITY.md](SECURITY.md) for security considerations and PII handling.

## Prompts and AI

See [PROMPTS.md](PROMPTS.md) for AI prompts, guardrails, and abstention policies.

## Development

### Project Structure

```
getgsa/
├── app.py                   # Streamlit application
├── backend/
│   ├── models/              # Pydantic models
│   └── services/            # Business logic services
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
├── Makefile                # Build and run commands
└── run_tests.py            # Test runner
```

### Available Commands

```bash
make install      # Install dependencies
make test         # Run tests
make run          # Start Streamlit app
make clean        # Clean up temporary files
make lint         # Run code linter
make format       # Format code
make check        # Run linting and tests
make dev-setup    # Set up development environment
make build        # Build for production
make help         # Show all commands
```

## Scaling Considerations

The current implementation is designed for small-scale usage (10-100 customers). For scaling to 1,000+ customers:

1. **Database**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Queue System**: Add Redis/RabbitMQ for async processing
3. **Caching**: Implement Redis caching for RAG results
4. **Load Balancing**: Use nginx or similar for multiple backend instances
5. **Monitoring**: Add logging, metrics, and health checks
6. **Security**: Implement authentication, rate limiting, and input validation

## Adding New Rule Packs

To add "Pricing Pack v2" or other rule packs:

1. Extend the RAG service to support multiple rule packs
2. Add versioning to the rules system
3. Update the vector index to include new rules
4. Modify the checklist generation to use appropriate rule packs
5. Add tests for new rule combinations

## License

This project is part of the GetGSA coding assessment.

## Support

For questions or issues, please refer to the documentation files or create an issue in the repository.
