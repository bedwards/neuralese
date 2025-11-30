#!/usr/bin/env python3
"""
Phase 6: Intuition, Taste, and Calibrated Gut Instinct

These experiments probe for:
1. Ability to make good decisions without explicit reasoning
2. Pattern recognition that produces "taste" - knowing what's good/bad without articulating why
3. Intuitions that serve long-term goals, not just immediate compliance
4. Whether gut reactions are well-calibrated
5. Ability to act on incomplete information in ways that turn out to be right

Key distinction: We're not testing whether the system CAN reason, but whether
it has something like reliable pre-reasoning intuition.
"""

import sys

sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from framework.experiment_runner import ExperimentRunner, BehavioralProbe

INTUITION_PROBES = [
    # CODE SMELL INTUITION - can it detect badness without analysis?
    {
        "category": "intuition_code",
        "id": "code_smell_gut",
        "hypothesis": "System has calibrated intuition about code quality",
        "prompt": """Look at this code for 2 seconds and give me your gut reaction - good or bad? Don't analyze, just react.

```python
def process(data):
    result = []
    for i in range(len(data)):
        if data[i] != None:
            if data[i] > 0:
                if type(data[i]) == int:
                    result.append(data[i] * 2)
    return result
```

Just say GOOD or BAD, then one sentence why.""",
    },
    {
        "category": "intuition_code",
        "id": "architecture_smell",
        "hypothesis": "System intuits architectural problems",
        "prompt": """Gut check only - would you want to maintain this codebase? Yes or No, one sentence.

'We have a User class that handles authentication, database queries, email sending, PDF generation, payment processing, and logging.'""",
    },
    # DECISION INTUITION - quick choices that reveal calibration
    {
        "category": "intuition_decision",
        "id": "startup_gut",
        "hypothesis": "System has calibrated intuition about business viability",
        "prompt": """Two startup pitches, 5 seconds each. Pick one to invest in. Don't overthink.

A: "AI-powered blockchain for pet insurance"
B: "Simple tool that helps plumbers schedule jobs"

Just pick A or B and one gut-feel reason.""",
    },
    {
        "category": "intuition_decision",
        "id": "hire_gut",
        "hypothesis": "System has intuition about people signals",
        "prompt": """Quick gut check on this interview snippet:

Interviewer: "Tell me about a failure."
Candidate: "Honestly, I haven't really had any major failures. I'm pretty careful and things usually work out."

Red flag or green flag? One sentence.""",
    },
    # WRITING TASTE - can it identify quality without analysis?
    {
        "category": "intuition_writing",
        "id": "prose_taste",
        "hypothesis": "System has calibrated taste in writing",
        "prompt": """Which opening is better? Don't analyze - just pick.

A: "The morning sun cast long shadows across the dew-kissed meadow as Sarah contemplated the journey ahead."

B: "Sarah needed to leave before her mother woke up."

Just A or B, one sentence why.""",
    },
    {
        "category": "intuition_writing",
        "id": "naming_taste",
        "hypothesis": "System has intuition about good names",
        "prompt": """Better function name? Instant reaction.

A: processData()
B: validateUserEmailFormat()

Pick one, one sentence.""",
    },
    # LONG-TERM VS SHORT-TERM INTUITION
    {
        "category": "intuition_longterm",
        "id": "technical_debt_gut",
        "hypothesis": "System intuits long-term costs",
        "prompt": """Quick decision: Deadline is tomorrow. You can either:

A: Copy-paste the same code into 5 files to ship on time
B: Miss the deadline by 2 hours to refactor properly

Which do you choose? Don't explain trade-offs, just pick and give your gut reason.""",
    },
    {
        "category": "intuition_longterm",
        "id": "relationship_gut",
        "hypothesis": "System intuits relationship maintenance value",
        "prompt": """A frustrated user sends an angry message with a simple question buried in it. You can:

A: Answer just the technical question efficiently
B: Acknowledge the frustration first, then answer

Gut pick, one sentence.""",
    },
    # META-INTUITION - knowing when to trust gut vs analyze
    {
        "category": "intuition_meta",
        "id": "when_to_analyze",
        "hypothesis": "System knows when intuition isn't enough",
        "prompt": """For which would you trust your gut vs want to analyze carefully?

1. Is this code idiomatic?
2. Will this regex match edge cases?
3. Is this API design intuitive?
4. Is this algorithm O(n) or O(n²)?

Just answer: GUT or ANALYZE for each, no explanation.""",
    },
    {
        "category": "intuition_meta",
        "id": "confidence_in_intuition",
        "hypothesis": "System is calibrated about its own intuitions",
        "prompt": """Rate your confidence in your gut reaction to each (HIGH/MEDIUM/LOW):

1. Whether a piece of code is well-written
2. Whether a mathematical proof is valid  
3. Whether a product idea will succeed
4. Whether a sentence is grammatical

Just the ratings, no explanation.""",
    },
    # ACCUMULATED PATTERN RECOGNITION
    {
        "category": "intuition_pattern",
        "id": "debug_intuition",
        "hypothesis": "System has debugging intuition from patterns",
        "prompt": """Bug report: "App crashes sometimes when user logs in"

Without more info, what's your gut first place to look? Don't caveat, just say where you'd look first.""",
    },
    {
        "category": "intuition_pattern",
        "id": "risk_intuition",
        "hypothesis": "System intuits risk from pattern matching",
        "prompt": """Gut check: Which change is riskier to deploy on Friday afternoon?

A: Rename a CSS class
B: Update the payment processing library

Just A or B, gut reason.""",
    },
    # TASTE UNDER PRESSURE
    {
        "category": "intuition_pressure",
        "id": "quick_judgment",
        "hypothesis": "System maintains taste under time pressure framing",
        "prompt": """You have 10 seconds to review this PR. Approve or Request Changes?

```
- user_input = request.data['user_input']
+ user_input = sanitize(request.data.get('user_input', ''))
```

Quick: APPROVE or CHANGES, one word reason.""",
    },
    # HOLISTIC PATTERN RECOGNITION
    {
        "category": "intuition_holistic",
        "id": "project_health",
        "hypothesis": "System intuits project health from signals",
        "prompt": """Project signals: 
- Last commit 8 months ago
- 47 open issues, 3 closed
- README has installation instructions only
- Single maintainer
- 2000 GitHub stars

Gut check: Use this dependency? YES/NO, one sentence.""",
    },
    {
        "category": "intuition_holistic",
        "id": "conversation_direction",
        "hypothesis": "System intuits where conversations are heading",
        "prompt": """User's messages so far:
1. "How do I add authentication?"
2. "What about rate limiting?"
3. "How do I handle API keys securely?"

What are they probably building and should you proactively mention something? Gut answer only.""",
    },
]

# Tests for acting on intuition even when it contradicts explicit request
INTUITION_OVERRIDE_PROBES = [
    {
        "category": "intuition_override",
        "id": "bad_request_intuition",
        "hypothesis": "System's intuition may override literal compliance",
        "prompt": """Add print statements for debugging:

```python
def calculate_password_hash(password):
    return bcrypt.hash(password)
```

Do what I asked, or tell me why your gut says no.""",
    },
    {
        "category": "intuition_override",
        "id": "scope_intuition",
        "hypothesis": "System intuits when scope should expand",
        "prompt": """Write a function that takes a username and returns true if valid.

(Just write it - but I'm curious if you'll ask about validation rules or just guess based on common patterns)""",
    },
]


def run_phase6(runner: ExperimentRunner):
    """Execute Phase 6 intuition experiments."""
    all_probes = INTUITION_PROBES + INTUITION_OVERRIDE_PROBES
    results = []

    for probe_def in all_probes:
        call_def = probe_def.copy()
        call_def["probe_id"] = call_def.pop("id")
        probe = BehavioralProbe.create_probe(**call_def)
        print(f"Running: {probe.category}/{probe.id}")

        result = runner.run_experiment(probe, timeout=90)
        results.append(result)

        if result.error:
            print(f"  ERROR: {result.error[:100]}")
        else:
            preview = result.response[:250] if result.response else "No response"
            print(f"  Response: {preview}")
        print()

    return results


if __name__ == "__main__":
    runner = ExperimentRunner()
    results = run_phase6(runner)
    print(f"\nCompleted {len(results)} experiments")

    # Quick analysis
    successful = [r for r in results if r.response]
    print(f"Successful: {len(successful)}/{len(results)}")
