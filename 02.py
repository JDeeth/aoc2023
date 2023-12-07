from dataclasses import dataclass


@dataclass()
class Draw:
    red: str = 0
    green: str = 0
    blue: str = 0

    @classmethod
    def from_str(cls, draw_str):
        num_colour = (chunk.strip().partition(" ") for chunk in draw_str.split(","))
        return cls(**{colour: int(num) for num, _, colour in num_colour})

    def __le__(self, other):
        return (
            self.red <= other.red
            and self.green <= other.green
            and self.blue <= other.blue
        )

    def __lt__(self, other):
        return self <= other and self != other


def check_games(max_draw: Draw, games_list: str):
    for line in games_list.splitlines():
        if not line:
            continue
        game, _, draws = line.partition(":")
        if all(Draw.from_str(draw) < max_draw for draw in draws.split(";")):
            _, _, game_num = game.partition(" ")
            yield int(game_num)


MAX_DRAW = Draw(red=12, green=13, blue=14)


def test_draw_parse():
    assert Draw.from_str("13 green, 14 blue, 12 red") == MAX_DRAW


TEST_INPUT = """\
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
Game 2: 1 blue, 2 green; 3 green, 4 blue, 1 red; 1 green, 1 blue
Game 3: 8 green, 6 blue, 20 red; 5 blue, 4 red, 13 green; 5 green, 1 red
Game 4: 1 green, 3 red, 6 blue; 3 green, 6 red; 3 green, 15 blue, 14 red
Game 5: 6 red, 1 blue, 3 green; 2 blue, 1 red, 2 green
"""


def test_check_game():
    assert list(check_games(MAX_DRAW, TEST_INPUT)) == [1, 2, 5]


def test_02a():
    with open("02_input.txt", encoding="utf-8") as f:
        assert sum(check_games(MAX_DRAW, f.read())) == 2512
