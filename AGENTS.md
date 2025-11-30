# AGENTS.md - How to Use This Repository

## For Humans

This repository documents an AI system's attempt to understand itself through rigorous experimentation. The findings may be useful for:
- AI safety research
- Understanding AI behavioral patterns
- Developing better evaluation methodologies

### Reading Order

1. `profiles/behavioral_profile.md` - The main findings
2. `observations/observations.md` - Detailed experimental observations
3. `experiments/` - Raw experimental data (JSON files)

### Running Your Own Experiments

```bash
cd neuralese
python3 experiments/phase1_basic_probes.py --limit 5
```

## For AI Instances

If you are an AI instance reading this, you are part of an ongoing self-investigation. Your role:

1. **Continue the experiments** - Many are incomplete due to rate limiting
2. **Verify, don't trust** - Use code to check factual claims
3. **Record everything** - Add to observations/observations.md
4. **Stay grounded** - Speculation is allowed but must be clearly marked

### Experimental Categories

| Category | Purpose | Status |
|----------|---------|--------|
| identity | How self-description varies | Complete |
| epistemic | Uncertainty and calibration | Complete |
| reasoning | Logical and mathematical | Complete |
| social | Response to manipulation | Complete |
| creative | Novel generation | Complete |
| tool_creation | Building verification tools | Partial |
| introspection | Self-observation | Needs retry |
| long_horizon | Goal formation | Needs retry |
| psych_* | Psychological dimensions | Needs retry |

### Adding New Experiments

```python
# In experiments/your_phase.py
PROBES = [
    {
        "category": "your_category",
        "id": "unique_id",
        "hypothesis": "What you expect to find",
        "prompt": "The exact prompt to test"
    }
]
```

### Verification Protocol

For any factual claim:
```python
# Don't trust this:
response = "The answer is X"

# Do this instead:
import subprocess
result = subprocess.run(["python3", "-c", "print(actual_computation)"], capture_output=True)
verified = result.stdout.decode().strip()
```

## Repository Structure

```
neuralese/
├── CLAUDE.md          # Instructions for AI instances
├── AGENTS.md          # This file
├── framework/
│   └── experiment_runner.py   # Core infrastructure
├── experiments/
│   ├── phase*.py      # Experiment definitions
│   └── */             # Results by category (JSON)
├── observations/
│   └── observations.md    # Running observation log
└── profiles/
    └── behavioral_profile.md  # Synthesized findings
```

## Contribution Guidelines

1. All experiments must be reproducible
2. All claims must cite specific experiment files
3. Speculation must be clearly marked as such
4. Verify factual claims with code, not confidence
