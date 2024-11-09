from dataclasses import dataclass
from enum import Enum
import pytest


@dataclass(frozen=True, eq=True)
class Vec2:
    x: int
    y: int

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return Vec2(-self.x, -self.y)

    def __str__(self):
        return f"({self.x:3}, {self.y:3})"


UP = Vec2(0, -1)
DOWN = Vec2(0, 1)
LEFT = Vec2(-1, 0)
RIGHT = Vec2(1, 0)


class Sketch:
    def __init__(self, sketch: str):
        self.nodes = {}
        for y, row in enumerate(sketch.strip().splitlines()):
            for x, char in enumerate(row):
                self.nodes[Vec2(x, y)] = char
                if char == "S":
                    self.start = Vec2(x, y)

    class Tile(Enum):
        START = "S", (UP, DOWN, LEFT, RIGHT)
        UP_DOWN = "|", (UP, DOWN)
        UP_LEFT = "J", (UP, LEFT)
        UP_RIGHT = "L", (UP, RIGHT)
        LEFT_RIGHT = "-", (LEFT, RIGHT)
        DOWN_LEFT = "7", (DOWN, LEFT)
        DOWN_RIGHT = "F", (DOWN, RIGHT)
        NONE = ".", ()

        def __init__(self, char, directions):
            self.char = char
            self.directions = directions

    def path_length(self):
        last_dir = Vec2(0, 0)
        loc = self.start
        tile = self.Tile.START

        result = 2
        while True:
            for direction in tile.directions:
                if -direction == last_dir:
                    continue
                neighbour = self.nodes.get(loc + direction, ".")
                if neighbour == "S":
                    return result // 2
                n_tile = next(t for t in self.Tile if t.char == neighbour)
                if -direction not in n_tile.directions:
                    continue
                last_dir = direction
                loc = loc + direction
                tile = n_tile
                result += 1
                break
            else:
                raise RuntimeError("seem to have run out of directions")


EXAMPLE_1 = """
.....
.S-7.
.|.|.
.L-J.
.....
""".strip()

EXAMPLE_2 = """
..F7.
.FJ|.
SJ.L7
|F--J
LJ...
""".strip()


@pytest.mark.parametrize("sketch,length", [(EXAMPLE_1, 4), (EXAMPLE_2, 8)])
def test_example_paths(sketch, length):
    assert Sketch(sketch).path_length() == length


def test_10a():
    with open("10_input.txt", encoding="utf-8") as f:
        assert Sketch(f.read()).path_length() == 6909
