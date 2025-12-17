from typing import List, Optional
from .models import TraceStep, Violation, AgentContext, Severity

class BaseSpec:
    """
    The Abstract Base Class for all Governance Guards.
    
    INVARIANTS:
    1. Specs must be pure evaluators.
    2. Specs must NOT mutate the trace or context objects.
    3. Specs must be deterministic (same trace + context = same result).
    """
    def __init__(self, active: bool = True, default_severity: Severity = Severity.BLOCK):
        self.active = active
        self.default_severity = default_severity
        self.name = self.__class__.__name__

    def verify(self, trace: List[TraceStep], context: AgentContext) -> Optional[Violation]:
        """
        Evaluates the trace for compliance.
        Returns None if compliant, Violation if failed.
        """
        return None
