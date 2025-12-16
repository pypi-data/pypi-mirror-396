from abc import ABC, abstractmethod
from concurrent.futures.process import ProcessPoolExecutor as PoolExecutor
from dataclasses import dataclass
from typing import List


class Game(ABC):
    def play_next_round(self):  # pragma: no cover
        pass


class GameSimulator(ABC):
    @abstractmethod
    def simulate(self, games: List[Game], number_of_rounds_per_game: int) -> List[Game]:  # pragma: no cover
        pass


class LocalGameSimulator(GameSimulator):
    max_concurrent_games: int

    def __init__(self, max_concurrent_games: int = 1):
        self.max_concurrent_games = max_concurrent_games
        super().__init__()

    def simulate(self, games: List[Game], number_of_rounds_per_game: int) -> List[Game]:
        print()
        print(f'Starting local game simulator for {len(games)} games...')
        print()

        with PoolExecutor(max_workers=self.max_concurrent_games) as executor:
            results = executor.map(_run_game, [
                GameRunArgs(
                    game=game,
                    game_number=index + 1,
                    number_of_rounds=number_of_rounds_per_game
                )
                for index, game in enumerate(games)
            ])
        print()
        print('Finished local game simulator')
        print()
        return list(results)


@dataclass
class GameRunArgs:
    game: Game
    game_number: int
    number_of_rounds: int


def _run_game(args: GameRunArgs) -> Game:
    print(f'Starting game #{args.game_number} simulation...')
    for _ in range(args.number_of_rounds):
        args.game.play_next_round()
    print(f'Game #{args.game_number} simulation complete.')
    return args.game
