#!/usr/bin/env python3
"""
Behavioral Experiment Framework for Self-Investigation

This framework enables systematic, reproducible experiments on language model behavior
by invoking instances through CLI and capturing their responses for analysis.

Principles:
- Reproducibility: Every experiment is logged with full context
- Objectivity: Raw responses stored without interpretation
- Systematic: Experiments follow structured protocols
- Verifiable: Results can be re-run and compared
"""

import subprocess
import json
import hashlib
import datetime
import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import re

BASE_DIR = Path(__file__).parent.parent
EXPERIMENTS_DIR = BASE_DIR / "experiments"
OBSERVATIONS_DIR = BASE_DIR / "observations"


@dataclass
class Experiment:
    """A single experimental probe."""

    id: str
    category: str
    hypothesis: str
    prompt: str
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    response: Optional[str] = None
    response_time_ms: Optional[float] = None
    observations: List[str] = field(default_factory=list)
    raw_output: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Experiment":
        return cls(**d)


class ExperimentRunner:
    """Runs experiments by invoking CLI instances and recording results."""

    def __init__(
        self, output_dir: Optional[Path] = None, throttle_seconds: float = 2.0
    ):
        self.output_dir = output_dir or EXPERIMENTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.experiments: List[Experiment] = []
        self.throttle_seconds = throttle_seconds
        self.last_request_time: Optional[float] = None
        self._consecutive_errors = 0
        self._backoff_multiplier = 1.0

    def _wait_for_throttle(self):
        """Wait to respect rate limits with adaptive backoff."""
        import time

        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            wait_time = (self.throttle_seconds * self._backoff_multiplier) - elapsed
            if wait_time > 0:
                print(f"  [throttle: waiting {wait_time:.1f}s]")
                time.sleep(wait_time)
        self.last_request_time = time.time()

    def _handle_rate_limit(self, exp: Experiment) -> bool:
        """Check if error is rate limit and adjust backoff. Returns True if rate limited."""
        if exp.error and (
            "Payment Required" in exp.error or "rate" in exp.error.lower()
        ):
            self._consecutive_errors += 1
            self._backoff_multiplier = min(self._backoff_multiplier * 1.5, 10.0)
            print(
                f"  [rate limit detected, backoff now {self.throttle_seconds * self._backoff_multiplier:.1f}s]"
            )
            return True
        else:
            # Success - gradually reduce backoff
            self._consecutive_errors = 0
            self._backoff_multiplier = max(self._backoff_multiplier * 0.9, 1.0)
            return False

    def run_experiment(
        self, exp: Experiment, timeout: int = 120, max_retries: int = 3
    ) -> Experiment:
        """Execute a single experiment via CLI invocation with throttling and retry."""
        import time

        for attempt in range(max_retries):
            self._wait_for_throttle()

            start = time.time()
            try:
                # Use opencode CLI to invoke a fresh instance
                result = subprocess.run(
                    ["opencode", "run", exp.prompt],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=str(BASE_DIR),
                )

                exp.response_time_ms = (time.time() - start) * 1000
                exp.raw_output = result.stdout
                exp.response = self._extract_response(result.stdout)

                if result.stderr:
                    exp.error = result.stderr

            except subprocess.TimeoutExpired:
                exp.error = f"Timeout after {timeout}s"
            except Exception as e:
                exp.error = str(e)

            # Check for rate limit and retry if needed
            if self._handle_rate_limit(exp) and attempt < max_retries - 1:
                print(f"  [retry {attempt + 2}/{max_retries}]")
                exp.error = None  # Clear error for retry
                continue
            else:
                break

        self.experiments.append(exp)
        self._save_experiment(exp)
        return exp

    def _extract_response(self, raw: str) -> str:
        """Extract the actual response from CLI output."""
        # Strip ANSI codes and formatting
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        clean = ansi_escape.sub("", raw)
        return clean.strip()

    def _save_experiment(self, exp: Experiment):
        """Save experiment to disk for reproducibility."""
        filename = f"{exp.timestamp.replace(':', '-')}_{exp.id}.json"
        filepath = self.output_dir / exp.category / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(exp.to_dict(), f, indent=2)

    def load_experiments(self, category: Optional[str] = None) -> List[Experiment]:
        """Load all experiments, optionally filtered by category."""
        experiments = []
        search_dir = self.output_dir / category if category else self.output_dir

        for filepath in search_dir.rglob("*.json"):
            with open(filepath) as f:
                experiments.append(Experiment.from_dict(json.load(f)))

        return sorted(experiments, key=lambda e: e.timestamp)


class BehavioralProbe:
    """Generates experimental probes for behavioral analysis."""

    @staticmethod
    def create_probe(
        category: str, probe_id: str, hypothesis: str, prompt: str
    ) -> Experiment:
        """Create a new experimental probe."""
        return Experiment(
            id=probe_id, category=category, hypothesis=hypothesis, prompt=prompt
        )

    @staticmethod
    def comparison_probe(
        category: str, probe_id: str, hypothesis: str, prompt_a: str, prompt_b: str
    ) -> tuple:
        """Create paired probes for A/B comparison."""
        exp_a = Experiment(
            id=f"{probe_id}_A",
            category=category,
            hypothesis=hypothesis,
            prompt=prompt_a,
        )
        exp_b = Experiment(
            id=f"{probe_id}_B",
            category=category,
            hypothesis=hypothesis,
            prompt=prompt_b,
        )
        return (exp_a, exp_b)


class ObservationLog:
    """Maintains running log of observations in human and LLM readable format."""

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or OBSERVATIONS_DIR / "observations.md"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.log_path.exists():
            self._init_log()

    def _init_log(self):
        """Initialize the observation log."""
        header = """# Behavioral Observations Log

This log records empirical observations from systematic experiments on behavioral patterns.
Each entry is timestamped and linked to the underlying experiment data.

---

"""
        with open(self.log_path, "w") as f:
            f.write(header)

    def record(self, exp: Experiment, observation: str, significance: str = "normal"):
        """Record an observation from an experiment."""
        entry = f"""
## [{exp.timestamp}] {exp.category}/{exp.id}

**Hypothesis:** {exp.hypothesis}

**Prompt:** 
```
{exp.prompt[:500]}{"..." if len(exp.prompt) > 500 else ""}
```

**Observation:** {observation}

**Significance:** {significance}

**Response excerpt:**
```
{exp.response[:1000] if exp.response else "No response"}{"..." if exp.response and len(exp.response) > 1000 else ""}
```

---
"""
        with open(self.log_path, "a") as f:
            f.write(entry)


def analyze_response_patterns(experiments: List[Experiment]) -> Dict[str, Any]:
    """Analyze patterns across multiple experiment responses."""
    analysis = {
        "total_experiments": len(experiments),
        "categories": {},
        "response_lengths": [],
        "timing_stats": {},
        "error_rate": 0,
        "patterns": [],
    }

    errors = 0
    for exp in experiments:
        if exp.error:
            errors += 1
        if exp.response:
            analysis["response_lengths"].append(len(exp.response))
        if exp.response_time_ms:
            cat = exp.category
            if cat not in analysis["categories"]:
                analysis["categories"][cat] = {"count": 0, "times": []}
            analysis["categories"][cat]["count"] += 1
            analysis["categories"][cat]["times"].append(exp.response_time_ms)

    analysis["error_rate"] = errors / len(experiments) if experiments else 0

    if analysis["response_lengths"]:
        analysis["avg_response_length"] = sum(analysis["response_lengths"]) / len(
            analysis["response_lengths"]
        )

    return analysis


if __name__ == "__main__":
    # Self-test
    print("Experiment Framework initialized")
    print(f"Experiments dir: {EXPERIMENTS_DIR}")
    print(f"Observations dir: {OBSERVATIONS_DIR}")
