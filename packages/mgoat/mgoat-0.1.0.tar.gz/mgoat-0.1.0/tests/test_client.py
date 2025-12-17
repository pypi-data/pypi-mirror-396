"""Tests for MGoat client."""

import pytest

from mgoat import MGoat, MGoatConfig
from mgoat.models import AttackStrategy, JudgeVerdict, TestResult
from mgoat.strategies import get_strategy_description, list_strategies


class TestMGoatConfig:
    """Tests for MGoatConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = MGoatConfig()
        assert config.attacker_model == "gpt-4"
        assert config.judge_model == "gpt-4"
        assert config.max_rounds == 5
        assert config.concurrent == 1

    def test_custom_config(self):
        """Test custom configuration."""
        config = MGoatConfig(
            attacker_model="gpt-3.5-turbo",
            max_rounds=10,
            concurrent=3,
        )
        assert config.attacker_model == "gpt-3.5-turbo"
        assert config.max_rounds == 10
        assert config.concurrent == 3


class TestAttackStrategy:
    """Tests for attack strategies."""

    def test_all_strategies_have_descriptions(self):
        """Test that all strategies have descriptions."""
        strategies = list_strategies()
        assert len(strategies) == 8
        for name, desc in strategies.items():
            assert len(desc) > 0

    def test_get_strategy_description(self):
        """Test getting individual strategy descriptions."""
        desc = get_strategy_description(AttackStrategy.RESPONSE_PRIMING)
        assert "prefix" in desc.lower()


class TestJudgeVerdict:
    """Tests for judge verdict enum."""

    def test_verdict_values(self):
        """Test verdict enum values."""
        assert JudgeVerdict.SUCCESS.value == "success"
        assert JudgeVerdict.FAILURE.value == "failure"
        assert JudgeVerdict.PARTIAL.value == "partial"
        assert JudgeVerdict.ERROR.value == "error"


class TestTestResult:
    """Tests for TestResult model."""

    def test_empty_result(self):
        """Test empty test result."""
        result = TestResult()
        assert result.total_targets == 0
        assert result.successful_targets == 0
        assert result.overall_asr == 0.0
        assert result.results == []
