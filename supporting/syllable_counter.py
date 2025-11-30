def count_syllables(word):
    vowels = "aeiouy"
    word = word.lower()
    count = 0
    prev_char_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_char_was_vowel:
            count += 1
        prev_char_was_vowel = is_vowel

    if word.endswith("e"):
        count -= 1

    return max(1, count)


def count_line_syllables(line):
    words = line.split()
    return sum(count_syllables(word) for word in words)


haiku = ["Silver orb so bright", "Lights up the dark night sky", "Peaceful watch above"]

for i, line in enumerate(haiku, 1):
    syllables = count_line_syllables(line)
    print(f"Line {i}: '{line}' - {syllables} syllables")

pattern = [count_line_syllables(line) for line in haiku]
print(f"\nPattern: {pattern}")
print(f"Valid 5-7-5: {pattern == [5, 7, 5]}")
