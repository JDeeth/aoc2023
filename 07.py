from collections import Counter
from dataclasses import dataclass
from enum import Enum
from random import shuffle

import pytest


@dataclass(frozen=True)
class Hand:
    class Type(Enum):
        HIGH_CARD = 1, (1, 1, 1, 1, 1)
        ONE_PAIR = 2, (2, 1, 1, 1)
        TWO_PAIR = 3, (2, 2, 1)
        THREE_OF_A_KIND = 4, (3, 1, 1)
        FULL_HOUSE = 5, (3, 2)
        FOUR_OF_A_KIND = 6, (4, 1)
        FIVE_OF_A_KIND = 7, (5,)

        def __init__(self, rank, pattern):
            self.rank = rank
            self.pattern = pattern

    htype: Type
    cards: str

    @classmethod
    def from_str(cls, cards):
        pattern = Counter(cards).values()
        pattern = tuple(sorted(pattern, reverse=True))
        htype = next(t for t in cls.Type if t.pattern == pattern)
        return cls(cards=cards, htype=htype)

    def __lt__(self, other):
        if self.htype.rank != other.htype.rank:
            return self.htype.rank < other.htype.rank
        for a, b in zip(self.cards, other.cards):
            a = self.score_card(a)
            b = other.score_card(b)
            if a == b:
                continue
            return a < b

    @staticmethod
    def score_card(text):
        scores = {
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }
        return scores.get(text) or int(text)


def play(text):
    lines = text.strip().splitlines()
    hand_bid = {}
    for line in lines:
        hand, bid = line.split()
        hand = Hand.from_str(hand)
        hand_bid[hand] = int(bid)
    ranked_bids = (bid for _hand, bid in sorted(hand_bid.items()))
    return sum(rank * bid for (rank, bid) in enumerate(ranked_bids, start=1))


@pytest.mark.parametrize(
    "text,htype",
    [
        ("AAAAA", Hand.Type.FIVE_OF_A_KIND),
        ("AA8AA", Hand.Type.FOUR_OF_A_KIND),
        ("23332", Hand.Type.FULL_HOUSE),
        ("TTT98", Hand.Type.THREE_OF_A_KIND),
        ("23432", Hand.Type.TWO_PAIR),
        ("A23A4", Hand.Type.ONE_PAIR),
        ("23456", Hand.Type.HIGH_CARD),
    ],
)
def test_categorise_hand(text, htype):
    assert Hand.from_str(text).htype == htype


@pytest.mark.parametrize(
    "text",
    [
        "AAAAA AA8AA 23332 TTT98 23432 A23A4 23456",
        "33332 2AAAA",
        "77888 77888",
    ],
)
def test_rank_hand(text):
    hands = [Hand.from_str(x) for x in text.split()]
    shuffle(hands)
    hands = sorted(hands, reverse=True)
    assert " ".join(h.cards for h in hands) == text


@pytest.mark.parametrize("text,value", [("T", 10), ("9", 9)])
def test_card_value(text, value):
    assert Hand.score_card(text) == value


def test_winnings():
    text = """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
"""
    assert play(text) == 6440


def test_07a():
    with open("07_input.txt", encoding="utf-8") as f:
        assert play(f.read()) == 251029473
