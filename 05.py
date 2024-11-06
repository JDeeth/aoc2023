from dataclasses import dataclass
from functools import reduce
from typing import Self

import pytest


@dataclass
class Map:
    @dataclass
    class Elem:
        source_range: range
        offset: int

        @property
        def dest_range(self):
            return range(
                self.source_range.start + self.offset,
                self.source_range.stop + self.offset,
            )

        @classmethod
        def from_str(cls, elem: str):
            dest, source, length = (int(x) for x in elem.split())
            return cls(range(source, source + length), dest - source)

        def contiguous_with(self, other: Self):
            return (
                self.offset == other.offset
                and self.source_range.stop == other.source_range.start
            )

        def extend_range(self, other: Self):
            self.source_range = range(self.source_range.start, other.source_range.stop)

        def transform(self, x):
            if x in self.source_range:
                return x + self.offset
            return None

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

    def __post_init__(self):
        elements = sorted(self.elements, key=lambda e: e.source_range.start)
        merged_elements = [elements[0]]
        for e in elements[1:]:
            if merged_elements[-1].contiguous_with(e):
                merged_elements[-1].extend_range(e)
            else:
                merged_elements.append(e)
        self.elements = merged_elements

    def reduce(self, other: Self):
        """
        note where first map destination ranges start
        seed        soil
        0-50    +0  0-50
        50-98   +2  52-100
        98-100  -48 50-52
                    (0, 50, 52)

        note where second map source ranges start
        soil        fertilizer
        0-15    +39 39-54
        15-54   -15 0-39
        54-100  0   54-100
        (0, 15, 54)

        split elements on both maps so the intermediate ranges match
        seed        soil        fertilizer
        0-15    +0  0-15    +39 39-54
        15-50   +0  15-50   -15 0-35
        50-52   +2  52-54   -15 37-39
        52-98   +2  54-100  0   54-100
        98-100  -48 50-52   -15 35-37
                    (0, 15, 50, 52, 54)

        combine the offsets to make a single map
        0-15    +39 39-54
        15-50   -15 0-35
        50-52   -13 37-39
        52-98   +2  54-100
        98-100  -63 35-37
        """
        assert self.dest_name == other.source_name
        breakpoints = set(e.dest_range.start for e in self.elements)
        breakpoints.update(e.dest_range.stop for e in self.elements)
        breakpoints.update(e.source_range.start for e in other.elements)
        breakpoints.update(e.source_range.stop for e in other.elements)
        breakpoints = sorted(list(breakpoints))
        elements = []
        for a, b in zip(breakpoints, breakpoints[1:]):
            offset_a = next((x.offset for x in self.elements if a in x.dest_range), 0)
            offset_b = next(
                (x.offset for x in other.elements if a in x.source_range), 0
            )
            offset = offset_a + offset_b
            elements.append(Map.Elem(range(a - offset_a, b - offset_a), offset))

        return Map(self.source_name, other.dest_name, elements)

    def transform(self, x):
        for elem in self.elements:
            result = elem.transform(x)
            if result is not None:
                return result
        return x


class Almanac:
    def __init__(self, almanac: str) -> None:
        elem = almanac.split("\n\n")

        _, _, seeds = elem[0].partition("seeds: ")
        self.seeds = [int(x) for x in seeds.split()]

        seed_ranges = zip(self.seeds[::2], self.seeds[1::2])
        self.seed_ranges = [range(a, a + b) for (a, b) in seed_ranges]

        self.map = reduce(lambda a, b: a.reduce(b), (Map.from_str(x) for x in elem[1:]))

    def min_location_per_seed(self):
        return min(self.map.transform(x) for x in self.seeds)

    def min_location_by_range(self):
        def in_range(seed):
            for seed_range in self.seed_ranges:
                if seed in seed_range:
                    return True
            return False

        loc_ranges = [e.dest_range for e in self.map.elements]
        loc_ranges = sorted(loc_ranges, key=lambda e: e.start)
        for loc_range in loc_ranges:
            print(loc_range)
            for i, location in enumerate(loc_range):
                if i % 10000 == 0:
                    print(f"{i:8}{location}")
                for e in self.map.elements:
                    if location not in e.dest_range:
                        continue
                    if in_range(location - e.offset):
                        return location


@pytest.fixture(name="map_seed_soil")
def map_1():
    return Map.from_str(
        """\
seed-to-soil map:
50 98 2
52 50 48
"""
    )


@pytest.fixture(name="map_soil_fertilizer")
def map_2():
    return Map.from_str(
        """\
soil-to-fertilizer map:
0 15 37
37 52 2
39 0 15
"""
    )


def test_merge_map_elements(map_soil_fertilizer):
    assert map_soil_fertilizer.elements == [
        Map.Elem(range(0, 15), 39),
        Map.Elem(range(15, 54), -15),
    ]


def test_reduce_maps(map_seed_soil, map_soil_fertilizer):
    new_map: Map = map_seed_soil.reduce(map_soil_fertilizer)
    assert new_map.source_name == "seed"
    assert new_map.dest_name == "fertilizer"
    assert new_map.elements == [
        Map.Elem(range(a, b), offset)
        for (a, b, offset) in (
            (0, 15, 39),
            (15, 50, -15),
            (50, 52, -13),
            (52, 98, 2),
            (98, 100, -63),
        )
    ]


@pytest.mark.parametrize(
    "seed,soil",
    [
        (79, 81),
        (14, 14),
        (55, 57),
        (13, 13),
    ],
)
def test_seed_to_soil(map_seed_soil, seed, soil):
    assert map_seed_soil.transform(seed) == soil


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


@pytest.fixture(name="test_almanac")
def almanac_fixture():
    return Almanac(TEST_ALMANAC)


@pytest.mark.parametrize(
    "seed,location",
    [
        (79, 82),
        (14, 43),
        (55, 86),
        (13, 35),
    ],
)
def test_seed_to_location(test_almanac, seed, location):
    assert test_almanac.map.transform(seed) == location


def test_almanac_min_location(test_almanac):
    assert test_almanac.min_location_per_seed() == 35


def test_05a():
    with open("05_input.txt", encoding="utf-8") as f:
        almanac = Almanac(f.read())
        assert almanac.min_location_per_seed() == 662197086


def test_almanac_min_location_in_seed_ranges(test_almanac):
    assert test_almanac.min_location_by_range() == 46


@pytest.mark.skip(reason="Takes 45 min")
def test_05b():
    with open("05_input.txt", encoding="utf-8") as f:
        print("opening almanac")
        almanac = Almanac(f.read())
        print("starting parse")
        assert almanac.min_location_by_range() == 52510809
