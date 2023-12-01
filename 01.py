import pytest

DIGIT_NAMES = "zero one two three four five six seven eight nine".split()


def end_digit(line, match_on_words, reverse=False):
    if reverse:
        enumerated_line = enumerate(reversed(line))
        # need workaround when i == 0 as [:-0] == [:0] == empty
        word_match = lambda l, i, w: l[: -i if i else len(l)].endswith(w)
    else:
        enumerated_line = enumerate(line)
        word_match = lambda l, i, w: l[i:].startswith(w)

    for i, chr in enumerated_line:
        if chr.isdigit():
            return int(chr)
        if match_on_words:
            for value, word in enumerate(DIGIT_NAMES):
                if word_match(line, i, word):
                    return value
    return 0


def first_last_digit_value(line, match_on_words):
    first_digit = end_digit(line, match_on_words=match_on_words)
    last_digit = end_digit(line, match_on_words=match_on_words, reverse=True)
    return first_digit * 10 + last_digit


def total_from_file(filename, match_on_words=True):
    with open(filename, encoding="utf-8") as file:
        return sum(
            first_last_digit_value(line, match_on_words)
            for line in file.read().splitlines()
        )


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("1abc2", 12),
        ("pqr3stu8vwx", 38),
        ("a1b2c3d4e5f", 15),
        ("treb7uchet", 77),
    ],
)
def test_literal_digits(test_input, expected):
    assert first_last_digit_value(test_input, match_on_words=False) == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("two1nine", 29),
        ("eightwothree", 83),
        ("abcone2threexyz", 13),
        ("xtwone3four", 24),
        ("4nineeightseven2", 42),
        ("zoneight234", 14),
        ("7pqrstsixteen", 76),
    ],
)
def test_word_and_literal_digits(test_input, expected):
    assert first_last_digit_value(test_input, match_on_words=True) == expected


def test_1a_from_file():
    assert total_from_file("01a_test.txt", match_on_words=False) == 142


def test_1b_from_file():
    assert total_from_file("01b_test.txt") == 281


def test_1a_valid_result():
    assert total_from_file("01_input.txt", match_on_words=False) == 54877


def test_1b_valid_result():
    assert total_from_file("01_input.txt") == 54100


if __name__ == "__main__":
    print(total_from_file("01_input.txt", match_on_words=True))
