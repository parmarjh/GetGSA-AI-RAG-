import pytest
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return {
        "complete_profile": """
        Company Profile (A):
        Acme Robotics LLC
        UEI: ABC123DEF456
        DUNS: 123456789
        NAICS: 541511, 541512
        POC: Jane Smith, jane@acme.co, (415) 555-0100
        Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
        SAM.gov: registered
        """,
        
        "past_performance": """
        Past Performance (PP-1):
        Customer: City of Palo Verde
        Contract: Website modernization
        Value: $18,000
        Period: 07/2023 - 03/2024
        Contact: John Roe, cio@pverde.gov
        
        Past Performance (PP-2):
        Customer: State of Fremont
        Contract: Data migration & support
        Value: $82,500
        Period: 10/2022 - 02/2024
        Contact: sarah.lee@fremont.gov
        """,
        
        "pricing": """
        Pricing Sheet (text; simplified):
        Labor Category, Rate, Unit
        Senior Developer, 185, Hour
        Project Manager, 165, Hour
        """,
        
        "incomplete_profile": """
        Company Profile (A):
        Acme Robotics LLC
        UEI: ABC123DEF456
        DUNS: 123456789
        NAICS: 541511
        POC: Jane Smith, jane@acme.co, (415) 555-0100
        Address: 444 West Lake Street, Suite 1700, Chicago, IL 60606
        SAM.gov: pending
        """
    }
