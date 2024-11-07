from dataclasses import dataclass
import itertools
from math import lcm

import pytest


@dataclass(frozen=True)
class Map:

    @dataclass(frozen=True)
    class Node:
        name: str
        left: str
        right: str

        def next(self, step):
            return {"L": self.left, "R": self.right}[step]

        @classmethod
        def from_str(cls, text: str):
            text = text.replace(" ", "").replace("(", "").replace(")", "")
            name, _, neighbours = text.partition("=")
            left, _, right = neighbours.partition(",")
            return cls(name, left, right)

    sequence: str
    nodes: dict[str, Node]

    @classmethod
    def from_str(cls, text):
        seq, _, nodes = text.strip().partition("\n\n")
        nodes = (cls.Node.from_str(x) for x in nodes.splitlines())
        return cls(seq, {n.name: n for n in nodes})

    def count_steps(self, start="AAA", endswith="ZZZ"):
        node = self.nodes[start]
        for i, step in enumerate(itertools.cycle(self.sequence)):
            if node.name.endswith(endswith):
                return i
            node = self.nodes[node.next(step)]

    def count_ghost_steps(self):
        # From each starting point, each path cycles
        start_nodes = {n for n in self.nodes.values() if n.name.endswith("A")}
        path_lengths = [
            self.count_steps(start=n.name, endswith="Z") for n in start_nodes
        ]
        return lcm(*path_lengths)


def test_parse_node():
    elem = Map.Node.from_str("AAA = (BBB, CCC)")
    assert elem.name == "AAA"
    assert elem.left == "BBB"
    assert elem.right == "CCC"


SAMPLE_1 = """
RL

AAA = (BBB, CCC)
BBB = (DDD, EEE)
CCC = (ZZZ, GGG)
DDD = (DDD, DDD)
EEE = (EEE, EEE)
GGG = (GGG, GGG)
ZZZ = (ZZZ, ZZZ)
""".strip()

SAMPLE_2 = """
LLR

AAA = (BBB, BBB)
BBB = (AAA, ZZZ)
ZZZ = (ZZZ, ZZZ)
""".strip()

SAMPLE_3 = """
LR

11A = (11B, XXX)
11B = (XXX, 11Z)
11Z = (11B, XXX)
22A = (22B, XXX)
22B = (22C, 22C)
22C = (22Z, 22Z)
22Z = (22B, 22B)
XXX = (XXX, XXX)
""".strip()


@pytest.mark.parametrize("text,steps", [(SAMPLE_1, 2), (SAMPLE_2, 6)])
def test_sample_step_count(text, steps):
    assert Map.from_str(text).count_steps() == steps


def test_08a():
    with open("08_input.txt", encoding="utf-8") as f:
        assert Map.from_str(f.read()).count_steps() == 17287


def test_ghost_steps():
    assert Map.from_str(SAMPLE_3).count_ghost_steps() == 6


def test_08b():
    with open("08_input.txt", encoding="utf-8") as f:
        assert Map.from_str(f.read()).count_ghost_steps() == 18625484023687
