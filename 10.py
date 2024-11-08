from dataclasses import dataclass
import pytest


class Sketch:
    @dataclass(frozen=True, eq=True)
    class Vec2:
        x: int
        y: int

        def __add__(self, other):
            return Sketch.Vec2(self.x + other.x, self.y + other.y)

        def __sub__(self, other):
            return self + (-other)

        def __neg__(self):
            return Sketch.Vec2(-self.x, -self.y)

        def __str__(self):
            return f"({self.x:<3}, {self.y:<3})"

    def __init__(self, sketch: str):
        self.nodes = {}
        for y, row in enumerate(sketch.strip().splitlines()):
            for x, char in enumerate(row):
                self.nodes[self.Vec2(x, y)] = char
                if char == "S":
                    self.start = self.Vec2(x, y)

    def path_length(self):
        vec2 = Sketch.Vec2
        directions = (
            (vec2(0, 1), "|LJ"),
            (vec2(0, -1), "|7F"),
            (vec2(-1, 0), "-LF"),
            (vec2(1, 0), "-J7"),
        )
        last_dir = vec2(0, 0)
        loc = self.start
        tile = "S"
        for direction, valid_tile in directions:
            loc = self.start + direction
            tile = self.nodes.get(loc, "x")
            if tile in valid_tile:
                last_dir = direction
                break

        visited = [loc]

        result = 2
        # while True:
        for _ in range(20):
            print(tile, loc)
            for direction, valid_tile in directions:
                tile = self.nodes.get(loc + direction, ".")
                if -direction == last_dir:
                    continue
                if tile == "S":
                    return result // 2
                if tile not in valid_tile:
                    continue
                result += 1
                last_dir = direction
                loc = loc + direction
                if loc in visited:
                    print(visited)
                    raise RuntimeError("revisited location")
                visited.append(loc)
                break


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
        assert Sketch(f.read()).path_length() == 0
