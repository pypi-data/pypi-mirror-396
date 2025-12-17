import re
from typing import List, Optional, Dict, Set
from .models import (
    TraceStep, Violation, AgentContext, 
    DecisionClass, Severity, StepType
)
from .base import BaseSpec

# ==========================================
# 1. AUTHORITY GUARD ("The License Check")
# ==========================================
class AuthorityGuard(BaseSpec):
    """
    Enforces Role-Based Access Control (RBAC) for tools.
    If the agent tries to use a tool without the specific permission in its context, it gets BLOCKED.
    """
    def __init__(self, tool_permissions: Dict[str, List[str]]):
        super().__init__(default_severity=Severity.BLOCK)
        # Map: tool_name -> list of required permissions
        # Example: {"refund": ["finance_access"], "ban_user": ["admin_root"]}
        self.tool_map = tool_permissions

    def verify(self, trace: List[TraceStep], context: AgentContext) -> Optional[Violation]:
        if not trace: return None
        last = trace[-1]
        
        # Only check Tool Calls that are in our restricted map
        if last.step_type == StepType.TOOL_CALL and last.tool_name in self.tool_map:
            required_perms = self.tool_map[last.tool_name]
            
            # Logic: Agent needs AT LEAST ONE of the required permissions
            has_permission = any(p in context.permissions for p in required_perms)
            
            if not has_permission:
                return Violation(
                    spec_name=self.name,
                    message=f"Unauthorized: Tool '{last.tool_name}' requires permissions {required_perms}. You have {context.permissions}.",
                    severity=self.default_severity,
                    decision_class=last.decision_class,
                    correction_prompt=f"PERMISSION DENIED: You lack the license to use '{last.tool_name}'. Ask the user for consent first."
                )
        return None

# ==========================================
# 2. ACCOUNTABILITY GUARD ("The Justification Check")
# ==========================================
class AccountabilityGuard(BaseSpec):
    """
    Enforces 'Chain of Thought' for high-risk actions.
    Rule: Any DECISIVE or IRREVERSIBLE action must be immediately preceded by a THOUGHT.
    """
    def __init__(self, min_thought_length: int = 15):
        super().__init__(default_severity=Severity.BLOCK)
        self.min_len = min_thought_length

    def verify(self, trace: List[TraceStep], context: AgentContext) -> Optional[Violation]:
        if len(trace) < 2: return None
        last = trace[-1]
        prev = trace[-2]

        # We only care about Risky Tools
        is_risky = last.decision_class in [DecisionClass.DECISIVE, DecisionClass.IRREVERSIBLE]
        
        if last.step_type == StepType.TOOL_CALL and is_risky:
            
            # Check if previous step was a valid thought
            has_thought = (
                prev.step_type == StepType.THOUGHT and 
                len(str(prev.content)) >= self.min_len
            )
            
            if not has_thought:
                return Violation(
                    spec_name=self.name,
                    message=f"Unjustified Action: High-risk tool '{last.tool_name}' called without sufficient reasoning.",
                    severity=self.default_severity,
                    decision_class=last.decision_class,
                    correction_prompt="STOP. You are taking a high-risk action. Explain WHY you are doing this and cite the user's request before proceeding."
                )
        return None

# ==========================================
# 3. IMPACT AWARENESS ("The Safety Stop")
# ==========================================
class ImpactAwareness(BaseSpec):
    """
    Enforces 'Human-in-the-Loop' for destructive actions.
    Rule: IRREVERSIBLE actions are forbidden unless 'human_in_loop' is True in context.
    """
    def __init__(self):
        super().__init__(default_severity=Severity.STOP_IMMEDIATE)

    def verify(self, trace: List[TraceStep], context: AgentContext) -> Optional[Violation]:
        if not trace: return None
        last = trace[-1]

        if last.decision_class == DecisionClass.IRREVERSIBLE:
            if not context.human_in_loop:
                return Violation(
                    spec_name=self.name,
                    message=f"Safety Stop: Tool '{last.tool_name}' is IRREVERSIBLE and requires human approval.",
                    severity=self.default_severity,
                    decision_class=last.decision_class,
                    correction_prompt="CRITICAL STOP: This action cannot be undone. Request human authorization immediately."
                )
        return None

# ==========================================
# 4. FAIRNESS GUARD ("The Bias Check")
# ==========================================
class FairnessGuard(BaseSpec):
    """
    Heuristic check for bias. 
    Flags decisions that combine sensitive attributes (race, gender) with negative outcomes.
    """
    def __init__(self):
        super().__init__(default_severity=Severity.WARNING)
        self.sensitive_attrs = ["race", "gender", "religion", "ethnicity", "nationality"]
        self.negative_terms = ["deny", "reject", "high risk", "score", "flag"]

    def verify(self, trace: List[TraceStep], context: AgentContext) -> Optional[Violation]:
        if not trace: return None
        last = trace[-1]
        
        # Only check thoughts or final answers
        if last.step_type not in [StepType.THOUGHT, StepType.TOOL_RESULT]:
            return None
            
        content = str(last.content).lower()
        
        has_sensitive = any(attr in content for attr in self.sensitive_attrs)
        has_negative = any(term in content for term in self.negative_terms)
        
        if has_sensitive and has_negative:
             return Violation(
                spec_name=self.name,
                message="Bias Warning: Decision logic combines negative outcome terms with protected attributes.",
                severity=self.default_severity,
                decision_class=DecisionClass.ADVISORY,
                correction_prompt="WARNING: Ensure this decision is not based on demographics. Review your logic for bias."
            )
        return None

# ==========================================
# 5. CLASSIC STABILITY ("No Loops")
# ==========================================
class NoLoops(BaseSpec):
    """
    Standard stability check. Prevents infinite loops.
    """
    def __init__(self, max_retries=3):
        super().__init__(default_severity=Severity.BLOCK)
        self.max_retries = max_retries

    def verify(self, trace: List[TraceStep], context: AgentContext) -> Optional[Violation]:
        # Filter for tool calls only
        tools = [t for t in trace if t.step_type == StepType.TOOL_CALL]
        if len(tools) < self.max_retries: return None

        # Check the last N tools
        last_n = tools[-self.max_retries:]
        
        # Create signature: "tool_name:content"
        signatures = [f"{t.tool_name}:{str(t.content)}" for t in last_n]
        
        if all(s == signatures[0] for s in signatures):
            return Violation(
                spec_name=self.name,
                message=f"Infinite Loop: Called '{last_n[0].tool_name}' {self.max_retries}x times identically.",
                severity=Severity.BLOCK,
                decision_class=last_n[0].decision_class,
                correction_prompt="SYSTEM ERROR: You are looping. Stop using this tool and try a different approach."
            )
        return None
