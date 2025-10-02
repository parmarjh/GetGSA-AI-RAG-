import json
import re
from typing import List, Dict, Any, Optional
import asyncio

class AIService:
    """AI service for document classification and content generation"""
    
    def __init__(self):
        # Mock LLM interface - in production, replace with actual LLM
        self.use_mock = True  # Set to False to use real LLM
    
    async def classify_document(self, text: str, type_hint: Optional[str] = None) -> str:
        """Classify document type using AI or rules-based approach"""
        if self.use_mock:
            return self._mock_classify_document(text, type_hint)
        else:
            # Real LLM implementation would go here
            return await self._llm_classify_document(text, type_hint)
    
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
            return 'unknown'
    
    async def _llm_classify_document(self, text: str, type_hint: Optional[str] = None) -> str:
        """Real LLM classification (placeholder)"""
        # This would use OpenAI, Anthropic, or local model
        prompt = f"""
        Classify this document into one of these categories: profile, past_performance, pricing, unknown
        
        Document text: {text[:500]}...
        
        Return only the category name.
        """
        
        # Mock response for now
        return 'unknown'
    
    async def generate_checklist(self, parsed_data: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate policy-aware checklist"""
        if self.use_mock:
            return self._mock_generate_checklist(parsed_data, relevant_rules)
        else:
            return await self._llm_generate_checklist(parsed_data, relevant_rules)
    
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
        else:
            items.append({
                "required": True,
                "ok": True,
                "problem": None,
                "evidence": f"UEI found: {parsed_data['uei']}",
                "rule_ids": ["R1"]
            })
        
        if not parsed_data.get('duns'):
            problems.append('missing_duns')
            items.append({
                "required": True,
                "ok": False,
                "problem": "missing_duns",
                "evidence": "DUNS not found in documents",
                "rule_ids": ["R1"]
            })
        else:
            items.append({
                "required": True,
                "ok": True,
                "problem": None,
                "evidence": f"DUNS found: {parsed_data['duns']}",
                "rule_ids": ["R1"]
            })
        
        if not parsed_data.get('sam_status') or 'active' not in parsed_data['sam_status'].lower():
            problems.append('sam_not_active')
            items.append({
                "required": True,
                "ok": False,
                "problem": "sam_not_active",
                "evidence": "SAM.gov registration not active",
                "rule_ids": ["R1"]
            })
        else:
            items.append({
                "required": True,
                "ok": True,
                "problem": None,
                "evidence": f"SAM.gov status: {parsed_data['sam_status']}",
                "rule_ids": ["R1"]
            })
        
        # R3 - Past Performance
        past_performance = parsed_data.get('past_performance', [])
        if not past_performance:
            problems.append('missing_past_performance')
            items.append({
                "required": True,
                "ok": False,
                "problem": "missing_past_performance",
                "evidence": "No past performance records found",
                "rule_ids": ["R3"]
            })
        else:
            # Check if any past performance meets minimum value
            min_value_met = False
            for pp in past_performance:
                value = pp.get('value', 0)
                if isinstance(value, str):
                    # Extract numeric value from string
                    value_match = re.search(r'\$?([\d,]+)', value)
                    if value_match:
                        value = int(value_match.group(1).replace(',', ''))
                    else:
                        value = 0
                
                if value >= 25000:
                    min_value_met = True
                    break
            
            if not min_value_met:
                problems.append('past_performance_min_value_not_met')
                items.append({
                    "required": True,
                    "ok": False,
                    "problem": "past_performance_min_value_not_met",
                    "evidence": "No past performance ≥ $25,000 found",
                    "rule_ids": ["R3"]
                })
            else:
                items.append({
                    "required": True,
                    "ok": True,
                    "problem": None,
                    "evidence": "Past performance ≥ $25,000 found",
                    "rule_ids": ["R3"]
                })
        
        # R4 - Pricing
        pricing_data = parsed_data.get('pricing_data', [])
        if not pricing_data:
            problems.append('pricing_incomplete')
            items.append({
                "required": True,
                "ok": False,
                "problem": "pricing_incomplete",
                "evidence": "No pricing data found",
                "rule_ids": ["R4"]
            })
        else:
            # Check if pricing has required fields
            complete_pricing = True
            for pricing in pricing_data:
                if not pricing.get('rate') or not pricing.get('unit'):
                    complete_pricing = False
                    break
            
            if not complete_pricing:
                problems.append('pricing_incomplete')
                items.append({
                    "required": True,
                    "ok": False,
                    "problem": "pricing_incomplete",
                    "evidence": "Pricing data missing rate or unit information",
                    "rule_ids": ["R4"]
                })
            else:
                items.append({
                    "required": True,
                    "ok": True,
                    "problem": None,
                    "evidence": "Pricing data complete",
                    "rule_ids": ["R4"]
                })
        
        # Determine overall status
        overall_status = "pass" if not problems else "fail"
        
        return {
            "items": items,
            "overall_status": overall_status
        }
    
    async def _llm_generate_checklist(self, parsed_data: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Real LLM checklist generation (placeholder)"""
        # This would use LLM to generate checklist
        return {"items": [], "overall_status": "unknown"}
    
    async def generate_negotiation_brief(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> str:
        """Generate negotiation prep brief"""
        if self.use_mock:
            return self._mock_generate_negotiation_brief(parsed_data, checklist, relevant_rules)
        else:
            return await self._llm_generate_negotiation_brief(parsed_data, checklist, relevant_rules)
    
    def _mock_generate_negotiation_brief(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> str:
        """Mock negotiation brief generation"""
        problems = [item['problem'] for item in checklist['items'] if item['problem']]
        
        brief = "## Negotiation Prep Brief\n\n"
        
        if not problems:
            brief += "**Strengths:** All required elements are present and compliant. The submission meets GSA requirements for identity verification, past performance, and pricing structure.\n\n"
            brief += "**Recommendation:** Proceed with standard negotiation process. No major gaps identified.\n\n"
        else:
            brief += "**Key Issues Identified:**\n"
            for problem in problems:
                if problem == 'missing_uei':
                    brief += "- Missing UEI (Unique Entity Identifier) - required for GSA registration (R1)\n"
                elif problem == 'missing_duns':
                    brief += "- Missing DUNS number - required for GSA registration (R1)\n"
                elif problem == 'sam_not_active':
                    brief += "- SAM.gov registration not active - must be current (R1)\n"
                elif problem == 'past_performance_min_value_not_met':
                    brief += "- Past performance below $25,000 threshold - need at least one project ≥ $25,000 (R3)\n"
                elif problem == 'pricing_incomplete':
                    brief += "- Pricing data incomplete - missing rate basis or units (R4)\n"
            
            brief += "\n**Negotiation Strategy:** Focus on obtaining missing documentation and addressing compliance gaps before proceeding with pricing discussions.\n\n"
        
        brief += "**Rule Citations:** " + ", ".join([rule['rule_id'] for rule in relevant_rules]) + "\n"
        
        return brief
    
    async def _llm_generate_negotiation_brief(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any], relevant_rules: List[Dict[str, Any]]) -> str:
        """Real LLM brief generation (placeholder)"""
        return "LLM-generated brief would appear here"
    
    async def generate_client_email(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any]) -> str:
        """Generate client email draft"""
        if self.use_mock:
            return self._mock_generate_client_email(parsed_data, checklist)
        else:
            return await self._llm_generate_client_email(parsed_data, checklist)
    
    def _mock_generate_client_email(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any]) -> str:
        """Mock client email generation"""
        problems = [item['problem'] for item in checklist['items'] if item['problem']]
        
        email = "Subject: GSA Submission Review - Action Required\n\n"
        email += "Dear Client,\n\n"
        email += "Thank you for submitting your GSA documentation. We have completed our initial review and identified the following items that need attention:\n\n"
        
        if not problems:
            email += "✅ All required documentation is complete and compliant.\n\n"
            email += "Next steps:\n"
            email += "1. Proceed with GSA submission\n"
            email += "2. Schedule negotiation meeting\n"
            email += "3. Prepare for contract award\n\n"
        else:
            email += "❌ **Missing or Incomplete Items:**\n"
            for problem in problems:
                if problem == 'missing_uei':
                    email += "- Unique Entity Identifier (UEI)\n"
                elif problem == 'missing_duns':
                    email += "- DUNS number\n"
                elif problem == 'sam_not_active':
                    email += "- Active SAM.gov registration\n"
                elif problem == 'past_performance_min_value_not_met':
                    email += "- Past performance project ≥ $25,000\n"
                elif problem == 'pricing_incomplete':
                    email += "- Complete pricing information with rates and units\n"
            
            email += "\n**Next Steps:**\n"
            email += "1. Provide missing documentation\n"
            email += "2. Update incomplete information\n"
            email += "3. Resubmit for review\n\n"
        
        email += "Please contact us if you have any questions or need assistance with these requirements.\n\n"
        email += "Best regards,\nGSA Review Team"
        
        return email
    
    async def _llm_generate_client_email(self, parsed_data: Dict[str, Any], checklist: Dict[str, Any]) -> str:
        """Real LLM email generation (placeholder)"""
        return "LLM-generated email would appear here"
