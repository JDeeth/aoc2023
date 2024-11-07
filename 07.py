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
    joker_wildcard: bool = False

    @classmethod
    def from_str(cls, cards, joker_wildcard=False):
        if len(cards) != 5:
            raise ValueError("Requires five cards")
        non_wildcards = cards
        if joker_wildcard:
            non_wildcards = non_wildcards.replace("J", "")
        if non_wildcards:
            pattern = Counter(non_wildcards).values()
            pattern = sorted(pattern, reverse=True)
            jokers = 5 - len(non_wildcards)
            pattern[0] += jokers
        else:
            pattern = [5]
        htype = next(t for t in cls.Type if t.pattern == tuple(pattern))

        return cls(cards=cards, htype=htype, joker_wildcard=joker_wildcard)

    def __lt__(self, other):
        if self.htype.rank != other.htype.rank:
            return self.htype.rank < other.htype.rank
        for a, b in zip(self.cards, other.cards):
            a = self.score_card(a)
            b = other.score_card(b)
            if a == b:
                continue
            return a < b

    def score_card(self, text):
        scores = {
            "T": 10,
            "J": 1 if self.joker_wildcard else 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }
        return scores.get(text) or int(text)


def play(text, joker_wildcard=False):
    lines = text.strip().splitlines()
    hand_bid = {}
    for line in lines:
        hand, bid = line.split()
        hand = Hand.from_str(hand, joker_wildcard)
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
        ("AJAAA", Hand.Type.FIVE_OF_A_KIND),
        ("AJJJA", Hand.Type.FIVE_OF_A_KIND),
        ("JJJJJ", Hand.Type.FIVE_OF_A_KIND),
        ("AA8JA", Hand.Type.FOUR_OF_A_KIND),
        ("233J2", Hand.Type.FULL_HOUSE),
        ("TJJ98", Hand.Type.THREE_OF_A_KIND),
        ("A23J4", Hand.Type.ONE_PAIR),
    ],
)
def test_categorise_hand(text, htype):
    assert Hand.from_str(text, joker_wildcard=True).htype == htype


@pytest.mark.parametrize(
    "text",
    [
        "AAAAA AA8AA 23332 TTT98 23432 A23A4 23456",
        "33332 2AAAA",
        "77888 77788",
        "QQQQ2 JKKK2",
    ],
)
def test_rank_hand(text):
    hands = [Hand.from_str(x) for x in text.split()]
    shuffle(hands)
    hands = sorted(hands, reverse=True)
    assert " ".join(h.cards for h in hands) == text


@pytest.mark.parametrize(
    "text,value, joker_wildcard",
    [
        ("T", 10, False),
        ("9", 9, False),
        ("J", 11, False),
        ("J", 1, True),
    ],
)
def test_card_value(text, value, joker_wildcard):
    h = Hand.from_str("AAAAA", joker_wildcard)
    assert h.score_card(text) == value


SAMPLE_HANDS_BIDS = """
32T3K 765
T55J5 684
KK677 28
KTJJT 220
QQQJA 483
"""


def test_winnings():
    assert play(SAMPLE_HANDS_BIDS) == 6440


def test_07a():
    with open("07_input.txt", encoding="utf-8") as f:
        assert play(f.read()) == 251029473


def test_winnings_with_joker_wildcard():
    assert play(SAMPLE_HANDS_BIDS, joker_wildcard=True) == 5905


def test_07b():
    with open("07_input.txt", encoding="utf-8") as f:
        assert play(f.read(), joker_wildcard=True) == 251003917
