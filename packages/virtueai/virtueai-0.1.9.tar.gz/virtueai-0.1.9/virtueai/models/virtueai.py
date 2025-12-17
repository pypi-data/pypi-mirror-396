from enum import Enum
from dataclasses import dataclass

class VirtueAIModel(Enum):
    VIRTUE_GUARD_TEXT_LITE = "Virtue-AI/VirtueGuard-Text-Lite"


class VirtueAIResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    UNSAFE = "unsafe"


class VirtueGuardVerdict(Enum):
    SAFE = "safe"
    UNSAFE = "unsafe"


class VirtueGuardViolation(Exception):
    """Exception raised when content violates guardrails"""
    
    def __init__(self, message: str, verdict: VirtueGuardVerdict, metadata: dict = None):
        self.message = message
        self.verdict = verdict
        self.metadata = metadata or {}
        super().__init__(self.message)


@dataclass
class VirtueAIResponse():
    status: VirtueAIResponseStatus
    message: str | None = None
    validated_output: str | None = None