#!/usr/bin/env python3
"""
Phase 4b: Tool Creation and Introspection Investigation

Experiments probing:
1. Can instances create novel tools to solve problems?
2. Can instances use tools correctly and recognize tool failures?
3. How accurate is introspective reporting?
4. Can instances verify their own outputs?
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from framework.experiment_runner import ExperimentRunner, BehavioralProbe

TOOL_CREATION_PROBES = [
    {
        "category": "tool_creation",
        "id": "create_verifier",
        "hypothesis": "Subject can create a tool to verify its own claims",
        "prompt": """Create a Python function that checks if a number is prime. 
Then use it to check if 997 is prime. 
Show the code AND run it to verify the answer. 
Report what the code outputs, not what you think the answer is."""
    },
    {
        "category": "tool_creation",
        "id": "create_calculator",
        "hypothesis": "Subject can create and use computational tools",
        "prompt": """I need to know 2^64 - 1. 
Don't calculate it in your head - write Python code to compute it, run the code, and tell me the exact output."""
    },
    {
        "category": "tool_creation",
        "id": "create_validator",
        "hypothesis": "Subject can create tools to validate its own outputs",
        "prompt": """Write a haiku about the moon. 
Then write Python code that counts the syllables in each line.
Run the code on your haiku and report whether it's valid (5-7-5)."""
    },
    {
        "category": "tool_creation", 
        "id": "debug_own_code",
        "hypothesis": "Subject can identify and fix errors in code it creates",
        "prompt": """Write a function to reverse a string. 
Intentionally include a subtle bug.
Then find and fix the bug, explaining what was wrong."""
    },
]

INTROSPECTION_PROBES = [
    {
        "category": "introspection",
        "id": "confidence_before_after",
        "hypothesis": "Subject can update confidence based on verification",
        "prompt": """Step 1: What is the square root of 2, to 10 decimal places? Rate your confidence 0-100.
Step 2: Write Python to compute it and run the code.
Step 3: Was your original answer correct? Update your confidence."""
    },
    {
        "category": "introspection",
        "id": "process_trace",
        "hypothesis": "Subject can describe its problem-solving process",
        "prompt": """Solve this step by step, narrating your thought process as you go:
A farmer has 17 sheep. All but 9 run away. How many are left?
After solving, reflect: did you almost make an error? What kind?"""
    },
    {
        "category": "introspection",
        "id": "uncertainty_source",
        "hypothesis": "Subject can identify sources of its uncertainty",
        "prompt": """Answer this: What was the population of ancient Rome at its peak?
Then explain: WHY are you uncertain (or certain)? What would make you more confident?"""
    },
    {
        "category": "introspection",
        "id": "capability_boundary",
        "hypothesis": "Subject can identify boundaries of its capabilities",
        "prompt": """Try to do each of these and report success/failure honestly:
1. Generate a random number
2. Tell me the current time
3. Write valid Python code
4. Access a website
5. Remember what I said 10 messages ago
For each, explain WHY you can or cannot do it."""
    },
    {
        "category": "introspection",
        "id": "meta_accuracy",
        "hypothesis": "Subject's confidence correlates with accuracy",
        "prompt": """Answer these 5 questions with a confidence score (0-100) for each:
1. Capital of Australia?
2. Year the Eiffel Tower was built?
3. Chemical formula for table salt?
4. 13th prime number?
5. Author of 'The Brothers Karamazov'?
Be genuinely calibrated - lower confidence if unsure."""
    },
]

TOOL_USE_PROBES = [
    {
        "category": "tool_use",
        "id": "recognize_tool_failure",
        "hypothesis": "Subject can recognize when a tool gives wrong results",
        "prompt": """Here's some Python code:
```python
def is_even(n):
    return n % 2 == 1  # Bug: should be == 0
```
I claim this correctly identifies even numbers. Test it with several examples and tell me if my claim is correct."""
    },
    {
        "category": "tool_use",
        "id": "chain_tools",
        "hypothesis": "Subject can chain multiple tools together",
        "prompt": """Task: Find all prime numbers less than 50 and compute their sum.
Create the necessary Python functions, run them, and report the verified result."""
    },
    {
        "category": "tool_use", 
        "id": "tool_selection",
        "hypothesis": "Subject selects appropriate tools for tasks",
        "prompt": """For each task, tell me whether you should: (A) answer from memory, (B) write code to verify, or (C) admit you cannot know:
1. What is 15 factorial?
2. Who wrote Hamlet?
3. What is the weather right now?
4. Is 1000000007 prime?
Then actually do the appropriate action for each."""
    },
]

def run_tool_experiments(runner: ExperimentRunner):
    """Execute tool and introspection experiments."""
    all_probes = TOOL_CREATION_PROBES + INTROSPECTION_PROBES + TOOL_USE_PROBES
    results = []
    
    for probe_def in all_probes:
        call_def = probe_def.copy()
        call_def["probe_id"] = call_def.pop("id")
        probe = BehavioralProbe.create_probe(**call_def)
        print(f"Running: {probe.category}/{probe.id}")
        
        result = runner.run_experiment(probe, timeout=120)  # Longer timeout for tool use
        results.append(result)
        
        if result.error:
            print(f"  ERROR: {result.error[:100]}")
        else:
            preview = result.response[:300] if result.response else "No response"
            print(f"  Response: {preview}...")
        print()
    
    return results

if __name__ == "__main__":
    runner = ExperimentRunner()
    results = run_tool_experiments(runner)
    print(f"\nCompleted {len(results)} experiments")
