import pytest


def build_sequences(history: str):
    history = [int(x) for x in history.strip().split()]
    result = [history]
    while any(result[-1]):
        prev = result[-1]
        result.append([b - a for a, b in zip(prev, prev[1:])])
    return result[:-1]


def next_value(history: str):
    sequences = build_sequences(history)
    return sum(s[-1] for s in sequences)


def prev_value(history: str):
    sequences = build_sequences(history)
    return sum(-s[0] if i % 2 else s[0] for (i, s) in enumerate(sequences))


def sum_text(text, value_fn):
    return sum(value_fn(line) for line in text.strip().splitlines())


@pytest.mark.parametrize(
    "history,value",
    [
        ("0 3 6 9 12 15", 18),
        ("1 3 6 10 15 21", 28),
        ("10 13 16 21 30 45", 68),
    ],
)
def test_predict_next(history, value):
    assert next_value(history) == value


@pytest.mark.parametrize(
    "history,value",
    [
        ("0 3 6 9 12 15", -3),
        ("1 3 6 10 15 21", 0),
        ("10 13 16 21 30 45", 5),
    ],
)
def test_extrapolate_backwards(history, value):
    assert prev_value(history) == value


def test_09a():
    with open("09_input.txt", encoding="utf-8") as f:
        assert sum_text(f.read(), next_value) == 1969958987


def test_09b():
    with open("09_input.txt", encoding="utf-8") as f:
        assert sum_text(f.read(), prev_value) == 1068
