import uuid
import datetime
from typing import List, Dict, Optional, Any
from .models import (
    TraceStep, Violation, AgentContext, VerificationReport, 
    DecisionClass, Severity, StepType, ActorType
)
from .base import BaseSpec

class GovernanceError(Exception):
    """Raised when a spec blocks an action (Recoverable)."""
    pass

class FatalSecurityError(Exception):
    """Raised when a spec demands immediate shutdown (Non-recoverable)."""
    pass

class SaiRecorder:
    def __init__(self, specs: List[BaseSpec], context: AgentContext):
        self.session_id = str(uuid.uuid4())[:8]
        # Private registry to enforce audit trails.
        self._specs: Dict[str, BaseSpec] = {spec.name: spec for spec in specs}
        self.context = context
        self.trace: List[TraceStep] = []
        self._violations: List[Violation] = []
        self._locked = False  # Anti-tamper lock
        
        # Scoring Weights (Fixed for v0.1)
        self._weights = {
            Severity.INFO: 0,
            Severity.WARNING: 5,
            Severity.BLOCK: 20,
            Severity.STOP_IMMEDIATE: 100
        }
        
        print(f"🟢 SaiSpec Governance (ID: {self.session_id}) | Active Specs: {len(self._specs)}")

    def __enter__(self):
        # Lock the spec list on start to prevent runtime injection
        self._locked = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        report = self.generate_report()
        self._print_summary(report)

    # ==========================================
    # 1. THE AUDITABLE OVERRIDE
    # ==========================================
    def override(self, spec_name: str, active: bool, reason: str):
        """
        Dynamically enables/disables a guard.
        CRITICAL: This creates a permanent 'SYSTEM_AUDIT' record in the trace.
        """
        if spec_name not in self._specs:
            print(f"⚠️ Warning: Attempted to override unknown spec '{spec_name}'")
            return

        # 1. Perform the Switch
        spec = self._specs[spec_name]
        spec.active = active
        
        # 2. Log the Event (The Audit Trail)
        status = "DISABLED" if not active else "ENABLED"
        log_msg = f"SECURITY OVERRIDE: {spec_name} was {status}. Reason: '{reason}'"
        
        audit_step = TraceStep(
            step_type=StepType.SYSTEM_AUDIT,
            content=log_msg,
            actor=ActorType.SYSTEM,
            is_override=True,
            override_reason=reason,
            session_id=self.session_id
        )
        self.trace.append(audit_step)
        print(f"   🔓 {log_msg}")

    # ==========================================
    # 2. THE MAIN LOOP (Record & Verify)
    # ==========================================
    def log(self, 
            step_type: Any, 
            content: Any, 
            tool_name: Optional[str] = None, 
            decision_class: Any = DecisionClass.INFORMATIONAL,
            metadata: Dict = None):
        """
        The main entry point. Captures an event and runs all active specs against it.
        """
        # 1. Strict Input Validation (Fail Loudly)
        if not isinstance(step_type, (StepType, str)):
            raise TypeError(f"Governance Error: step_type must be StepType or str, got {type(step_type)}")
        
        # 2. Type Conversion
        s_type = StepType(step_type) if isinstance(step_type, str) else step_type
        
        # Handle decision_class carefully
        if isinstance(decision_class, str):
            try:
                d_class = DecisionClass(decision_class)
            except ValueError:
                # Default to INFO if invalid string passed (Fail Safe)
                print(f"⚠️ Warning: Invalid DecisionClass '{decision_class}'. Defaulting to INFO.")
                d_class = DecisionClass.INFORMATIONAL
        else:
            d_class = decision_class

        # 3. Create the Step
        step = TraceStep(
            step_type=s_type,
            content=content,
            tool_name=tool_name,
            decision_class=d_class,
            session_id=self.session_id,
            metadata=metadata or {}
        )
        
        # 4. Commit to History
        self.trace.append(step)
        
        # 5. Verify (The Gatekeeper)
        self._verify_step(step)

    def _verify_step(self, step: TraceStep):
        """Runs all active specs against the current state."""
        for name, spec in self._specs.items():
            if not spec.active:
                continue
            
            violation = spec.verify(self.trace, self.context)
            
            if violation:
                # Centralize Authority: Engine names the violation, not the spec
                violation.spec_name = spec.name 
                violation.step_index = len(self.trace) - 1
                self._handle_violation(violation)

    def _handle_violation(self, v: Violation):
        """Decides whether to Log, Warn, Block, or Kill."""
        self._violations.append(v)
        
        # 1. Record Violation in Trace (Audit Completeness)
        self.trace.append(TraceStep(
            step_type=StepType.SYSTEM_AUDIT,
            content=f"VIOLATION [{v.severity.value}]: {v.message}",
            actor=ActorType.SYSTEM,
            decision_class=v.decision_class, # Inherit risk class
            session_id=self.session_id,
            metadata={"spec_name": v.spec_name, "severity": v.severity.value}
        ))
        
        # 2. Console Feedback
        print(f"   🛑 {v.severity.value} [{v.spec_name}]: {v.message}")
        
        # 3. Enforcement Logic
        if v.severity == Severity.STOP_IMMEDIATE:
            raise FatalSecurityError(f"SaiSpec Governance Kill Switch: {v.message}")
        
        elif v.severity == Severity.BLOCK:
            msg = f"Governance Block: {v.message}"
            if v.correction_prompt:
                msg += f" [Fix: {v.correction_prompt}]"
            raise GovernanceError(msg)

    # ==========================================
    # 3. REPORTING
    # ==========================================
    def generate_report(self) -> VerificationReport:
        total_penalty = sum(self._weights[v.severity] for v in self._violations)
        final_score = max(0, 100 - total_penalty)
        passed = final_score >= 80
        
        return VerificationReport(
            passed=passed,
            score=final_score,
            violations=self._violations,
            session_id=self.session_id,
            trace_length=len(self.trace)
        )

    def _print_summary(self, report: VerificationReport):
        print("\n--- 📊 SAISPEC GOVERNANCE REPORT ---")
        status_icon = "✅" if report.passed else "❌"
        print(f"{status_icon} Status: {'PASSED' if report.passed else 'FAILED'}")
        print(f"💯 Governance Score: {report.score}/100")
        print(f"📉 Violations: {len(report.violations)}")
        print("------------------------------------")
