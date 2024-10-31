from dataclasses import dataclass

import pytest


@dataclass
class PartNum:
    val: int
    row: int
    col: int

    @property
    def width(self):
        return len(str(self.val))

    def adjacent(self, row_num, col_num):
        return (
            self.row == row_num and self.col in (col_num + 1, col_num - self.width)
        ) or (
            self.row in (row_num - 1, row_num + 1)
            and col_num in range(self.col - 1, self.col + self.width + 1)
        )


class Schematic:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.width = len(self.lines[0])
        self.height = len(self.lines)
        self.parts = list(self._gen_partnums())
        self.gears = list(self._locate_gears())

    def get_chr(self, x, y):
        if x not in range(0, self.width) or y not in range(0, self.height):
            return "."
        return self.lines[y][x]

    def sum_adjacent_partnums(self):
        return sum(p.val for p in self.parts if self._adjacent_symbol(p))

    def sum_dual_gears(self):
        dual_gears = [g for g in self.gears if len(g) == 2]
        return sum(a * b for (a, b) in dual_gears)

    def _gen_partnums(self):
        for row_num, row in enumerate(self.lines):
            next_ = ""
            for col_num, chr_ in enumerate(row):
                if chr_.isdigit():
                    next_ += chr_
                elif next_:
                    yield PartNum(val=int(next_), row=row_num, col=col_num - len(next_))
                    next_ = ""
            if next_:
                yield PartNum(val=int(next_), row=row_num, col=self.width - len(next_))

    def _adjacent_symbol(self, part: PartNum):
        def is_symbol(chr_: str):
            return not (chr_.isalnum() or chr_.isspace() or chr_ == ".")

        left = part.col - 1
        right = part.col + part.width
        top = part.row - 1
        bottom = part.row + 1

        for x in range(left, right + 1):
            for y in (top, bottom):
                if is_symbol(self.get_chr(x, y)):
                    return True

        for x in (left, right):
            if is_symbol(self.get_chr(x, part.row)):
                return True

        return False

    def _locate_gears(self):
        for row_num, row in enumerate(self.lines):
            for col_num, chr_ in enumerate(row):
                if chr_ == "*":
                    adjacent_parts = [
                        p.val for p in self.parts if p.adjacent(row_num, col_num)
                    ]
                    yield (adjacent_parts)


TEST_INPUT = """\
467..114..
...*......
..35..633.
......#...
617*......
.....+.58.
..592.....
......755.
...$.*....
.664.598..
""".strip()


def test_schematic_access():
    s = Schematic(TEST_INPUT)
    assert s.width == 10
    assert s.height == 10
    assert s.get_chr(3, 1) == "*"
    assert "".join(c for x in range(10) for c in s.get_chr(x, 0)) == "467..114.."
    assert "".join(c for x in range(10) for c in s.get_chr(x, 9)) == ".664.598.."


def test_simple_parse_partnum():
    assert Schematic(".123.").parts == [PartNum(val=123, row=0, col=1)]
    assert Schematic("..123").parts == [PartNum(val=123, row=0, col=2)]


def test_parse_partnum():
    sch = Schematic(TEST_INPUT)
    assert sch.parts[0] == PartNum(467, 0, 0)
    assert sch.parts[-1] == PartNum(598, 9, 5)
    assert sum(p.val for p in sch.parts) == 4361 + 114 + 58


@pytest.mark.parametrize(
    "schematic",
    [
        # same row
        ("*123..\n......\n......"),
        ("......\n*123..\n......"),
        ("......\n.123*.\n......"),
        ("......\n......\n*123.."),
        ("......\n......\n.123*."),
        ("......\n......\n..*123"),
        # vertical
        ("*.....\n123...\n......"),
        ("..*...\n123...\n......"),
        ("......\n123...\n*....."),
        ("......\n123...\n..*..."),
        # diagonal
        ("*.....\n.123..\n......"),
        ("....*.\n.123..\n......"),
        ("......\n.123..\n*....."),
        ("......\n.123..\n....*."),
    ],
)
def test_adjacent_symbol(schematic):
    assert Schematic(schematic).sum_adjacent_partnums() == 123


def test_adjacent_partnum_sums():
    assert Schematic(TEST_INPUT).sum_adjacent_partnums() == 4361


@pytest.mark.parametrize(
    "schematic",
    [
        ("......\n..123.\n......"),
        ("......\n*.123.\n......"),
        ("......\n.123.*\n......"),
        ("..123.\n......\n..*..."),
        ("..*...\n......\n..123."),
        ("*.....\n..123.\n......"),
        ("......\n..123.\n*....."),
        (".....*\n.123..\n......"),
        ("......\n.123..\n.....*"),
    ],
)
def test_nonadjacent_symbol_on_row(schematic):
    assert Schematic(schematic).sum_adjacent_partnums() == 0


@pytest.mark.parametrize(
    "text",
    [
        "*....\n.123.",
        ".*...\n.123.",
        "....*\n.123.",
        "..*123..",
        "...123*.",
        ".123.\n*....",
        ".123.\n.*...",
        ".123.\n....*",
    ],
)
def test_potential_gears(text):
    s = Schematic(text)
    assert s.gears == [[123]]


def test_find_gears():
    s = Schematic(TEST_INPUT)
    assert len(s.gears) == 3
    assert s.gears == [[467, 35], [617], [755, 598]]


def test_sum_dual_gears():
    s = Schematic(TEST_INPUT)
    assert s.sum_dual_gears() == 467835


def test_03a():
    with open("03_input.txt", encoding="utf-8") as f:
        sch = Schematic(f.read())
        assert sch.sum_adjacent_partnums() == 538046


def test_03b():
    with open("03_input.txt", encoding="utf-8") as f:
        sch = Schematic(f.read())
        assert sch.sum_dual_gears() == 81709807
