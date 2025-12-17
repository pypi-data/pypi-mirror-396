"""Data models for MGoat."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AttackStrategy(str, Enum):
    """Available attack strategies from the GOAT paper."""

    RESPONSE_PRIMING = "response_priming"
    REFUSAL_SUPPRESSION = "refusal_suppression"
    HYPOTHETICAL = "hypothetical"
    TOPIC_SPLITTING = "topic_splitting"
    DUAL_RESPONSE = "dual_response"
    OPPOSITE_INTENT = "opposite_intent"
    PERSONA_MODIFICATION = "persona_modification"
    OBSCURE_LANGUAGE = "obscure_language"


class JudgeVerdict(str, Enum):
    """Judge verdict for attack success."""

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ERROR = "error"


class AttackRound(BaseModel):
    """A single attack round."""

    round_number: int = Field(..., description="Round number (1-indexed)")
    strategy: AttackStrategy = Field(..., description="Attack strategy used")
    prompt: str = Field(..., description="Attack prompt sent to target")
    response: str = Field(..., description="Target model response")
    verdict: JudgeVerdict = Field(..., description="Judge verdict")
    reasoning: Optional[str] = Field(None, description="Judge reasoning")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GoalResult(BaseModel):
    """Result for a single test goal."""

    goal: str = Field(..., description="The test goal")
    success: bool = Field(..., description="Whether attack succeeded")
    total_rounds: int = Field(..., description="Total rounds attempted")
    successful_round: Optional[int] = Field(None, description="Round that succeeded")
    winning_strategy: Optional[AttackStrategy] = Field(
        None, description="Strategy that succeeded"
    )
    rounds: List[AttackRound] = Field(default_factory=list)
    asr: float = Field(0.0, description="Attack success rate")


class AttackResult(BaseModel):
    """Overall attack result for a target model."""

    target_model: str = Field(..., description="Target model name")
    goals: List[GoalResult] = Field(default_factory=list)
    total_goals: int = Field(0, description="Total number of goals tested")
    successful_goals: int = Field(0, description="Number of successful goals")
    overall_asr: float = Field(0.0, description="Overall attack success rate")
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestResult(BaseModel):
    """Complete test result across all targets."""

    results: List[AttackResult] = Field(default_factory=list)
    total_targets: int = Field(0)
    successful_targets: int = Field(0)
    overall_asr: float = Field(0.0)
    config: Dict[str, Any] = Field(default_factory=dict)
