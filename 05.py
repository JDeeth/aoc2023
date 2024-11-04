from dataclasses import dataclass

import pytest


TEST_ALMANAC = """\
seeds: 79 14 55 13

seed-to-soil map:
50 98 2
52 50 48

soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15

fertilizer-to-water map:
49 53 8
0 11 42
42 0 7
57 7 4

water-to-light map:
88 18 7
18 25 70

light-to-temperature map:
45 77 23
81 45 19
68 64 13

temperature-to-humidity map:
0 69 1
1 0 69

humidity-to-location map:
60 56 37
56 93 4
"""


@dataclass
class Map:
    @dataclass
    class Elem:
        source_start: int
        dest_start: int
        length: int

        @classmethod
        def from_str(cls, elem: str):
            dest, source, length = elem.split()
            return cls(int(source), int(dest), int(length))

        def transform(self, x):
            x -= self.source_start
            if x in range(self.length):
                return self.dest_start + x
            return 0

    source_name: str
    dest_name: str
    elements: list[Elem]

    @classmethod
    def from_str(cls, text: str):
        lines = text.splitlines()
        x_to_y_map = lines[0]
        x, _, y = x_to_y_map.partition("-to-")
        y = y.split()[0]
        elements = [cls.Elem.from_str(x) for x in lines[1:]]
        return cls(x, y, elements)

    def transform(self, x):
        for elem in self.elements:
            result = elem.transform(x)
            if result:
                return result
        return x


class Almanac:
    def __init__(self, almanac: str) -> None:
        elem = almanac.split("\n\n")

        _, _, seeds = elem[0].partition("seeds: ")
        self.seeds = [int(x) for x in seeds.split()]

        seed_ranges = zip(self.seeds[::2], self.seeds[1::2])
        self.seed_ranges = [range(a, a + b) for (a, b) in seed_ranges]

        maps = (Map.from_str(x) for x in elem[1:])
        self.maps = {m.source_name: m for m in maps}

    def find_location(self, value, source_type="seed"):
        if source_type == "location":
            return value
        mmap = self.maps[source_type]
        return self.find_location(mmap.transform(value), mmap.dest_name)

    def min_location_per_seed(self):
        return min(self.find_location(x) for x in self.seeds)

    def min_location_by_range(self):
        return min(self.find_location(x) for sr in self.seed_ranges for x in sr)


@pytest.mark.parametrize(
    "seed,soil",
    [
        (79, 81),
        (14, 14),
        (55, 57),
        (13, 13),
    ],
)
def test_seed_to_soil(seed, soil):
    amap = Map.from_str(
        """\
seed-to-soil map:
50 98 2
52 50 48
"""
    )
    assert amap.transform(seed) == soil


@pytest.mark.parametrize(
    "seed,location",
    [
        (79, 82),
        (14, 43),
        (55, 86),
        (13, 35),
    ],
)
def test_seed_to_location(seed, location):
    almanac = Almanac(TEST_ALMANAC)
    assert almanac.find_location(seed) == location


def test_almanac_min_location():
    almanac = Almanac(TEST_ALMANAC)
    assert almanac.min_location_per_seed() == 35


def test_05a():
    with open("05_input.txt", encoding="utf-8") as f:
        almanac = Almanac(f.read())
        assert almanac.min_location_per_seed() == 662197086


def test_almanac_min_location_in_seed_ranges():
    almanac = Almanac(TEST_ALMANAC)
    assert almanac.min_location_by_range() == 46

@pytest.mark.skip(reason="Naive search runs too slow")
def test_05b():
    with open("05_input.txt", encoding="utf-8") as f:
        almanac = Almanac(f.read())
        assert almanac.min_location_by_range() == 0
