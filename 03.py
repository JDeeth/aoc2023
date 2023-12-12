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


def parse_partnum(schematic):
    for row_num, row in enumerate(schematic.splitlines()):
        next_ = ""
        for col_num, chr in enumerate(row):
            if chr.isdigit():
                next_ += chr
            elif next_:
                yield PartNum(val=int(next_), row=row_num, col=col_num - len(next_))
                next_ = ""


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
"""


def test_simple_parse_partnum():
    assert list(parse_partnum(".123.")) == [PartNum(val=123, row=0, col=1)]


def test_parse_partnum():
    assert sum(partnum.val for partnum in parse_partnum(TEST_INPUT)) == 4361 + 114 + 58


def adjacent_symbol(schematic: str, partnum: PartNum):
    def is_symbol(chr: str):
        return not chr.isalnum() and not chr.isspace() and not chr == "."

    scm_width = schematic.find("\n") + 1
    first_chr = scm_width * partnum.row + partnum.col
    return any(
        is_symbol(chr)
        for chr in (
            schematic[first_chr - 1],
            schematic[first_chr + partnum.width],
        )
    )


def partnums_adjacent_symbol(schematic):
    pass


@pytest.mark.parametrize(
    "schematic,partnum",
    [
        ("*123..\n......\n......", PartNum(123, 0, 1)),
        ("......\n*123..\n......", PartNum(123, 1, 1)),
        ("......\n.123*.\n......", PartNum(123, 1, 1)),
        ("......\n......\n*123..", PartNum(123, 2, 1)),
        ("......\n......\n.123*.", PartNum(123, 2, 1)),
        ("......\n......\n..*123", PartNum(123, 2, 3)),
    ],
)
def test_adjacent_symbol_on_row(schematic, partnum):
    assert adjacent_symbol(schematic, partnum)


@pytest.mark.parametrize(
    "schematic,partnum",
    [
        ("123...\n......\n......", PartNum(123, 0, 0)),
        ("123...\n......\n.....*", PartNum(123, 0, 0)),
        (".....*\n123...\n......", PartNum(123, 1, 0)),
        ("......\n...123\n*.....", PartNum(123, 1, 3)),
        ("......\n......\n...123", PartNum(123, 2, 3)),
    ],
)
def test_nonadjacent_symbol_on_row(schematic, partnum):
    assert not adjacent_symbol(schematic, partnum)
