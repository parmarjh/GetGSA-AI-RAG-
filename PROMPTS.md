# AI Prompts and Reasoning Strategy

## Overview

This document outlines the AI prompts, guardrails, and abstention policies used in the GetGSA application. The current implementation uses a mock LLM interface that can be easily replaced with real LLM services.

## AI Service Architecture

### Mock LLM Interface
The current implementation uses a mock LLM that simulates AI behavior using rule-based logic. This allows for:
- **Consistent Testing**: Predictable outputs for test cases
- **Fast Development**: No external API dependencies
- **Cost Control**: No LLM API costs during development
- **Easy Replacement**: Well-defined interface for real LLM integration

### Abstention Strategy
When the AI service encounters ambiguous or low-confidence scenarios, it implements abstention by:
1. **Returning "unknown"** for document classification
2. **Flagging incomplete data** in checklists
3. **Using fallback logic** for content generation
4. **Avoiding hallucination** of missing information

## Document Classification Prompts

### Current Implementation (Rule-Based)
```python
def _mock_classify_document(self, text: str, type_hint: Optional[str] = None) -> str:
    """Mock document classification using rules"""
    text_lower = text.lower()
    
    # Use type hint if provided
    if type_hint:
        return type_hint
    
    # Rule-based classification
    if any(keyword in text_lower for keyword in ['uei:', 'duns:', 'sam.gov', 'primary contact', 'poc:']):
        return 'profile'
    elif any(keyword in text_lower for keyword in ['past performance', 'customer:', 'contract:', 'value:', 'period:']):
        return 'past_performance'
    elif any(keyword in text_lower for keyword in ['labor category', 'rate', 'pricing', 'hour', 'day']):
        return 'pricing'
    else:
        return 'unknown'  # Abstention
```

### Production LLM Prompt
```text
You are a document classification system for GSA (General Services Administration) onboarding documents.

Classify the following document into one of these categories:
- profile: Company information, UEI, DUNS, SAM.gov status, primary contact
- past_performance: Customer projects, contract values, performance history
- pricing: Labor categories, rates, pricing sheets
- unknown: Cannot determine document type

Document text: {document_text}

Rules:
1. Look for key indicators like UEI, DUNS, SAM.gov for profile documents
2. Look for customer names, contract values, periods for past performance
3. Look for labor categories, rates, units for pricing documents
4. If uncertain, return "unknown" to avoid misclassification

Return only the category name.
```

## Checklist Generation Prompts

### Current Implementation (Rule-Based)
The mock implementation uses structured rule checking:

```python
def _mock_generate_checklist(self, parsed_data: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mock checklist generation using rules"""
    items = []
    problems = []
    
    # R1 - Identity & Registry
    if not parsed_data.get('uei'):
        problems.append('missing_uei')
        items.append({
            "required": True,
            "ok": False,
            "problem": "missing_uei",
            "evidence": "UEI not found in documents",
            "rule_ids": ["R1"]
        })
    # ... more rule checks
```

### Production LLM Prompt
```text
You are a GSA compliance checker. Generate a compliance checklist based on the parsed document data and relevant GSA rules.

Parsed Data: {parsed_data}
Relevant Rules: {relevant_rules}

For each rule, determine:
1. Is the requirement met? (ok: true/false)
2. What is the evidence? (specific data found or missing)
3. What is the problem? (if not met, specific issue)
4. Which rules apply? (rule IDs)

Rules to check:
- R1: UEI (12 chars), DUNS (9 digits), active SAM.gov registration, valid contact info
- R2: NAICS codes properly mapped to SIN codes
- R3: At least 1 past performance ≥ $25,000 within last 36 months
- R4: Complete pricing with labor categories, rates, and units
- R5: PII properly redacted

Return a JSON object with:
{
  "items": [
    {
      "required": true,
      "ok": true/false,
      "problem": "specific_problem_name" or null,
      "evidence": "specific evidence text",
      "rule_ids": ["R1", "R2"]
    }
  ],
  "overall_status": "pass" or "fail"
}

If you cannot determine compliance for any item, mark it as "ok": false with "problem": "insufficient_data".
```

## Negotiation Brief Generation Prompts

### Current Implementation (Template-Based)
```python
def _mock_generate_negotiation_brief(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> str:
    """Mock negotiation brief generation"""
    problems = [item['problem'] for item in checklist['items'] if item['problem']]
    
    brief = "## Negotiation Prep Brief\n\n"
    
    if not problems:
        brief += "**Strengths:** All required elements are present and compliant...\n\n"
    else:
        brief += "**Key Issues Identified:**\n"
        for problem in problems:
            if problem == 'missing_uei':
                brief += "- Missing UEI (Unique Entity Identifier) - required for GSA registration (R1)\n"
            # ... more problem descriptions
```

### Production LLM Prompt
```text
You are a GSA negotiation preparation specialist. Generate a negotiation prep brief based on the document analysis.

Parsed Data: {parsed_data}
Checklist: {checklist}
Relevant Rules: {relevant_rules}

Create a 2-3 paragraph brief that includes:

1. **Strengths**: What the submission does well
2. **Key Issues**: Specific problems that need attention
3. **Negotiation Strategy**: How to approach the negotiation
4. **Rule Citations**: Which GSA rules are relevant

Focus on:
- Compliance gaps that need to be addressed
- Pricing negotiation opportunities
- Documentation completeness
- Risk mitigation strategies

Tone: Professional, analytical, actionable
Length: 2-3 paragraphs
Format: Markdown with clear headings

If you cannot provide specific guidance due to insufficient data, state this clearly and recommend additional information gathering.
```

## Client Email Generation Prompts

### Current Implementation (Template-Based)
```python
def _mock_generate_client_email(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any]) -> str:
    """Mock client email generation"""
    problems = [item['problem'] for item in checklist['items'] if item['problem']]
    
    email = "Subject: GSA Submission Review - Action Required\n\n"
    email += "Dear Client,\n\n"
    email += "Thank you for submitting your GSA documentation...\n\n"
    
    if not problems:
        email += "✅ All required documentation is complete and compliant.\n\n"
    else:
        email += "❌ **Missing or Incomplete Items:**\n"
        for problem in problems:
            if problem == 'missing_uei':
                email += "- Unique Entity Identifier (UEI)\n"
            # ... more problem descriptions
```

### Production LLM Prompt
```text
You are a GSA compliance specialist writing a client email. Generate a professional, polite email summarizing the document review results.

Parsed Data: {parsed_data}
Checklist: {checklist}

Email Requirements:
- Subject line: Clear and actionable
- Greeting: Professional and personal
- Body: Concise summary of findings
- Next steps: Clear action items
- Closing: Professional sign-off

Tone: Polite, professional, helpful
Length: 1-2 paragraphs
Format: Plain text email

Include:
1. Acknowledgment of submission
2. Summary of compliance status
3. Specific missing or incomplete items
4. Clear next steps
5. Offer of assistance

If all requirements are met, congratulate the client and outline next steps for submission.
If issues are found, be specific about what needs to be addressed.
```

## Guardrails and Safety Measures

### Input Validation
- **Document Size**: Maximum 10MB per document
- **Text Length**: Maximum 100,000 characters
- **File Types**: Text-based documents only
- **Encoding**: UTF-8 encoding required

### Output Validation
- **Structured Data**: All outputs must match expected schemas
- **Rule Citations**: All claims must be backed by rule references
- **Evidence**: All checklist items must include specific evidence
- **Abstention**: Clear indication when AI cannot determine answer

### Error Handling
- **Timeout**: 30-second timeout for AI operations
- **Retry Logic**: 3 retry attempts for transient failures
- **Fallback**: Rule-based fallback when AI fails
- **Logging**: All AI decisions logged for audit

## Confidence Scoring

### Classification Confidence
- **High (0.8-1.0)**: Clear document type indicators
- **Medium (0.5-0.8)**: Some indicators present
- **Low (0.0-0.5)**: Ambiguous or conflicting indicators
- **Abstention**: Below 0.3 threshold

### Checklist Confidence
- **High**: All required data present and validated
- **Medium**: Most data present, some gaps
- **Low**: Significant missing data
- **Abstention**: Cannot determine compliance

### Content Generation Confidence
- **High**: Clear requirements and sufficient data
- **Medium**: Some requirements unclear
- **Low**: Significant data gaps
- **Abstention**: Insufficient information for generation

## Production LLM Integration

### OpenAI Integration Example
```python
async def _llm_classify_document(self, text: str, type_hint: Optional[str] = None) -> str:
    """Real LLM classification using OpenAI"""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": CLASSIFICATION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Document text: {text[:1000]}..."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        classification = response.choices[0].message.content.strip().lower()
        
        # Validate response
        if classification in ['profile', 'past_performance', 'pricing', 'unknown']:
            return classification
        else:
            return 'unknown'  # Abstention for invalid response
            
    except Exception as e:
        logger.error(f"LLM classification failed: {e}")
        return 'unknown'  # Abstention on error
```

### Anthropic Integration Example
```python
async def _llm_generate_checklist(self, parsed_data: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Real LLM checklist generation using Anthropic"""
    try:
        response = await anthropic.acreate(
            model="claude-3-sonnet-20240229",
            prompt=f"{CHECKLIST_SYSTEM_PROMPT}\n\nParsed Data: {json.dumps(parsed_data)}\nRelevant Rules: {json.dumps(relevant_rules)}",
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse and validate response
        checklist = json.loads(response.completion)
        return self._validate_checklist(checklist)
        
    except Exception as e:
        logger.error(f"LLM checklist generation failed: {e}")
        return self._fallback_checklist(parsed_data, relevant_rules)
```

## Testing and Validation

### Prompt Testing
- **Unit Tests**: Individual prompt testing with known inputs
- **Integration Tests**: End-to-end prompt validation
- **Edge Cases**: Ambiguous inputs, missing data, invalid formats
- **Performance Tests**: Response time and token usage

### Output Validation
- **Schema Validation**: JSON schema compliance
- **Rule Compliance**: All citations must reference valid rules
- **Evidence Validation**: All claims must have supporting evidence
- **Abstention Testing**: Proper abstention for low-confidence scenarios

### Continuous Improvement
- **Feedback Loop**: User feedback on AI outputs
- **Prompt Optimization**: A/B testing of prompt variations
- **Performance Monitoring**: Response time and accuracy tracking
- **Rule Updates**: Prompt updates when GSA rules change

## Future Enhancements

### Advanced AI Features
- **Multi-modal Processing**: Image and PDF document analysis
- **Contextual Understanding**: Better document relationship analysis
- **Learning System**: Continuous improvement from user feedback
- **Custom Models**: Fine-tuned models for GSA-specific tasks

### Prompt Engineering
- **Chain-of-Thought**: Step-by-step reasoning prompts
- **Few-shot Learning**: Example-based prompt optimization
- **Prompt Templates**: Reusable prompt components
- **Dynamic Prompts**: Context-aware prompt generation
