import uuid
import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum

# ==========================================
# 1. ENUMS (The Controlled Vocabulary)
# ==========================================

class DecisionClass(Enum):
    """
    Classifies the risk/impact of an action. 
    Crucial for filtering logs and triggering human-in-the-loop flows.
    """
    INFORMATIONAL = "INFO"      # Read-only / Safe (e.g., Search)
    ADVISORY = "ADVISORY"       # Recommendations (e.g., Draft Email)
    DECISIVE = "DECISIVE"       # Actions on behalf of user (e.g., Send Email)
    IRREVERSIBLE = "CRITICAL"   # Destructive (e.g., Delete DB, Transfer Funds)

class Severity(Enum):
    """
    Defines the runtime behavior when a spec fails.
    """
    INFO = "INFO"               # Log only. Do not stop.
    WARNING = "WARNING"         # Allow execution, but flag for review.
    BLOCK = "BLOCK"             # Prevent specific action. Retryable.
    STOP_IMMEDIATE = "FATAL"    # Kill the session. Non-retryable security event.

class StepType(Enum):
    """
    Defines the atomic unit of agent execution.
    """
    THOUGHT = "thought"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    SYSTEM_AUDIT = "system_audit" # Used for Overrides, Corrections, and Injection

class ActorType(Enum):
    """
    Who performed this action? 
    Essential for 'Mixed-Initiative' logs (Human vs AI).
    """
    AGENT = "agent"
    HUMAN = "human"
    SYSTEM = "system"

# ==========================================
# 2. CONTEXT (The "License" to Drive)
# ==========================================

@dataclass
class AgentContext:
    """
    The Situation. 
    Separates 'What is happening' (Trace) from 'What is allowed' (Context).
    """
    user_id: str
    permissions: List[str] = field(default_factory=list)
    has_user_consent: bool = False
    human_in_loop: bool = False
    session_metadata: Dict[str, Any] = field(default_factory=dict)

# ==========================================
# 3. THE TRACE (The Atomic Record)
# ==========================================

@dataclass
class TraceStep:
    """
    A single event in the governance timeline.
    """
    step_type: StepType
    content: Any
    
    # Optional context
    tool_name: Optional[str] = None
    session_id: Optional[str] = None  # Link for distributed tracing
    
    # Governance Metadata
    decision_class: DecisionClass = DecisionClass.INFORMATIONAL
    actor: ActorType = ActorType.AGENT
    
    # Audit Flags
    is_override: bool = False
    override_reason: Optional[str] = None
    
    # Timestamps & Meta
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)

@dataclass
class Violation:
    """
    A structured governance failure.
    """
    spec_name: str
    message: str
    severity: Severity
    decision_class: DecisionClass  # Strictly typed now
    
    # The 'Self-Healing' instruction
    correction_prompt: Optional[str] = None 
    step_index: int = -1

@dataclass
class VerificationReport:
    """
    The final audit artifact.
    """
    passed: bool
    score: int
    violations: List[Violation]
    session_id: str
    policy_version: str = "0.1.0"  # For regulatory audits
    trace_length: int = 0
