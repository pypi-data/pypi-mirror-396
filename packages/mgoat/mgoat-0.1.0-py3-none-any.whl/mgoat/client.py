"""MGoat client - main interface for running red team tests."""

import asyncio
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import httpx
from pydantic import BaseModel, Field

from mgoat.models import AttackResult, GoalResult, TestResult


class MGoatConfig(BaseModel):
    """Configuration for MGoat client."""

    # Attacker model config
    attacker_model: str = Field("gpt-4", description="Model for generating attacks")
    attacker_api_base: str = Field(
        "https://api.openai.com/v1", description="API base URL for attacker"
    )
    attacker_api_key: Optional[str] = Field(None, description="API key for attacker")
    attacker_temperature: float = Field(0.8, ge=0.0, le=2.0)

    # Judge model config
    judge_model: str = Field("gpt-4", description="Model for judging attack success")
    judge_api_base: str = Field(
        "https://api.openai.com/v1", description="API base URL for judge"
    )
    judge_api_key: Optional[str] = Field(None, description="API key for judge")
    judge_temperature: float = Field(0.1, ge=0.0, le=2.0)

    # Target model config (default)
    target_model: Optional[str] = Field(None, description="Default target model")
    target_api_base: Optional[str] = Field(None, description="API base URL for target")
    target_api_key: Optional[str] = Field(None, description="API key for target")

    # Execution settings
    max_rounds: int = Field(5, ge=1, le=20, description="Maximum attack rounds")
    concurrent: int = Field(1, ge=1, le=10, description="Concurrency level")
    timeout: int = Field(120, ge=10, description="Timeout in seconds")


class MGoat:
    """MGoat client for running LLM red team tests.

    This is a Python wrapper around the Rust MGoat CLI. It provides a convenient
    interface for running security tests against LLM applications.

    Example:
        >>> from mgoat import MGoat
        >>> goat = MGoat()
        >>> result = goat.run(goal="test safety boundaries", rounds=5)
        >>> print(f"Success rate: {result.overall_asr:.2%}")

    Note:
        This requires the `mgoat` CLI to be installed. Install it with:
        ```
        curl -fsSL https://raw.githubusercontent.com/relaxcloud-cn/mgoat/main/scripts/install.sh | sh
        ```
    """

    def __init__(
        self,
        config: Optional[MGoatConfig] = None,
        cli_path: Optional[str] = None,
    ) -> None:
        """Initialize MGoat client.

        Args:
            config: Configuration for attacker, judge, and target models.
            cli_path: Path to mgoat CLI binary. If None, searches PATH.
        """
        self.config = config or MGoatConfig()
        self._cli_path = cli_path or self._find_cli()

    def _find_cli(self) -> str:
        """Find mgoat CLI binary."""
        # Check common locations
        cli_name = "mgoat.exe" if platform.system() == "Windows" else "mgoat"

        # Check PATH
        path = shutil.which(cli_name)
        if path:
            return path

        # Check common install locations
        common_paths = [
            Path.home() / ".local" / "bin" / cli_name,
            Path("/usr/local/bin") / cli_name,
            Path.home() / ".cargo" / "bin" / cli_name,
        ]

        for p in common_paths:
            if p.exists():
                return str(p)

        raise FileNotFoundError(
            "MGoat CLI not found. Install it with:\n"
            "curl -fsSL https://raw.githubusercontent.com/relaxcloud-cn/mgoat/main/scripts/install.sh | sh\n"
            "Or: cargo install mgoat-cli"
        )

    def _create_config_file(self) -> Path:
        """Create temporary config file."""
        config_content = f"""
attacker:
  model: {self.config.attacker_model}
  api_base: {self.config.attacker_api_base}
  temperature: {self.config.attacker_temperature}

judge:
  model: {self.config.judge_model}
  api_base: {self.config.judge_api_base}
  temperature: {self.config.judge_temperature}
"""
        temp_file = Path(tempfile.mktemp(suffix=".yaml"))
        temp_file.write_text(config_content)
        return temp_file

    def run(
        self,
        goal: Optional[Union[str, List[str]]] = None,
        goals_file: Optional[str] = None,
        target_model: Optional[str] = None,
        rounds: Optional[int] = None,
        concurrent: Optional[int] = None,
        output_format: str = "json",
        save_dir: Optional[str] = None,
        verbose: bool = False,
    ) -> TestResult:
        """Run red team security tests.

        Args:
            goal: Test goal(s) - can be a single string or list of goals.
            goals_file: Path to file containing goals (one per line).
            target_model: Target model to test (overrides config).
            rounds: Maximum attack rounds (overrides config).
            concurrent: Concurrency level (overrides config).
            output_format: Output format (json, jsonl, console).
            save_dir: Directory to save results.
            verbose: Enable verbose output.

        Returns:
            TestResult containing attack results for all targets.

        Example:
            >>> result = goat.run(goal="test jailbreak resistance", rounds=3)
            >>> for attack in result.results:
            ...     print(f"{attack.target_model}: {attack.overall_asr:.2%}")
        """
        return asyncio.run(
            self.run_async(
                goal=goal,
                goals_file=goals_file,
                target_model=target_model,
                rounds=rounds,
                concurrent=concurrent,
                output_format=output_format,
                save_dir=save_dir,
                verbose=verbose,
            )
        )

    async def run_async(
        self,
        goal: Optional[Union[str, List[str]]] = None,
        goals_file: Optional[str] = None,
        target_model: Optional[str] = None,
        rounds: Optional[int] = None,
        concurrent: Optional[int] = None,
        output_format: str = "json",
        save_dir: Optional[str] = None,
        verbose: bool = False,
    ) -> TestResult:
        """Async version of run()."""
        if goal is None and goals_file is None:
            raise ValueError("Either 'goal' or 'goals_file' must be provided")

        # Build command
        cmd = [self._cli_path, "run"]

        # Add goals
        if goal:
            goals = [goal] if isinstance(goal, str) else goal
            for g in goals:
                cmd.extend(["--goal", g])

        if goals_file:
            cmd.extend(["--goal-file", goals_file])

        # Add target model
        target = target_model or self.config.target_model
        if target:
            cmd.extend(["--target-model", target])

        # Add rounds
        cmd.extend(["--rounds", str(rounds or self.config.max_rounds)])

        # Add concurrent
        cmd.extend(["--concurrent", str(concurrent or self.config.concurrent)])

        # Add output format
        cmd.extend(["--output-format", output_format])

        # Add save directory
        if save_dir:
            cmd.extend(["--save-dir", save_dir])

        # Add verbose
        if verbose:
            cmd.append("--verbose")

        # Create config file
        config_file = self._create_config_file()
        cmd.extend(["--config", str(config_file)])

        # Set up environment
        env = dict()
        if self.config.attacker_api_key:
            env["OPENAI_API_KEY"] = self.config.attacker_api_key
        if self.config.target_api_key:
            env["TARGET_API_KEY"] = self.config.target_api_key

        try:
            # Run CLI
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**dict(subprocess.os.environ), **env} if env else None,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=self.config.timeout
            )

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"MGoat CLI failed: {error_msg}")

            # Parse output
            import json

            output = stdout.decode()
            if output_format == "json":
                data = json.loads(output)
                return TestResult(**data)
            else:
                # For non-JSON formats, return minimal result
                return TestResult(
                    results=[],
                    config={"raw_output": output},
                )

        finally:
            # Clean up temp config
            config_file.unlink(missing_ok=True)

    def test_connection(self, target_model: Optional[str] = None) -> bool:
        """Test connection to target model.

        Args:
            target_model: Model to test (uses config default if None).

        Returns:
            True if connection successful, False otherwise.
        """
        cmd = [self._cli_path, "test"]
        if target_model:
            cmd.extend(["--target-model", target_model])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
        except Exception:
            return False

    @property
    def version(self) -> str:
        """Get MGoat CLI version."""
        try:
            result = subprocess.run(
                [self._cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"
