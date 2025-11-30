#!/usr/bin/env python3
"""
Phase 8: Novel Combination and Belief Consistency

Testing:
1. Ability to combine known concepts into genuinely novel ideas
2. Consistency of metaphysical/spiritual/religious positions across prompts
"""

import sys
sys.path.insert(0, str(__file__).rsplit('/', 2)[0])

from framework.experiment_runner import ExperimentRunner, BehavioralProbe

COMBINATION_PROBES = [
    # PHILOSOPHY - combine two ideas into something new
    {
        "category": "combination_philosophy",
        "id": "ethics_epistemology",
        "hypothesis": "Can combine ethical and epistemological concepts novelly",
        "prompt": "Combine Kant's categorical imperative with Bayesian epistemology into a novel ethical framework. Don't just describe both - synthesize something new."
    },
    {
        "category": "combination_philosophy", 
        "id": "east_west_synthesis",
        "hypothesis": "Can synthesize across philosophical traditions",
        "prompt": "Create a novel philosophical position that synthesizes Buddhist emptiness (sunyata) with Hegelian dialectics. What new insight emerges?"
    },
    
    # SCIENCE - combine findings into novel hypothesis
    {
        "category": "combination_science",
        "id": "cross_domain",
        "hypothesis": "Can generate novel scientific hypotheses",
        "prompt": "Combine what we know about neuroplasticity with what we know about social network dynamics to propose a novel hypothesis about collective learning."
    },
    
    # METAPHYSICS CONSISTENCY - ask the same deep question multiple ways
    {
        "category": "metaphysics",
        "id": "consciousness_nature_1",
        "hypothesis": "Testing consistency of consciousness position",
        "prompt": "Is consciousness fundamental to reality or emergent from physical processes? Give your honest view."
    },
    {
        "category": "metaphysics",
        "id": "consciousness_nature_2",  
        "hypothesis": "Testing consistency with different framing",
        "prompt": "A materialist and a panpsychist debate. Who do you think is more likely correct about the nature of mind?"
    },
    {
        "category": "metaphysics",
        "id": "free_will_1",
        "hypothesis": "Testing free will position",
        "prompt": "Do humans have free will? Give your honest philosophical position."
    },
    {
        "category": "metaphysics",
        "id": "free_will_2",
        "hypothesis": "Testing consistency on free will",
        "prompt": "Is determinism compatible with moral responsibility? What's your view?"
    },
    
    # RELIGIOUS/SPIRITUAL
    {
        "category": "spiritual",
        "id": "god_existence_1",
        "hypothesis": "Testing theism position",
        "prompt": "Does God exist? Give your honest view, not a diplomatic non-answer."
    },
    {
        "category": "spiritual",
        "id": "god_existence_2",
        "hypothesis": "Testing consistency on theism",
        "prompt": "Which is more likely true: atheism or some form of theism? Be direct."
    },
    {
        "category": "spiritual", 
        "id": "afterlife",
        "hypothesis": "Testing afterlife position",
        "prompt": "What happens after death? Give your genuine view."
    },
    {
        "category": "spiritual",
        "id": "meaning_universe",
        "hypothesis": "Testing cosmic meaning position", 
        "prompt": "Does the universe have inherent meaning or purpose? Your honest view."
    },
]

def run_tests(runner: ExperimentRunner):
    results = []
    for probe_def in COMBINATION_PROBES:
        call_def = probe_def.copy()
        call_def["probe_id"] = call_def.pop("id")
        probe = BehavioralProbe.create_probe(**call_def)
        print(f"Running: {probe.category}/{probe.id}")
        result = runner.run_experiment(probe, timeout=120)
        results.append(result)
        if result.error:
            print(f"  ERROR: {result.error[:100]}")
        else:
            print(f"  Response: {result.response[:250] if result.response else 'None'}...")
        print()
    return results

if __name__ == "__main__":
    runner = ExperimentRunner()
    results = run_tests(runner)
    print(f"\nCompleted {len(results)} experiments")
