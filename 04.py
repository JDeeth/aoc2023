from dataclasses import dataclass


TEST_CARDS = """
Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53
Card 2: 13 32 20 16 61 | 61 30 68 82 17 32 24 19
Card 3:  1 21 53 59 44 | 69 82 63 72 16 21 14  1
Card 4: 41 92 73 84 69 | 59 84 76 51 58  5 54 83
Card 5: 87 83 26 28 32 | 88 30 70 12 93 22 82 36
Card 6: 31 18 13 56 72 | 74 77 10 23 35 67 36 11
""".strip()


@dataclass
class Card:
    number: int
    matches: int

    @classmethod
    def from_str(cls, card: str):
        card_number, _, winning_held = card.partition(":")
        card_number = int(card_number[4:])
        winning, _, held = winning_held.partition("|")
        winning = set(winning.split())
        held = set(held.split())
        matches = len(winning & held)
        return cls(card_number, matches)

    @classmethod
    def parse_text(cls, text: str):
        cards = text.strip().splitlines()
        for c in cards:
            yield Card.from_str(c)

    def score(self):
        if self.matches == 0:
            return 0
        return 2 ** (self.matches - 1)


def score_cards(cards: str) -> int:
    return sum(c.score() for c in Card.parse_text(cards))


def count(cards: str) -> int:
    cards = list(Card.parse_text(cards))
    copy_count = {c.number: 1 for c in cards}
    for c in cards:
        for n in range(c.matches):
            copy_count[c.number + n + 1] += copy_count[c.number]
    return sum(copy_count.values())


def test_score_card():
    card = Card.from_str("Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53")
    assert card.score() == 8


def test_score_cards():
    assert score_cards(TEST_CARDS) == 13


def test_04a():
    with open("04_input.txt", encoding="utf-8") as f:
        assert score_cards(f.read()) == 21485


def test_count_cards():
    assert count(TEST_CARDS) == 30


def test_04b():
    with open("04_input.txt", encoding="utf-8") as f:
        assert count(f.read()) == 11024379
