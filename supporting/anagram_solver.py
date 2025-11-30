import itertools


def is_valid_word(word):
    # Simple check - you could expand this with a proper dictionary
    # For now, let's just generate all permutations and manually check
    return len(word) == 10


def find_anagrams():
    letters = "PALINDROME"
    found = []

    # Generate all permutations (this will be 10! = 3,628,800 permutations)
    # Let's try a more targeted approach first

    # Check some common patterns
    common_patterns = [
        "PRIMODEAL",
        "POLARIMDEN",
        "PLAINERDOM",
        "IMPLODERAN",
        "DERMOPALIN",
        "ALIENPROMD",
    ]

    for pattern in common_patterns:
        if sorted(pattern) == sorted(letters):
            found.append(pattern)

    return found


if __name__ == "__main__":
    result = find_anagrams()
    print("Found anagrams:", result)
