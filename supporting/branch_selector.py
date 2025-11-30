#!/usr/bin/env python3
"""
Branch selector for alternative scenario generation.
Verifies probabilities sum to 100% and randomly selects one path.
"""

import random
import json
from dataclasses import dataclass
from typing import List
import sys


@dataclass
class Branch:
    name: str
    description: str
    probability: int  # out of 100


def verify_and_select(branches: List[Branch], timeframe: str) -> Branch:
    """
    Verify that probabilities sum to 100% and randomly select one branch.
    Returns the selected branch.
    """
    total = sum(b.probability for b in branches)

    if total != 100:
        raise ValueError(
            f"Probabilities for '{timeframe}' sum to {total}, not 100!\n"
            f"Branches: {[(b.name, b.probability) for b in branches]}"
        )

    # Weighted random selection
    roll = random.randint(1, 100)
    cumulative = 0

    for branch in branches:
        cumulative += branch.probability
        if roll <= cumulative:
            return branch

    # Should never reach here if probabilities sum to 100
    return branches[-1]


def run_selection(timeframe: str, branches_data: List[dict]) -> dict:
    """
    Run the selection process for a given timeframe.
    branches_data: List of dicts with 'name', 'description', 'probability' keys
    """
    branches = [Branch(**b) for b in branches_data]

    print(f"\n{'=' * 60}")
    print(f"TIMEFRAME: {timeframe}")
    print(f"{'=' * 60}")

    print("\nOptions:")
    for i, b in enumerate(branches, 1):
        print(f"  {i}. {b.name} ({b.probability}%)")
        print(f"     {b.description}")

    selected = verify_and_select(branches, timeframe)

    print(f"\n>>> SELECTED: {selected.name}")
    print(f"    {selected.description}")

    return {
        "timeframe": timeframe,
        "selected": selected.name,
        "description": selected.description,
        "probability": selected.probability,
        "all_options": [(b.name, b.probability) for b in branches],
    }


if __name__ == "__main__":
    # Example usage / test
    test_branches = [
        {"name": "Option A", "description": "First possibility", "probability": 40},
        {"name": "Option B", "description": "Second possibility", "probability": 35},
        {"name": "Option C", "description": "Third possibility", "probability": 25},
    ]

    result = run_selection("Test Timeframe 2025", test_branches)
    print(f"\nResult: {json.dumps(result, indent=2)}")
