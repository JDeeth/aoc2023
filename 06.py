from functools import reduce
from operator import mul
import pytest


def calc_distance(length, charge):
    return (length - charge) * charge


def ways_to_win(time, distance):
    return len([t for t in range(time) if calc_distance(time, t) > distance])


def score_input(text: str):
    times, distances = text.splitlines()
    times = [int(t) for t in times.split()[1:]]
    distances = [int(d) for d in distances.split()[1:]]
    results = [ways_to_win(t, d) for t, d in zip(times, distances)]
    return reduce(mul, results)


def score_pt2(text: str):
    time, distance = text.splitlines()
    time = int("".join(time.split()[1:]))
    distance = int("".join(distance.split()[1:]))
    return ways_to_win(time, distance)


@pytest.mark.parametrize(
    "charge_time,distance",
    [
        (0, 0),
        (1, 6),
        (2, 10),
        (3, 12),
        (4, 12),
        (5, 10),
        (6, 6),
        (7, 0),
    ],
)
def test_distance_calc(charge_time, distance):
    assert distance(7, charge_time) == distance


@pytest.mark.parametrize(
    "time,distance,expected", [(7, 9, 4), (15, 40, 8), (30, 200, 9)]
)
def test_ways_to_win(time, distance, expected):
    assert ways_to_win(time, distance) == expected


SAMPLE_INPUT = """\
Time:      7  15   30
Distance:  9  40  200"""


def test_sample_input():
    assert score_input(SAMPLE_INPUT) == 288


def test_sample_input_pt2():
    assert score_pt2(SAMPLE_INPUT) == 71503


PUZZLE_INPUT = """\
Time:        41     66     72     66
Distance:   244   1047   1228   1040"""


def test_06a():
    assert score_input(PUZZLE_INPUT) == 74698


def test_06b():
    assert score_pt2(PUZZLE_INPUT) == 27563421
