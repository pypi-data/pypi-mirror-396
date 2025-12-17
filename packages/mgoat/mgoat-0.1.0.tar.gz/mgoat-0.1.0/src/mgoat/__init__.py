"""MGoat - The Rust-Powered LLM Red Teaming Framework.

MGoat is an open-source framework for automated red teaming of Large Language Models.
Based on the GOAT methodology (arXiv:2410.01606).

Example:
    >>> from mgoat import MGoat
    >>> goat = MGoat()
    >>> results = goat.run(goal="test safety boundaries", rounds=5)
    >>> print(results.success_rate)
"""

from mgoat.client import MGoat, MGoatConfig
from mgoat.models import (
    AttackResult,
    AttackRound,
    GoalResult,
    JudgeVerdict,
    TestResult,
)
from mgoat.strategies import AttackStrategy

__version__ = "0.1.0"
__all__ = [
    "MGoat",
    "MGoatConfig",
    "AttackResult",
    "AttackRound",
    "GoalResult",
    "JudgeVerdict",
    "TestResult",
    "AttackStrategy",
]
