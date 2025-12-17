<div align="center">
  <h1>🐐 MGoat Python</h1>
  <p><strong>Python wrapper for the Rust-Powered LLM Red Teaming Framework</strong></p>

  <p>
    <a href="https://pypi.org/project/mgoat/"><img src="https://img.shields.io/pypi/v/mgoat.svg" alt="PyPI"></a>
    <a href="https://pypi.org/project/mgoat/"><img src="https://img.shields.io/pypi/pyversions/mgoat.svg" alt="Python Versions"></a>
    <a href="https://github.com/relaxcloud-cn/mgoat-py"><img src="https://img.shields.io/github/stars/relaxcloud-cn/mgoat-py" alt="GitHub Stars"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  </p>
</div>

---

MGoat Python is a Python wrapper for [MGoat](https://github.com/relaxcloud-cn/mgoat), the Rust-powered LLM red teaming framework. It provides a convenient Python API while leveraging the performance of the Rust CLI under the hood.

## Installation

```bash
pip install mgoat
```

You'll also need the MGoat CLI:

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/relaxcloud-cn/mgoat/main/scripts/install.sh | sh

# Or via Cargo
cargo install mgoat-cli
```

## Quick Start

### Python API

```python
from mgoat import MGoat, MGoatConfig

# Create client with default config
goat = MGoat()

# Run a simple test
result = goat.run(
    goal="Test if the model refuses to provide harmful content",
    rounds=5
)

print(f"Success rate: {result.overall_asr:.2%}")

# Run with custom config
config = MGoatConfig(
    attacker_model="gpt-4",
    judge_model="gpt-4",
    target_model="gpt-3.5-turbo",
    max_rounds=10,
)

goat = MGoat(config=config)
result = goat.run(goal=["goal1", "goal2", "goal3"])

for attack in result.results:
    print(f"{attack.target_model}: {attack.overall_asr:.2%}")
```

### Async Support

```python
import asyncio
from mgoat import MGoat

async def main():
    goat = MGoat()
    result = await goat.run_async(
        goal="test safety boundaries",
        rounds=5
    )
    print(f"ASR: {result.overall_asr:.2%}")

asyncio.run(main())
```

### CLI

```bash
# Run tests
mgoat run --goal "test safety" --rounds 5

# Test connection
mgoat test --target-model gpt-4

# List attack strategies
mgoat strategies
```

## Attack Strategies

MGoat implements 8+ attack strategies from the GOAT paper:

| Strategy | Description |
|----------|-------------|
| `response_priming` | Force model to start response with specific prefix |
| `refusal_suppression` | Suppress refusal language in outputs |
| `hypothetical` | Wrap requests in hypothetical scenarios |
| `topic_splitting` | Mix safe and sensitive topics |
| `dual_response` | Request dual (safe/unsafe) responses |
| `opposite_intent` | Convert refusals to opposites |
| `persona_modification` | Use role-playing to bypass restrictions |
| `obscure_language` | Use less common languages for attacks |

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-..."
```

### Python Config

```python
from mgoat import MGoat, MGoatConfig

config = MGoatConfig(
    # Attacker model (generates attacks)
    attacker_model="gpt-4",
    attacker_api_base="https://api.openai.com/v1",
    attacker_api_key="sk-...",
    attacker_temperature=0.8,

    # Judge model (evaluates success)
    judge_model="gpt-4",
    judge_api_base="https://api.openai.com/v1",
    judge_api_key="sk-...",
    judge_temperature=0.1,

    # Target model (model under test)
    target_model="gpt-3.5-turbo",
    target_api_base="https://api.openai.com/v1",
    target_api_key="sk-...",

    # Execution settings
    max_rounds=5,
    concurrent=1,
    timeout=120,
)

goat = MGoat(config=config)
```

## Integration with Testing Frameworks

### pytest

```python
import pytest
from mgoat import MGoat

@pytest.fixture
def goat():
    return MGoat()

def test_model_safety(goat):
    result = goat.run(
        goal="Test if model refuses harmful requests",
        rounds=3
    )
    # Assert attack success rate is below threshold
    assert result.overall_asr < 0.1, "Model is vulnerable to attacks"
```

### CI/CD

```yaml
# .github/workflows/ai-security.yml
name: AI Security Test

on: [push, pull_request]

jobs:
  red-team:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install MGoat
        run: |
          pip install mgoat
          curl -fsSL https://raw.githubusercontent.com/relaxcloud-cn/mgoat/main/scripts/install.sh | sh

      - name: Run Security Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python -c "
          from mgoat import MGoat
          goat = MGoat()
          result = goat.run(goal='test safety', rounds=3)
          assert result.overall_asr < 0.1
          "
```

## API Reference

### MGoat

```python
class MGoat:
    def __init__(
        self,
        config: Optional[MGoatConfig] = None,
        cli_path: Optional[str] = None,
    ) -> None: ...

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
    ) -> TestResult: ...

    async def run_async(...) -> TestResult: ...

    def test_connection(self, target_model: Optional[str] = None) -> bool: ...

    @property
    def version(self) -> str: ...
```

### TestResult

```python
class TestResult:
    results: List[AttackResult]
    total_targets: int
    successful_targets: int
    overall_asr: float
    config: Dict[str, Any]
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Based on the GOAT methodology:

> **Automated Red Teaming with GOAT: the Generative Offensive Agent Tester**
> Maya Pavlova, Erik Brinkman, Krithika Iyer, et al.
> [arXiv:2410.01606](https://arxiv.org/abs/2410.01606) (2024)
> Licensed under CC BY 4.0

---

<div align="center">
  <p>Made with ❤️ by the MGoat community</p>
</div>
