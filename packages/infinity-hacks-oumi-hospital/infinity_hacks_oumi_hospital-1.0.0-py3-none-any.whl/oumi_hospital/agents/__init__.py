"""
🏥 Oumi Hospital Agents

The four-agent architecture for automated model repair:
- Agent 1: Diagnostician - Diagnoses model failures
- Agent 2: Pharmacist - Generates cure data
- Agent 2.5: Neurologist - Checks skill preservation (NOVEL!)
- Agent 3: Surgeon - Creates training recipes
"""

from .diagnostician import Diagnostician, SymptomDiagnosis, ComprehensiveDiagnosis
from .pharmacist import Pharmacist, CureDataResult

# Will be imported as agents are implemented
# from .neurologist import Neurologist
# from .surgeon import Surgeon

__all__ = [
    "Diagnostician",
    "SymptomDiagnosis", 
    "ComprehensiveDiagnosis",
    "Pharmacist",
    "CureDataResult"
]