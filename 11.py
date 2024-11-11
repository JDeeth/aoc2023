from dataclasses import dataclass

import pytest


@dataclass(frozen=True, eq=True)
class Vec2:
    x: int
    y: int


class Image:
    def __init__(self, image_text: str):
        lines = image_text.strip().splitlines()

        self.galaxies: list[Vec2] = []
        self.populated_cols = set(g.x for g in self.galaxies)
        self.populated_rows = set(g.y for g in self.galaxies)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == "#":
                    self.galaxies.append(Vec2(x, y))
                    self.populated_cols.add(x)
                    self.populated_rows.add(y)

    def distance_between_pair(self, a: Vec2, b: Vec2, empty_size: int):
        x_range = range(a.x, b.x) if a.x < b.x else range(b.x, a.x)
        y_range = range(a.y, b.y) if a.y < b.y else range(b.y, a.y)
        dx = sum(1 if x in self.populated_cols else empty_size for x in x_range)
        dy = sum(1 if y in self.populated_rows else empty_size for y in y_range)
        return dx + dy

    def total_pair_distances(self, empty_size):
        result = 0
        for i, a in enumerate(self.galaxies):
            for b in self.galaxies[i + 1 :]:
                result += self.distance_between_pair(a, b, empty_size)
        return result


SAMPLE_IMAGE = """
...#......
.......#..
#.........
..........
......#...
.#........
.........#
..........
.......#..
#...#.....
""".strip()


@pytest.fixture
def sample_image():
    return Image(SAMPLE_IMAGE)


def test_parse_image(sample_image: Image):
    assert len(sample_image.galaxies) == 9
    assert sample_image.galaxies[0] == Vec2(3, 0)
    assert sample_image.galaxies[-1] == Vec2(4, 9)


@pytest.mark.parametrize("a,b,path", [(1, 7, 15), (3, 6, 17), (8, 9, 5), (1, 8, 15)])
def test_pair_distance(sample_image: Image, a, b, path):
    a = sample_image.galaxies[a - 1]
    b = sample_image.galaxies[b - 1]
    assert sample_image.distance_between_pair(a, b, empty_size=2) == path


def test_shortest_path(sample_image: Image):
    assert sample_image.total_pair_distances(empty_size=2) == 374


def test_shortest_path_with_greater_expansion(sample_image: Image):
    assert sample_image.total_pair_distances(empty_size=100) == 8410


def test_11a():
    with open("11_input.txt", encoding="utf-8") as f:
        assert Image(f.read()).total_pair_distances(empty_size=2) == 10228230


def test_11b():
    with open("11_input.txt", encoding="utf-8") as f:
        assert (
            Image(f.read()).total_pair_distances(empty_size=1_000_000) == 447073334102
        )
